"""
Test script for the /api/analyze endpoint
"""
import asyncio
import httpx

async def test_analyze_endpoint():
    # Sample vulnerable Python code
    test_code = '''
import os
password = "hardcoded123"
user_input = input("Enter command: ")
os.system(user_input)
'''
    
    url = "http://localhost:8000/api/analyze"
    
    print("=" * 60)
    print("Testing /api/analyze endpoint")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Code length: {len(test_code)} characters")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                url,
                json={"code": test_code},
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Analysis successful!")
                print()
                print("Summary:")
                print(data.get("summary", "No summary"))
                print()
                print(f"Issues found: {len(data.get('issues', []))}")
                
                for i, issue in enumerate(data.get("issues", []), 1):
                    print(f"\n{i}. {issue.get('title', 'Unknown')}")
                    print(f"   Severity: {issue.get('severity', 'unknown')}")
                    print(f"   CVSS: {issue.get('cvss_score', 'N/A')}")
            else:
                print("✗ Analysis failed!")
                print("Response:")
                print(response.text)
    
    except httpx.ConnectError:
        print("✗ Connection failed!")
        print("Make sure the backend server is running:")
        print("  uv run server.py")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_analyze_endpoint())
