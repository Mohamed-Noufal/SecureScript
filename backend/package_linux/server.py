"""
SecureScript API Server

A FastAPI-based security analysis service that uses AI to detect and fix
vulnerabilities in Python code. Features JWT authentication, rate limiting,
and streaming code fixes.
"""

import os
import logging
import json
from pathlib import Path
from functools import lru_cache
import fastapi
from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from openai import AsyncOpenAI
import jwt
import httpx

from context import SECURITY_RESEARCHER_INSTRUCTIONS, get_analysis_prompt

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

print(f"Loading .env from: {env_path}")
print(f"GROQ_API_KEY loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_email(request: Request) -> str:
    """Extract user email from request headers for rate limiting.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User email from X-User-Email header, or client IP as fallback
    """
    return request.headers.get("X-User-Email") or get_remote_address(request)


limiter = Limiter(key_func=get_user_email)

app = FastAPI(title="SecureScript API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def verify_authenticated_user(request: Request) -> str:
    """Verify Clerk JWT token and extract user identity.
    
    Validates the JWT signature using Clerk's JWKS endpoint to ensure
    the token was issued by Clerk and hasn't been tampered with.
    
    Args:
        request: FastAPI request object containing Authorization header
        
    Returns:
        User email extracted from verified JWT claims
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in."
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        clerk_frontend_api = os.getenv("CLERK_FRONTEND_API", "")
        if not clerk_frontend_api:
            logger.warning("CLERK_FRONTEND_API not set, using permissive mode for development")
            if os.getenv("REQUIRE_JWT_VERIFICATION", "true").lower() == "true":
                raise HTTPException(status_code=500, detail="Server misconfiguration: CLERK_FRONTEND_API not set")
        
        jwks_url = f"https://{clerk_frontend_api}/.well-known/jwks.json" if clerk_frontend_api else None
        
        if jwks_url:
            async with httpx.AsyncClient() as client:
                jwks_response = await client.get(jwks_url)
                jwks = jwks_response.json()
            
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            signing_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not signing_key:
                raise HTTPException(status_code=401, detail="Unable to find signing key")
            
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
        else:
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.warning("JWT signature verification SKIPPED - development mode only!")
        
        user_email = payload.get("email") or payload.get("primary_email_address") or payload.get("sub")
        
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token: no user identifier")
        
        return user_email
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please sign in again.")
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    except Exception as e:
        logger.exception(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed.")


cors_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    """Request model for code analysis endpoint."""
    code: str = Field(description="Python code to analyze for security vulnerabilities")


class SecurityIssue(BaseModel):
    """Model representing a single security vulnerability."""
    title: str
    description: str
    code: str
    fix: str
    cvss_score: float
    severity: str


class SecurityReport(BaseModel):
    """Model for complete security analysis report."""
    summary: str
    issues: List[SecurityIssue]


class FixRequest(BaseModel):
    """Request model for code fix endpoint."""
    code: str = Field(description="Original vulnerable code")
    issues: List[SecurityIssue] = Field(description="List of issues to fix")


def validate_request(request: AnalyzeRequest) -> None:
    """Validate analysis request parameters.
    
    Args:
        request: AnalyzeRequest object to validate
        
    Raises:
        HTTPException: If code is empty, too large, or has syntax errors
    """
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    if len(request.code) > 50000:
        raise HTTPException(status_code=400, detail="Code is too large. Maximum size is 50KB")
    
    try:
        compile(request.code, '<string>', 'exec')
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Python syntax: {str(e)}")


def check_api_keys() -> None:
    """Verify required API keys are configured.
    
    Raises:
        HTTPException: If GROQ_API_KEY is not set
    """
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify client API key if required.
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        True if verification passes
        
    Raises:
        HTTPException: If API key is required but missing or invalid
    """
    if os.getenv("REQUIRE_API_KEY", "false").lower() == "true":
        valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
        if not x_api_key or x_api_key not in valid_keys:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "Bearer"}
            )
    return True


async def run_security_analysis_with_mcp(code: str) -> SecurityReport:
    """Execute security analysis using Groq LLM.
    
    Analyzes Python code for security vulnerabilities using Llama 3.3 70B
    with structured JSON output.
    
    Args:
        code: Python code to analyze
        
    Returns:
        SecurityReport containing analysis summary and detected issues
        
    Raises:
        Exception: If analysis fails or response cannot be parsed
    """
    client = AsyncOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": SECURITY_RESEARCHER_INSTRUCTIONS
                },
               {
                    "role": "user",
                    "content": get_analysis_prompt(code)
                }
            ],
            temperature=0.1,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        output_text = response.choices[0].message.content
        logger.info(f"Received response: {len(output_text)} characters")
        
        try:
            data = json.loads(output_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', output_text)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{[\s\S]*\}', output_text)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    return SecurityReport(
                        summary="Failed to parse analysis results. Raw output: " + output_text[:200],
                        issues=[]
                    )
            data = json.loads(json_str)
            
        return SecurityReport(**data)
        
    except Exception as e:
        logger.exception(f"Analysis failed: {e}")
        raise


@app.post("/api/analyze", response_model=SecurityReport)
@limiter.limit("7/day")
async def analyze_code(
    request: Request,
    analyze_request: AnalyzeRequest,
    x_api_key: Optional[str] = Header(None),
    user_email: str = fastapi.Depends(verify_authenticated_user)
) -> SecurityReport:
    """Analyze Python code for security vulnerabilities.
    
    Rate limit: 7 requests per day per user
    
    Args:
        request: FastAPI request object
        analyze_request: Code analysis request
        x_api_key: Optional API key header
        user_email: Authenticated user email from JWT
        
    Returns:
        SecurityReport with detected vulnerabilities
        
    Raises:
        HTTPException: If validation fails or analysis errors occur
    """
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Analysis request ({len(analyze_request.code)} chars)")
    
    try:
        verify_api_key(x_api_key)
        validate_request(analyze_request)
        logger.info(f"[{request_id}] Validation passed")
        
        check_api_keys()
        
        logger.info(f"[{request_id}] Starting analysis...")
        report = await run_security_analysis_with_mcp(analyze_request.code)
        logger.info(f"[{request_id}] Complete. Found {len(report.issues)} issues")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{request_id}] Failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed. Contact support with ID: {request_id}"
        )


@app.post("/api/fix")
@limiter.limit("7/day")
async def fix_security_issues(
    request: Request,
    fix_request: FixRequest,
    x_api_key: Optional[str] = Header(None),
    user_email: str = fastapi.Depends(verify_authenticated_user)
):
    """Fix security issues with real-time streaming.
    
    Returns Server-Sent Events (SSE) stream with fixed code.
    Rate limit: 7 requests per day per user
    
    Args:
        request: FastAPI request object
        fix_request: Code fix request with issues to address
        x_api_key: Optional API key header
        user_email: Authenticated user email from JWT
        
    Returns:
        StreamingResponse with SSE events
    """
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Fix request for {len(fix_request.issues)} issues")
    
    verify_api_key(x_api_key)
    
    async def generate_fix_stream():
        """Generate SSE stream for code fixes."""
        try:
            client = AsyncOpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            
            issues_text = "\n".join([
                f"{i+1}. {issue.title}: {issue.description}"
                for i, issue in enumerate(fix_request.issues)
            ])
            
            prompt = f"""Fix the following security issues in this Python code:

ISSUES TO FIX:
{issues_text}

ORIGINAL CODE:
{fix_request.code}

Return ONLY the fixed code with all security issues resolved. Maintain the original code structure and comments."""
            
            yield f"event: start\ndata: {{\"status\": \"Starting fixes...\"}}\n\n"
            
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,
                stream=True
            )
            
            fixed_code = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    fixed_code += content
                    import json
                    yield f"event: chunk\ndata: {json.dumps({'chunk': content})}\n\n"
            
            yield f"event: complete\ndata: {json.dumps({'fixed_code': fixed_code})}\n\n"
            logger.info(f"[{request_id}] Fix complete")
            
        except Exception as e:
            logger.exception(f"[{request_id}] Fix failed: {e}")
            yield f"event: error\ndata: {{\"error\": \"Fix failed\"}}\n\n"
    
    return StreamingResponse(
        generate_fix_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/health")
async def health():
    """Health check endpoint.
    
    Returns:
        Dict with service status
    """
    return {"status": "ok", "service": "Cybersecurity Analyzer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# AWS Lambda Handler
from mangum import Mangum
handler = Mangum(app, lifespan="off")
