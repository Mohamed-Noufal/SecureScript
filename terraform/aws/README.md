# SecureScript AWS Terraform

This directory contains Terraform configuration for deploying the SecureScript backend to AWS Lambda.

## 📁 Files

- `main.tf` - Main infrastructure configuration (Lambda + API Gateway)
- `variables.tf` - Input variables
- `outputs.tf` - Output values (API URL, function name)
- `terraform.tfvars` - Your API keys and configuration (gitignored)
- `deploy.ps1` - Automated deployment script
- `destroy.ps1` - Automated cleanup script

## 🚀 Quick Deploy

### Option 1: Using Deploy Script (Recommended)

```powershell
.\deploy.ps1
```

### Option 2: Manual Deployment

```powershell
# Initialize
terraform init

# Preview changes
terraform plan

# Deploy
terraform apply

# Get API URL
terraform output api_gateway_url
```

## 🗑️ Destroy Resources

To remove all AWS resources and stop billing:

```powershell
.\destroy.ps1
```

Or manually:

```powershell
terraform destroy
```

## 📊 What Gets Created

- **Lambda Function**: `securescript-api-prod`
  - Runtime: Python 3.12
  - Memory: 512 MB
  - Timeout: 60 seconds
  
- **API Gateway**: `securescript-gw-prod`
  - Type: HTTP API
  - CORS enabled
  - Auto-deploy enabled

- **IAM Role**: `securescript_lambda_role_prod`
  - Basic Lambda execution permissions

## 💰 Cost

All resources are within AWS Free Tier:
- Lambda: 1M requests/month free
- API Gateway: 1M requests/month free
- **Expected cost: $0/month** for MVP usage

## 🔧 Configuration

Edit `terraform.tfvars` to change:
- AWS region
- API keys
- Deployment stage (dev/prod)

## 📝 Notes

- Frontend is deployed to Vercel (not included here)
- S3 and CloudFront resources removed (not needed)
- Backend.zip must exist in `../../backend/` before deployment
