"""
Test script for Groq API integration
"""
import os
from pathlib import Path
from dotenv import load_dotenv
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
print("TEST 2: Direct Groq API Call (using openai library)")
print("=" * 60)
try:
    from openai import AsyncOpenAI
    
    async def test_groq_api():
        client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello in one word"}],
            max_tokens=10
        )
        return response.choices[0].message.content
    
    result = asyncio.run(test_groq_api())
    print(f"✓ Groq API call successful!")
    print(f"Response: {result}")
except Exception as e:
    print(f"✗ Groq API call failed: {e}")
print()

print("=" * 60)
print("TEST 3: Agents SDK with Groq")
print("=" * 60)
try:
    from agents import Agent, Runner
    
    async def test_agent():
        agent = Agent(
            name="Test Agent",
            instructions="You are a helpful assistant. Be concise.",
            model="llama-3.3-70b-versatile"
        )
        result = await Runner.run(agent, input="Say 'test successful' in exactly those words")
        return result.final_output
    
    result = asyncio.run(test_agent())
    print(f"✓ Agents SDK call successful!")
    print(f"Response: {result}")
except Exception as e:
    print(f"✗ Agents SDK call failed: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("TEST 4: MCP Semgrep Server")
print("=" * 60)
try:
    from mcp_servers import create_semgrep_server
    
    async def test_mcp():
        async with create_semgrep_server() as semgrep:
            print(f"✓ MCP server created successfully")
            return "MCP server working"
    
    result = asyncio.run(test_mcp())
    print(result)
except Exception as e:
    print(f"✗ MCP server test failed: {e}")
    import traceback
    traceback.print_exc()
print()

print("=" * 60)
print("Summary")
print("=" * 60)
print("Run this test to diagnose issues before testing the full analyze endpoint")
