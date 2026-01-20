# 🛠️ AWS Serverless Deployment Guide

This architecture uses the most modern, cost-effective AWS services for an AI application.

## 🏗️ Architecture
- **Frontend**: Next.js (Static Export) -> **Amazon S3** -> **Amazon CloudFront**
- **Backend**: FastAPI (Python) -> **AWS Lambda** -> **Amazon API Gateway**
- **Infrastructure**: **Terraform**

---

## 🚀 Step-by-Step Deployment

### 1. Provision Infrastructure (Terraform)
1. Navigate to `terraform/aws`.
2. Initialize and apply:
   ```bash
   terraform init
   terraform apply -var="groq_api_key=SK_..." -var="clerk_frontend_api=clerk.your-app.com"
   ```
3. Save the outputs:
   - `s3_bucket_name`
   - `cloudfront_domain_name`
   - `api_gateway_url`

### 2. Configure GitHub Secrets
Add these to your GitHub repository (**Settings > Secrets > Actions**):
- `AWS_ACCESS_KEY_ID`: Your IAM user access key
- `AWS_SECRET_ACCESS_KEY`: Your IAM user secret key
- `AWS_REGION`: `us-east-1`
- `S3_BUCKET_NAME`: (From Terraform output)
- `CLOUDFRONT_DIST_ID`: (From AWS Console/Terraform)
- `CLERK_PUBLISHABLE_KEY`: (From Clerk Dashboard)
- `BACKEND_API_URL`: (Your API Gateway URL)

### 3. Deploy
Pushing to the `main` branch will now automatically:
1. Build and sync the Frontend to **S3** and invalidate **CloudFront**.
2. Package and upload the Backend to **Lambda**.

---

## 📝 Technical Details

### Backend (Lambda)
- Uses **Mangum** to bridge FastAPI and AWS Lambda.
- Memory: 2GB (for LLM processing overhead).
- Port: 8000.

### Frontend (CloudFront)
- Serving static assets from S3.
- SSL/HTTPS enabled by default.
- Global CDN caching for performance.
