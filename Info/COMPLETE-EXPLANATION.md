# 📚 Complete Deployment Explanation

This guide explains **every file** in your deployment setup, line by line, so you understand exactly what's happening.

---

## 🗂️ Part 1: Terraform Files (Infrastructure as Code)

Terraform lets you define AWS resources using code instead of clicking in the AWS Console.

### `terraform/aws/main.tf`

This is the main configuration file that creates all your AWS resources.

#### Section 1: Provider Setup
```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```
**What it does:** Tells Terraform "I want to use AWS" and which region (like `us-east-1`).

---

#### Section 2: Frontend - S3 Bucket
```hcl
resource "aws_s3_bucket" "frontend" {
  bucket = "securescript-frontend-${var.stage}"
}
```
**What it does:** Creates a storage bucket (like a folder in the cloud) to hold your React/Next.js files.

**Why S3?** It's cheap and perfect for static files (HTML, CSS, JS).

---

#### Section 3: Frontend - CloudFront (CDN)
```hcl
resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "S3-Frontend"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }
  # ... more config
}
```
**What it does:** Creates a CDN (Content Delivery Network) that copies your website to servers worldwide.

**Why CloudFront?** Makes your site load fast for users in Japan, Brazil, or anywhere else.

---

#### Section 4: Backend - Lambda Function
```hcl
resource "aws_lambda_function" "api" {
  function_name = "securescript-api-${var.stage}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "server.handler"
  runtime       = "python3.12"
  
  environment {
    variables = {
      GROQ_API_KEY = var.groq_api_key
      # ... other env vars
    }
  }
}
```
**What it does:** Creates a Lambda function (serverless compute) to run your FastAPI code.

**Key parts:**
- `handler = "server.handler"`: Points to the `handler` function in `server.py` (the Mangum wrapper).
- `runtime = "python3.12"`: Tells AWS to use Python 3.12.
- `environment.variables`: Your API keys and config.

---

#### Section 5: Backend - API Gateway
```hcl
resource "aws_apigatewayv2_api" "lambda_api" {
  name          = "securescript-gw-${var.stage}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.lambda_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}
```
**What it does:** Creates a public URL (like `https://abc123.execute-api.us-east-1.amazonaws.com`) that triggers your Lambda.

**Key parts:**
- `route_key = "ANY /{proxy+}"`: Means "send ALL requests to Lambda" (GET, POST, etc.).

---

### `terraform/aws/variables.tf`

```hcl
variable "groq_api_key" {
  description = "API Key for Groq"
  type        = string
  sensitive   = true
}
```
**What it does:** Defines input variables. You provide these when running `terraform apply`.

**Why?** Keeps secrets out of the code. You pass them at runtime.

---

### `terraform/aws/outputs.tf`

```hcl
output "api_gateway_url" {
  value = aws_apigatewayv2_api.lambda_api.api_endpoint
}
```
**What it does:** After Terraform creates everything, it prints useful info (like your API URL).

---

## 🤖 Part 2: GitHub Actions (CI/CD)

GitHub Actions are automation scripts that run when you push code.

### `.github/workflows/deploy-backend.yml`

```yaml
on:
  push:
    branches: [ "main" ]
    paths:
      - 'backend/**'
```
**What it does:** "Run this workflow when code in `backend/` is pushed to `main`."

---

```yaml
- name: Install dependencies
  run: |
    cd backend
    pip install uv
    uv pip install -r pyproject.toml --target .
```
**What it does:** Installs all your Python libraries (FastAPI, Mangum, etc.) into the `backend/` folder.

**Why `--target .`?** Lambda needs all dependencies in the same folder as your code.

---

```yaml
- name: Zip backend
  run: |
    cd backend
    zip -r ../backend.zip .
```
**What it does:** Creates a ZIP file with your code + libraries.

**Why ZIP?** Lambda accepts code as a ZIP file.

---

```yaml
- name: Deploy to Lambda
  run: |
    aws lambda update-function-code --function-name securescript-api-prod --zip-file fileb://backend.zip
```
**What it does:** Uploads the ZIP to your Lambda function.

---

### `.github/workflows/deploy-frontend.yml`

```yaml
- name: Build Next.js
  run: |
    cd frontend
    npm run build
```
**What it does:** Builds your React/Next.js app into static files (HTML/CSS/JS).

---

```yaml
- name: Deploy to S3
  run: |
    aws s3 sync frontend/out s3://${{ secrets.S3_BUCKET_NAME }} --delete
```
**What it does:** Uploads the built files to your S3 bucket.

**`--delete`:** Removes old files that no longer exist.

---

```yaml
- name: Invalidate CloudFront
  run: |
    aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_DIST_ID }} --paths "/*"
```
**What it does:** Tells CloudFront "Clear your cache, there's new content!"

**Why?** Otherwise, users might see the old version for hours.

---

## 🌉 Part 3: The Code Changes

### `backend/server.py` (Bottom of file)

```python
from mangum import Mangum
handler = Mangum(app, lifespan="off")
```
**What it does:** Wraps your FastAPI `app` so it can run on Lambda.

**How it works:**
1. API Gateway sends a JSON event to Lambda.
2. Mangum converts it to an HTTP request.
3. FastAPI processes it.
4. Mangum converts the response back to JSON.

---

### `backend/pyproject.toml`

```toml
dependencies = [
    # ... other deps
    "mangum>=0.17.0",
]
```
**What it does:** Adds Mangum to your project dependencies.

---

## 🎯 The Full Flow

1. **You push code** to GitHub.
2. **GitHub Actions** runs:
   - Frontend: Builds Next.js → Uploads to S3 → Invalidates CloudFront.
   - Backend: Zips Python code → Uploads to Lambda.
3. **User visits your site**:
   - CloudFront serves the React app (fast!).
   - User clicks "Analyze Code".
   - Frontend calls API Gateway URL.
   - API Gateway triggers Lambda.
   - Mangum converts event → FastAPI processes → Returns response.
   - User sees results!

---

## 💡 Key Concepts

| Concept | What it is | Why we use it |
|---------|-----------|---------------|
| **Terraform** | Code that creates AWS resources | Repeatable, version-controlled infrastructure |
| **Lambda** | Serverless function | Pay only when code runs, auto-scales |
| **S3** | Cloud storage | Cheap hosting for static files |
| **CloudFront** | CDN | Fast global delivery |
| **API Gateway** | HTTP endpoint for Lambda | Gives Lambda a public URL |
| **Mangum** | FastAPI ↔ Lambda adapter | Bridges web framework and serverless |
| **GitHub Actions** | Automation | Deploys on every push |

---

## 🚀 Next Steps

1. **Study the Terraform files** - See how resources connect.
2. **Run `terraform plan`** - See what would be created (without creating it).
3. **Trace a request** - Follow the path from user click → CloudFront → API Gateway → Lambda → FastAPI.

Happy learning! 🎓
