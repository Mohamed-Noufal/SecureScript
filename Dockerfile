# Production backend image for SecureScript
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install --no-cache-dir uv

# Copy Python dependencies first (for layer caching)
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Copy backend source files
COPY backend/server.py ./
COPY backend/context.py ./

# Note: mcp_servers.py is NOT copied because MCP is not used in production
# It's only in pyproject.toml for potential future use

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start the FastAPI server
# For serverless (Lambda), the Mangum handler in server.py is used instead
# For containers, this runs the standard Uvicorn server
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]