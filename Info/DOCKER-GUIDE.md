# 🐳 Complete Docker Guide for SecureScript

This guide explains **every line** of your Dockerfile and shows you how to run your security analyzer app in Docker.

---

## 📋 Your Dockerfile (Line-by-Line Explanation)

```dockerfile
# Production backend image for SecureScript
FROM python:3.12-slim
```
**What it does:** Uses Python 3.12 as the base image. `slim` variant is ~150MB smaller than the full image.

---

```dockerfile
WORKDIR /app
```
**What it does:** Sets `/app` as the working directory. All subsequent commands run from here.

---

```dockerfile
# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
```
**What it does:**
- `apt-get update`: Updates package lists
- `apt-get install -y curl`: Installs curl (needed for health checks)
- `rm -rf /var/lib/apt/lists/*`: Cleans up package lists to reduce image size (~10MB saved)

---

```dockerfile
# Install uv for Python package management
RUN pip install --no-cache-dir uv
```
**What it does:**
- Installs `uv` (fast Python package manager)
- `--no-cache-dir`: Doesn't cache pip downloads (saves ~50MB)

---

```dockerfile
# Copy Python dependencies first (for layer caching)
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev
```
**What it does:**
- Copies only dependency files first
- `uv sync --frozen`: Installs exact versions from lock file
- `--no-dev`: Skips development dependencies (pytest, etc.)

**Why copy separately?** Docker layer caching! If your code changes but dependencies don't, Docker reuses this layer (builds in seconds instead of minutes).

---

```dockerfile
# Copy backend source files
COPY backend/server.py ./
COPY backend/context.py ./
```
**What it does:** Copies only the 2 Python files your app actually uses.

**Why not `COPY backend/ ./`?** That would copy unnecessary files (`.venv`, `__pycache__`, `test/`, `mcp_servers.py`), making the image larger and slower to build.

---

```dockerfile
# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```
**What it does:**
- Checks if your app is healthy every 30 seconds
- Calls `http://localhost:8000/health` endpoint
- `--start-period=60s`: Gives app 60 seconds to start before checking
- `--retries=3`: Marks unhealthy after 3 failed checks
- Used by Docker, AWS ECS, and Kubernetes to know if container is working

---

```dockerfile
EXPOSE 8000
```
**What it does:** Documents that the container listens on port 8000 (doesn't actually open the port, just documentation).

---

```dockerfile
# Start the FastAPI server
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```
**What it does:**
- `uv run`: Runs command in the uv environment
- `uvicorn server:app`: Starts FastAPI app from `server.py`
- `--host 0.0.0.0`: Listens on all network interfaces (required for Docker)
- `--port 8000`: Runs on port 8000

**Note:** For serverless (Lambda), the Mangum handler in `server.py` is used instead of this command.

---

## 🚀 How to Run Your App in Docker

### Step 1: Build the Docker Image

```bash
# From the project root (cyber/)
docker build -t securescript-backend -f Dockerfile .
```

**What this does:**
- `-t securescript-backend`: Tags the image with a name
- `-f Dockerfile`: Specifies which Dockerfile to use
- `.`: Build context (current directory)

**Expected output:**
```
[+] Building 35.2s (11/11) FINISHED
 => [1/6] FROM python:3.12-slim
 => [2/6] WORKDIR /app
 => [3/6] RUN apt-get update && apt-get install -y curl
 => [4/6] RUN pip install --no-cache-dir uv
 => [5/6] COPY backend/pyproject.toml backend/uv.lock ./
 => [6/6] RUN uv sync --frozen --no-dev
 => [7/6] COPY backend/server.py ./
 => [8/6] COPY backend/context.py ./
 => exporting to image
Successfully tagged securescript-backend:latest
```

---

### Step 2: Run the Container

```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_groq_key_here \
  -e CLERK_FRONTEND_API=your-app.clerk.accounts.dev \
  -e REQUIRE_JWT_VERIFICATION=false \
  -e ALLOWED_ORIGINS=http://localhost:3000 \
  --name securescript-api \
  securescript-backend
```

**What each flag does:**
- `-p 8000:8000`: Maps port 8000 on your machine to port 8000 in container
- `-e`: Sets environment variables
- `--name`: Names the container for easy reference
- `securescript-backend`: The image to run

**Or use your .env file:**
```bash
docker run -p 8000:8000 --env-file backend/.env --name securescript-api securescript-backend
```

**Expected output:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 3: Test the API

```bash
# In another terminal
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status": "ok", "service": "Cybersecurity Analyzer"}
```

**Test code analysis:**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{"code": "import os\npassword = \"hardcoded123\""}'
```

---

## 🔧 Docker Commands Cheat Sheet

### Build Commands
```bash
# Build image
docker build -t securescript-backend -f Dockerfile .

# Build with no cache (fresh build)
docker build --no-cache -t securescript-backend -f Dockerfile .

# View build history
docker history securescript-backend
```

### Run Commands
```bash
# Run in foreground (see logs)
docker run -p 8000:8000 securescript-backend

# Run in background (detached)
docker run -d -p 8000:8000 --name securescript-api securescript-backend

# Run with environment file
docker run -p 8000:8000 --env-file backend/.env securescript-backend

# Run with custom port
docker run -p 8001:8000 securescript-backend
```

### Manage Containers
```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Stop container
docker stop securescript-api

# Start stopped container
docker start securescript-api

# Restart container
docker restart securescript-api

# View logs
docker logs securescript-api

# Follow logs (live)
docker logs -f securescript-api

# Execute command in running container
docker exec -it securescript-api bash

# View container stats (CPU, memory)
docker stats securescript-api
```

### Clean Up
```bash
# Remove container
docker rm securescript-api

# Force remove running container
docker rm -f securescript-api

# Remove image
docker rmi securescript-backend

# Remove all stopped containers
docker container prune

# Remove all unused images
docker image prune -a

# Remove everything (containers, images, networks)
docker system prune -a
```

---

## 📊 Docker Image Layers

When you build, Docker creates layers:

```
Layer 1: python:3.12-slim (base)           [180 MB]
Layer 2: WORKDIR /app                      [0 MB]
Layer 3: Install curl                      [5 MB]
Layer 4: Install uv                        [8 MB]
Layer 5: Copy pyproject.toml + uv.lock     [1 KB]
Layer 6: Install dependencies              [45 MB]
Layer 7: Copy server.py                    [15 KB]
Layer 8: Copy context.py                   [1 KB]
────────────────────────────────────────────────────
Total: ~238 MB
```

**Why layers matter:**
- If only Layer 7 or 8 changes (your code), Docker reuses Layers 1-6
- Rebuilds take ~5 seconds instead of ~35 seconds!

---

## 🐛 Troubleshooting

### "Cannot connect to Docker daemon"
```bash
# Windows/Mac: Start Docker Desktop
# Linux: Start Docker service
sudo systemctl start docker
```

### "Port 8000 already in use"
```bash
# Windows: Find what's using the port
netstat -ano | findstr :8000

# Mac/Linux: Find what's using the port
lsof -i :8000

# Use a different port
docker run -p 8001:8000 securescript-backend
```

### "Image build fails"
```bash
# Check Docker has enough space
docker system df

# Clean up
docker system prune -a

# Check Docker version
docker --version
```

### "Container exits immediately"
```bash
# View logs to see error
docker logs securescript-api

# Common issue: Missing environment variables
# Solution: Use --env-file or -e flags
```

---

## 🎯 Production Best Practices

### 1. Use Multi-Stage Builds (Optional)
For even smaller images:
```dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY backend/server.py backend/context.py ./
CMD [".venv/bin/uvicorn", "server:app", "--host", "0.0.0.0"]
```

### 2. Use .dockerignore
Already configured in your project to exclude:
- `.git`, `.venv`, `__pycache__`
- `node_modules`, `.next`
- Test files, documentation

### 3. Security Scanning
```bash
# Scan for vulnerabilities
docker scan securescript-backend
```

---

## ✅ Summary

Your Dockerfile is **production-ready** and:
- ✅ Uses Python 3.12 (latest stable)
- ✅ Optimized for layer caching (fast rebuilds)
- ✅ Only includes necessary files (small image)
- ✅ Includes health checks (for orchestration)
- ✅ Runs FastAPI with Uvicorn
- ✅ Total size: ~238 MB

**To run your app in Docker:**
```bash
# Build
docker build -t securescript-backend -f Dockerfile .

# Run
docker run -p 8000:8000 --env-file backend/.env securescript-backend

# Test
curl http://localhost:8000/health
```

Your app is now fully Dockerized and ready for deployment! 🐳🚀
