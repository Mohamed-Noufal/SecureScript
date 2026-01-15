# 🛡️ SecureScript (Code Safety Analyzer)

**SecureScript** is an advanced, AI-powered security analysis tool designed to identify and automatically remediate vulnerabilities in Python code. Built for speed and accuracy, it leverages **Groq's LPU™ Inference Engine** (Llama 3.3) to provide near-instant security audits and fixes.

![CodeSentinel Preview](assets/codesentinel-preview.png)

## 🚀 Key Features

*   **🛡️ Deep Security Analysis**: Detects OWASP Top 10 vulnerabilities (SQLi, XSS, Deserialization, Hardcoded Secrets) using semantic understanding, not just regex.
*   **⚡ Streaming Auto-Fix**: Instantly generates secure patches for identified issues.
*   **🔐 Strict Access Control**: Mandatory authentication via Clerk prevents unauthorized usage.
*   **🚦 Intelligent Rate Limiting**: Enforces a strict quota of **7 requests per user per day** to prevent abuse and manage LLM costs.
*   **🎨 Premium UI**: A modern, dark-mode/light-mode compatible interface built with Next.js and Shadcn UI.

## 🛠️ Technology Stack

### Frontend
- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/) & [Shadcn UI](https://ui.shadcn.com/)
- **Auth**: [Clerk](https://clerk.com/)
- **State**: React Hooks (Strict Mode)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI Engine**: [Groq](https://groq.com/) (Llama 3.3 70B Versatile)
- **Rate Limiting**: [SlowAPI](https://github.com/laurentS/slowapi) (In-memory, email-based)
- **Validation**: Pydantic

## 🏁 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- **Groq API Key**: Get one at [console.groq.com](https://console.groq.com)
- **Clerk Keys**: Create an application at [dashboard.clerk.com](https://dashboard.clerk.com)

### 1. Backend Setup

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Install dependencies (using uv for speed)
uv sync
# OR
pip install -r requirements.txt

# Configure Environment
# Create .env file with:
GROQ_API_KEY=gsk_your_key_here
ALLOWED_ORIGINS=http://localhost:3000

# Start Server
uv run server.py
# Server runs at http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure Environment
# Create .env.local file with:
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000

# Start App
npm run dev
# App runs at http://localhost:3000
```

## 🧪 Usage Guide

1.  **Sign In**: You must log in via Clerk to access the workspace.
2.  **Upload Code**: Paste your Python code or click "Open" to upload a `.py` file.
3.  **Run Analysis**:
    *   Click the **Run Analysis** button.
    *   The backend scans your code for vulnerabilities.
4.  **Fix Issues**:
    *   Review the cards on the right.
    *   Click **Fix All Issues** (Blue button) to stream a complete rewrite of your code with fixes applied.
    *   *Note*: You are limited to 7 analyses/fixes per day.

## 🛡️ Security

*   **Secrets**: All API keys are stored in `.env` files (git-ignored).
*   **Auth**: Requests to the backend require a valid `X-User-Email` header, verified against the session.
*   **XSS Protection**: React automatically escapes content rendering.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.