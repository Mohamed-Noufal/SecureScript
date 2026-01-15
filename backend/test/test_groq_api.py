"""
Test script for Groq Responses API with direct integration
"""
from pathlib import Path
from dotenv import load_dotenv
import os
import asyncio

# Load environment
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Set OpenAI environment variables for Groq
if os.getenv("GROQ_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")
    os.environ["OPENAI_BASE_URL"] = "https://api.groq.com/openai/v1"

print("=" * 60)
print("TEST 1: Environment Variables")
print("=" * 60)
print(f"GROQ_API_KEY: {'✓ Set' if os.getenv('GROQ_API_KEY') else '✗ NOT SET'}")
print(f"OPENAI_API_KEY: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ NOT SET'}")
print(f"OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
print()

print("=" * 60)
print("TEST 2: Direct Groq API Call (Chat Completions)")
print("=" * 60)
try:
    from openai import AsyncOpenAI
    
    async def test_groq_chat():
        client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "Say 'test successful' in exactly those words"}],
            max_tokens=10
        )
        return response.choices[0].message.content
    
    result = asyncio.run(test_groq_chat())
    print(f"✓ Groq chat API call successful!")
    print(f"Response: {result}")
except Exception as e:
    print(f"✗ Groq chat API call failed: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("TEST 3: Security Analysis with JSON Output")
print("=" * 60)
try:
    async def test_analysis():
        client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        test_code = """
import os
password = "hardcoded123"
user_input = input("Enter command: ")
os.system(user_input)
"""
        
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": """You are a security analyst. Analyze the code and return ONLY a JSON object with this structure:
{
  "summary": "Brief summary of security issues found",
  "issues": [
    {
      "title": "Issue name",
      "description": "Description",
      "code": "Vulnerable code",
      "fix": "How to fix",
      "cvss_score": 7.5,
      "severity": "high"
    }
  ]
}"""
                },
                {
                    "role": "user",
                    "content": f"Analyze this Python code for security issues:\n\n{test_code}"
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    result = asyncio.run(test_analysis())
    print(f"✓ Security analysis successful!")
    print(f"Response length: {len(result)} characters")
    print(f"First 200 chars: {result[:200]}...")
    
    # Try to parse JSON
    import json
    import re
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = None
    
    if json_str:
        data = json.loads(json_str)
        print(f"✓ JSON parsing successful!")
        print(f"Summary: {data.get('summary', 'N/A')}")
        print(f"Issues found: {len(data.get('issues', []))}")
    else:
        print(f"✗ Could not find JSON in response")
        
except Exception as e:
    print(f"✗ Security analysis failed: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("Summary")
print("=" * 60)
print("All components tested. Ready for end-to-end testing via /api/analyze")
