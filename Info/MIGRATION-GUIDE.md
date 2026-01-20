# 🔄 Migration Guide: Serverless to Containers

This guide shows you exactly how to migrate from the serverless architecture (Lambda) to containers (App Runner) if you need to.

---

## When Should You Migrate?

Migrate from serverless to containers if you experience:
- ❌ Analysis tasks taking > 10 minutes (approaching Lambda's 15-min limit)
- ❌ Frequent cold starts affecting user experience
- ❌ Consistent high traffic (making containers cheaper)
- ❌ Need to store temporary files on disk

---

## Migration Process (Step-by-Step)

### Step 1: Update Backend Code

**Remove Mangum Handler** (only needed for Lambda):

```python
# In backend/server.py - DELETE these lines:
from mangum import Mangum
handler = Mangum(app, lifespan="off")
```

**That's it!** Your FastAPI code already works with containers.

---

### Step 2: Update Dockerfile

We already have a container-ready Dockerfile! Just verify it:

```dockerfile
# backend/Dockerfile (already exists)
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install uv

COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen

COPY backend/ ./

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### Step 3: Update Terraform Configuration

**Replace Lambda with App Runner:**

```hcl
# terraform/aws/main.tf - REPLACE Lambda section with:

# ECR Repository for Docker images
resource "aws_ecr_repository" "backend" {
  name                 = "securescript-backend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
}

# IAM Role for App Runner
resource "aws_iam_role" "app_runner_role" {
  name = "AppRunnerECRAccessRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "build.apprunner.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "app_runner_policy" {
  role       = aws_iam_role.app_runner_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# App Runner Service
resource "aws_apprunner_service" "backend" {
  service_name = "securescript-api"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.app_runner_role.arn
    }
    image_repository {
      image_identifier      = "${aws_ecr_repository.backend.repository_url}:latest"
      image_repository_type = "ECR"
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          GROQ_API_KEY             = var.groq_api_key
          CLERK_FRONTEND_API       = var.clerk_frontend_api
          REQUIRE_JWT_VERIFICATION = "true"
          ALLOWED_ORIGINS          = "*"
        }
      }
    }
  }

  instance_configuration {
    cpu    = "1024"
    memory = "2048"
  }
}

# Output the App Runner URL
output "app_runner_url" {
  value = aws_apprunner_service.backend.service_url
}
```

---

### Step 4: Update GitHub Actions

**Replace Lambda deployment with Docker build/push:**

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to AWS App Runner

on:
  push:
    branches: [ "main" ]
    paths:
      - 'backend/**'
      - 'Dockerfile'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build, tag, and push image to ECR
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: securescript-backend
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -f Dockerfile .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

    - name: Deploy to App Runner
      run: |
        aws apprunner start-deployment --service-arn $(aws apprunner list-services --query "ServiceSummaryList[?ServiceName=='securescript-api'].ServiceArn" --output text)
```

---

### Step 5: Deploy

```bash
# 1. Destroy existing Lambda infrastructure
cd terraform/aws
terraform destroy

# 2. Apply new App Runner infrastructure
terraform apply

# 3. Push code to trigger GitHub Actions
git add .
git commit -m "Migrate to App Runner"
git push
```

---

## What Changes in Your Workflow?

| Aspect | Serverless (Before) | Containers (After) |
|--------|---------------------|-------------------|
| **Deployment** | ZIP file to Lambda | Docker image to ECR |
| **Scaling** | Instant | 30-60 seconds |
| **Cold Starts** | Yes (1-2s) | No |
| **Cost (Idle)** | $0 | $30-50/month |
| **Max Duration** | 15 minutes | Unlimited |

---

## Rollback Plan

If you need to go back to serverless:

```bash
# 1. Re-add Mangum handler to server.py
# 2. Revert Terraform to Lambda configuration
# 3. Revert GitHub Actions to Lambda deployment
# 4. Run terraform apply
```

---

## Cost Impact

**Before (Serverless):**
- 1,000 requests/month: **$0**
- 10,000 requests/month: **~$2**

**After (Containers):**
- Any usage: **$30-50/month** (base cost)
- High traffic: **$50-150/month**

---

## Summary

**Migration is simple:**
1. Remove Mangum handler (2 lines)
2. Update Terraform (swap Lambda for App Runner)
3. Update GitHub Actions (Docker build instead of ZIP)
4. Deploy

**Time required:** ~1-2 hours

**Downtime:** ~5-10 minutes during the switch

**Reversible:** Yes, you can always go back!
