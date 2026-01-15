# 🛡️ CodeSentinel Backend

The backend for CodeSentinel, a real-time security analysis and remediation tool. Built with **FastAPI** and powered by **Groq**'s LPU inference engine for ultra-fast LLM responses.

## 🏗️ Architecture

The backend is designed for speed and reliability, acting as an intelligent orchestration layer between the frontend client and the LLM.

### Key Components

*   **FastAPI**: Asynchronous web framework for handling high-concurrency requests.
*   **Groq Integration**: Uses `AsyncOpenAI` client to interface with Groq's high-performance models (e.g., `llama3-70b`, `mixtral-8x7b`).
*   **SlowAPI**: Implements IP-based rate limiting to prevent abuse.
*   **Server-Sent Events (SSE)**: Enables real-time streaming of code fixes to the frontend, providing a "typing" effect.
*   **Pydantic**: Enforces strict data validation for all requests and responses.

## 🔌 API Endpoints

### 1. Security Analysis
*   **Endpoint**: `POST /api/analyze`
*   **Description**: Analyzes the submitted code for vulnerabilities.
*   **Auth**: Requires `X-User-Email` header.
*   **Rate Limit**: 7 requests / day / user
*   **Input**: JSON containing the source code.
*   **Output**: JSON report with a summary and list of security issues.

### 2. Auto-Fix (Streaming)
*   **Endpoint**: `POST /api/fix`
*   **Description**: Generates secure code fixes for identified issues.
*   **Auth**: Requires `X-User-Email` header.
*   **Rate Limit**: 7 requests / day / user
*   **Response**: `text/event-stream` (SSE)
*   **Events**:
    *   `start`: Analysis starting.
    *   `chunk`: Code fragment (streamed).
    *   `complete`: Final fixed code.
    *   `error`: If generation fails.

### 3. Health Check
*   **Endpoint**: `GET /health`
*   **Usage**: Kubernetes probes / uptime monitoring.

## 🤖 Mechanism of Action

1.  **Request Handshake**: Client sends code snippet.
2.  **Validation**: Backend validates payload size (<50KB) and basic syntax.
3.  **Prompt Engineering**: Context is injected via `context.SECURITY_RESEARCHER_INSTRUCTIONS`, instructing the LLM to act as a senior security researcher.
4.  **Inference (Groq)**: The prompt is sent to Groq. Due to LPU speeds, analysis is often near-instant.
5.  **Parsing**: The LLM's raw output is reliably parsed into structured JSON for the frontend.

## 🛠️ Setup & Development

### Requirements
*   Python 3.10+
*   Groq API Key

### Installation

```bash
# 1. Create venv
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt
# OR
uv sync

# 3. Configure Environment
# Create .env file
GROQ_API_KEY=your_key_here
ALLOWED_ORIGINS=http://localhost:3000
```

### Running the Server

```bash
# Using uvicorn directly
uvicorn server:app --reload --port 8000

# OR using the utility script
python server.py
```

## 🧪 Testing

The backend includes a test suite to verify endpoints and logic.

```bash
# Run all tests
pytest

# Run specific test
pytest test/test_analyze.py
```
