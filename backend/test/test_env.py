from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(__file__).parent / ".env"
print(f"Loading from: {env_path}")
print(f"File exists: {env_path.exists()}")

load_dotenv(env_path)

key = os.getenv("GROQ_API_KEY")
print(f"GROQ_API_KEY loaded: {bool(key)}")
if key:
    print(f"Key starts with: {key[:15]}...")
else:
    print("ERROR: No API key found!")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Looking for .env at: {env_path.absolute()}")
