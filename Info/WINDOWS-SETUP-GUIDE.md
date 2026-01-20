# 🚀 Complete Setup Guide - Deploy from Windows

This guide shows you **everything** you need to install and configure to deploy SecureScript from your Windows laptop.

---

## ✅ Prerequisites Checklist

Before you start, you need:
- [ ] Windows 10/11
- [ ] Internet connection
- [ ] AWS account (free tier is fine)
- [ ] GitHub account
- [ ] Admin access on your laptop

---

## 📦 Step 1: Install Required Software

### 1.1 Install Git for Windows
**What it is:** Version control system

**Download:** https://git-scm.com/download/win

**Installation:**
1. Download the installer
2. Run it and click "Next" through all options (defaults are fine)
3. Verify installation:
```powershell
git --version
# Should show: git version 2.x.x
```

---

### 1.2 Install AWS CLI
**What it is:** Command-line tool to interact with AWS

**Download:** https://awscli.amazonaws.com/AWSCLIV2.msi

**Installation:**
1. Download and run the MSI installer
2. Follow the installation wizard
3. Verify installation:
```powershell
aws --version
# Should show: aws-cli/2.x.x Python/3.x.x Windows/10
```

---

### 1.3 Install Terraform
**What it is:** Infrastructure as Code tool

**Download:** https://www.terraform.io/downloads

**Installation (Easy Way):**
1. Download the Windows AMD64 ZIP file
2. Extract `terraform.exe` to `C:\terraform\`
3. Add to PATH:
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" → Edit
   - Click "New" → Add `C:\terraform`
   - Click OK on all windows
4. **Restart PowerShell**
5. Verify installation:
```powershell
terraform --version
# Should show: Terraform v1.x.x
```

**Alternative (Using Chocolatey):**
```powershell
# Install Chocolatey first (if you don't have it)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then install Terraform
choco install terraform
```

---

### 1.4 Install Node.js (for Frontend)
**What it is:** JavaScript runtime for Next.js

**Download:** https://nodejs.org/ (LTS version)

**Installation:**
1. Download and run the installer
2. Click "Next" through all options
3. Verify installation:
```powershell
node --version
# Should show: v20.x.x

npm --version
# Should show: 10.x.x
```

---

### 1.5 Install Python (for Backend)
**What it is:** Programming language for FastAPI

**Download:** https://www.python.org/downloads/ (Python 3.12)

**Installation:**
1. Download the installer
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Click "Install Now"
4. Verify installation:
```powershell
python --version
# Should show: Python 3.12.x

pip --version
# Should show: pip 24.x.x
```

---

## 🔐 Step 2: Configure AWS

### 2.1 Create AWS Account
1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the signup process (you'll need a credit card, but won't be charged if you stay in free tier)

### 2.2 Create IAM User
1. Log into AWS Console
2. Go to **IAM** → **Users** → **Create user**
3. Username: `terraform-deploy`
4. Check "Provide user access to the AWS Management Console" (optional)
5. Click "Next"
6. Attach policies:
   - `AmazonS3FullAccess`
   - `AWSLambda_FullAccess`
   - `CloudFrontFullAccess`
   - `IAMFullAccess`
   - `AmazonAPIGatewayAdministrator`
7. Click "Create user"

### 2.3 Create Access Keys
1. Click on the user you just created
2. Go to **Security credentials** tab
3. Scroll to "Access keys" → Click "Create access key"
4. Select "Command Line Interface (CLI)"
5. Check the confirmation box
6. Click "Create access key"
7. **IMPORTANT:** Copy both:
   - Access key ID (starts with `AKIA...`)
   - Secret access key (long random string)
8. Save these somewhere safe (you'll need them next)

### 2.4 Configure AWS CLI
```powershell
aws configure
```

**Enter the following when prompted:**
```
AWS Access Key ID: <paste your access key ID>
AWS Secret Access Key: <paste your secret access key>
Default region name: us-east-1
Default output format: json
```

**Verify it works:**
```powershell
aws sts get-caller-identity
# Should show your account info
```

---

## 🔧 Step 3: Prepare Your Project

### 3.1 Navigate to Your Project
```powershell
cd D:\LLM\end-end\deployment-production\code-saftey-analyzer\cyber
```

### 3.2 Install Backend Dependencies
```powershell
cd backend
pip install uv
uv sync
cd ..
```

### 3.3 Install Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

### 3.4 Configure Environment Variables

**Backend (`backend/.env`):**
```bash
GROQ_API_KEY=your_groq_api_key_here
CLERK_FRONTEND_API=your-app.clerk.accounts.dev
REQUIRE_JWT_VERIFICATION=true
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (`frontend/.env.local`):**
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🚀 Step 4: Deploy to AWS

### 4.1 Initialize Terraform
```powershell
cd terraform\aws
terraform init
```

**Expected output:**
```
Terraform has been successfully initialized!
```

### 4.2 Plan Deployment
```powershell
terraform plan -var="groq_api_key=YOUR_GROQ_KEY" -var="clerk_frontend_api=YOUR_CLERK_URL"
```

**This shows what will be created (doesn't actually create anything yet)**

### 4.3 Deploy Infrastructure
```powershell
terraform apply -var="groq_api_key=YOUR_GROQ_KEY" -var="clerk_frontend_api=YOUR_CLERK_URL"
```

**Type `yes` when prompted**

**Expected output:**
```
Apply complete! Resources: 8 added, 0 changed, 0 destroyed.

Outputs:
api_gateway_url = "https://abc123.execute-api.us-east-1.amazonaws.com"
cloudfront_domain_name = "d1234567890.cloudfront.net"
s3_bucket_name = "securescript-frontend-prod"
```

**Save these URLs!** You'll need them.

---

## 🌐 Step 5: Deploy Your Code

### 5.1 Update Frontend Environment
Edit `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=https://abc123.execute-api.us-east-1.amazonaws.com
```
(Use the `api_gateway_url` from Terraform output)

### 5.2 Build Frontend
```powershell
cd frontend
npm run build
```

### 5.3 Deploy Frontend to S3
```powershell
aws s3 sync out s3://securescript-frontend-prod --delete
```
(Use the `s3_bucket_name` from Terraform output)

### 5.4 Invalidate CloudFront Cache
```powershell
# Get distribution ID
aws cloudfront list-distributions --query "DistributionList.Items[0].Id" --output text

# Invalidate (replace DISTRIBUTION_ID with the output above)
aws cloudfront create-invalidation --distribution-id DISTRIBUTION_ID --paths "/*"
```

### 5.5 Deploy Backend to Lambda
```powershell
cd ..\..\backend
pip install --target . -r pyproject.toml
Compress-Archive -Path * -DestinationPath ..\backend.zip -Force
aws lambda update-function-code --function-name securescript-api-prod --zip-file fileb://..\backend.zip
```

---

## ✅ Step 6: Test Your Deployment

### 6.1 Test Backend
```powershell
curl https://abc123.execute-api.us-east-1.amazonaws.com/health
```

**Expected:** `{"status":"ok","service":"Cybersecurity Analyzer"}`

### 6.2 Test Frontend
Open browser: `https://d1234567890.cloudfront.net`

**Expected:** Your SecureScript UI loads

---

## 🎯 Step 7: Set Up GitHub Actions (Optional but Recommended)

### 7.1 Push to GitHub
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/securescript.git
git push -u origin main
```

### 7.2 Add GitHub Secrets
Go to: **GitHub Repo → Settings → Secrets and variables → Actions**

Add:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: `us-east-1`
- `S3_BUCKET_NAME`: From Terraform output
- `CLOUDFRONT_DIST_ID`: From AWS Console
- `GROQ_API_KEY`: Your Groq API key
- `CLERK_PUBLISHABLE_KEY`: Your Clerk key

### 7.3 Future Deployments
```powershell
# Just push your code
git add .
git commit -m "Updated feature"
git push

# GitHub Actions deploys automatically!
```

---

## 🐛 Troubleshooting

### "terraform: command not found"
- Restart PowerShell after installing Terraform
- Check PATH environment variable

### "aws: command not found"
- Restart PowerShell after installing AWS CLI
- Reinstall AWS CLI

### "Access Denied" errors
- Check IAM user has correct permissions
- Run `aws configure` again

### Terraform errors
- Make sure you're in `terraform/aws` directory
- Run `terraform init` first

---

## 💰 Cost Estimate

**With AWS Free Tier:**
- First year: **$0-5/month**
- After free tier: **$10-20/month** (for low traffic)

---

## ✅ Summary

**You installed:**
- ✅ Git
- ✅ AWS CLI
- ✅ Terraform
- ✅ Node.js
- ✅ Python

**You configured:**
- ✅ AWS account and credentials
- ✅ Environment variables

**You deployed:**
- ✅ Infrastructure with Terraform
- ✅ Frontend to S3 + CloudFront
- ✅ Backend to Lambda

**Your app is now live!** 🚀

**No Linux needed - everything works on Windows!** 💻
