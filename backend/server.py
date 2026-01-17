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

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Verify API key is loaded
print(f"Loading .env from: {env_path}")
print(f"GROQ_API_KEY loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
def get_user_email(request: Request) -> str:
    """
    Rate limit key function: Use X-User-Email header.
    Fall back to IP if missing (though verify_authenticated_user will block missing headers).
    """
    return request.headers.get("X-User-Email") or get_remote_address(request)

limiter = Limiter(key_func=get_user_email)

app = FastAPI(title="SecureScript API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

async def verify_authenticated_user(request: Request):
    """
    Verify Clerk JWT token from Authorization header.
    Fetches Clerk's JWKS to validate the token signature.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in."
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Get Clerk Frontend API URL from environment
        clerk_frontend_api = os.getenv("CLERK_FRONTEND_API", "")
        if not clerk_frontend_api:
            # Fallback: extract from NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY format
            # For production, set CLERK_FRONTEND_API explicitly
            logger.warning("CLERK_FRONTEND_API not set, using permissive mode for development")
            # In development, we can still verify structure but skip signature
            # For production, this MUST be set
            if os.getenv("REQUIRE_JWT_VERIFICATION", "true").lower() == "true":
                raise HTTPException(status_code=500, detail="Server misconfiguration: CLERK_FRONTEND_API not set")
        
        # Fetch JWKS from Clerk
        jwks_url = f"https://{clerk_frontend_api}/.well-known/jwks.json" if clerk_frontend_api else None
        
        if jwks_url:
            async with httpx.AsyncClient() as client:
                jwks_response = await client.get(jwks_url)
                jwks = jwks_response.json()
            
            # Get the signing key
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            signing_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    signing_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
                    break
            
            if not signing_key:
                raise HTTPException(status_code=401, detail="Unable to find signing key")
            
            # Verify and decode the token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                options={"verify_aud": False}  # Clerk tokens don't always have aud
            )
        else:
            # Development fallback: decode without verification (NOT FOR PRODUCTION)
            payload = jwt.decode(token, options={"verify_signature": False})
            logger.warning("JWT signature verification SKIPPED - development mode only!")
        
        # Extract user email from claims
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

# Configure CORS - use env var for production
cors_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Data Models
class AnalyzeRequest(BaseModel):
    code: str = Field(description="Python code to analyze for security vulnerabilities")


class SecurityIssue(BaseModel):
    title: str
    description: str
    code: str
    fix: str
    cvss_score: float
    severity: str


class SecurityReport(BaseModel):
    summary: str
    issues: List[SecurityIssue]


class FixRequest(BaseModel):
    code: str = Field(description="Original vulnerable code")
    issues: List[SecurityIssue] = Field(description="List of issues to fix")


# Validation
def validate_request(request: AnalyzeRequest) -> None:
    """Validate the analysis request."""
    if not request.code or not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")
    
    if len(request.code) > 50000:  # 50KB limit
        raise HTTPException(status_code=400, detail="Code is too large. Maximum size is 50KB")
    
    # Basic Python syntax check
    try:
        compile(request.code, '<string>', 'exec')
    except SyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Python syntax: {str(e)}")


def check_api_keys() -> None:
    """Verify required API keys are configured."""
    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="Service temporarily unavailable")


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """Verify the client API key (optional for development)."""
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
    """
    Execute security analysis using Groq Responses API with Remote MCP.
    
    This uses Groq's official Responses API which handles tool discovery
    and orchestration server-side.
    """
    client = AsyncOpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )
    
    try:
        # Use Groq Responses API with Remote MCP
        # NOTE: This requires an MCP server exposed via HTTP
        # For local Semgrep, we'd need to expose it as HTTP server first
        # For now, we'll use direct chat completions (MCP setup needed separately)
        
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
        
        # Parse response
        output_text = response.choices[0].message.content
        logger.info(f"Received response: {len(output_text)} characters")
        
        # Extract JSON
        try:
            # First try direct parsing (since json_object mode usually returns raw JSON)
            data = json.loads(output_text)
        except json.JSONDecodeError:
            # Fallback for markdown blocks if model ignores mode
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
    """
    Analyze Python code for security vulnerabilities.
    
    Rate limit: 7 requests per day per User (Email)
    """
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Analysis request ({len(analyze_request.code)} chars)")
    
    try:
        # Verify API key
        verify_api_key(x_api_key)
        
        # Validate request
        validate_request(analyze_request)
        logger.info(f"[{request_id}] Validation passed")
        
        # Check internal API keys
        check_api_keys()
        
        # Run analysis
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
    """
    Fix security issues with real-time streaming.
    Returns Server-Sent Events (SSE) stream.
    
    Rate limit: 7 requests per day per User (Email)
    """
    import uuid
    
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Fix request for {len(fix_request.issues)} issues")
    
    # Verify API key
    verify_api_key(x_api_key)
    
    async def generate_fix_stream():
        try:
            client = AsyncOpenAI(
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            
            # Create fix prompt
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
            
            # Send start event
            yield f"event: start\ndata: {{\"status\": \"Starting fixes...\"}}\n\n"
            
            # Stream from Groq
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
                    # Send code chunk
                    import json
                    yield f"event: chunk\ndata: {json.dumps({'chunk': content})}\n\n"
            
            # Send completion
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
    """Health check endpoint."""
    return {"status": "ok", "service": "Cybersecurity Analyzer"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
