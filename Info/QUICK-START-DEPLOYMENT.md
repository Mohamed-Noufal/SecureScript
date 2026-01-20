# 🚀 Quick Start: Deploy in 30 Minutes

**TL;DR**: Deploy backend to AWS Lambda, frontend to Vercel. Both FREE.

---

## Prerequisites (5 min)

```powershell
# Install tools
winget install Amazon.AWSCLI
winget install Hashicorp.Terraform

# Configure AWS
aws configure
# Enter: Access Key, Secret Key, Region: us-east-1
```

---

## Deploy Backend (15 min)

```powershell
# 1. Package backend
cd backend
pip install fastapi mangum slowapi pyjwt httpx python-dotenv openai -t package/
Copy-Item server.py package/
Copy-Item context.py package/
cd package
Compress-Archive -Path * -DestinationPath ..\backend.zip -Force
cd ..
Move-Item backend.zip ..\terraform\aws\backend.zip -Force

# 2. Create terraform.tfvars
cd ..\terraform\aws
# Add your API keys to terraform.tfvars (see full guide)

# 3. Deploy
terraform init
terraform apply
# Type 'yes'

# 4. Get API URL
terraform output
```

**Copy the API Gateway URL!**

---

## Deploy Frontend (10 min)

1. **Push to GitHub**:
```powershell
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy to Vercel**:
   - Go to https://vercel.com
   - Import your GitHub repo
   - Set Root Directory: `frontend`
   - Add environment variables:
     - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
     - `CLERK_SECRET_KEY`
     - `NEXT_PUBLIC_API_URL` (your API Gateway URL)
   - Click Deploy

3. **Update CORS**:
```powershell
aws lambda update-function-configuration `
  --function-name securescript-api-prod `
  --environment "Variables={ALLOWED_ORIGINS=https://YOUR_VERCEL_URL.vercel.app,...}"
```

---

## Test

1. Open Vercel URL
2. Sign in
3. Analyze code
4. ✅ Done!

**For detailed instructions, see [DEPLOYMENT-GUIDE-AWS-VERCEL.md](./DEPLOYMENT-GUIDE-AWS-VERCEL.md)**
