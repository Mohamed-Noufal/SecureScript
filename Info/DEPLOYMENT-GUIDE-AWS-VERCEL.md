# 🚀 Complete Deployment Guide: AWS + Vercel

**Deploy SecureScript with Backend on AWS Lambda and Frontend on Vercel**

This guide provides **two deployment methods** for each platform:
- **🖥️ Web Console** (Beginner-friendly, visual interface)
- **⌨️ CLI** (Advanced, automation-ready)

**Total deployment time:** ~1 hour (Web Console) | ~30 minutes (CLI)

---

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                       │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         │                      │
    ┌────▼─────┐          ┌────▼──────┐
    │  Vercel  │          │ AWS Lambda│
    │ (Frontend)│◄────────►│ (Backend) │
    │ Next.js  │   API    │  FastAPI  │
    └──────────┘  Calls   └───────────┘
         │                      │
         │                      │
    ┌────▼─────┐          ┌────▼──────┐
    │  Clerk   │          │   Groq    │
    │  (Auth)  │          │   (LLM)   │
    └──────────┘          └───────────┘
```

**Why This Architecture?**
- ✅ **FREE** for MVP usage (both platforms have generous free tiers)
- ✅ **Fast** - Vercel optimized for Next.js, Lambda for APIs
- ✅ **Scalable** - Both auto-scale automatically
- ✅ **Simple** - Each platform does what it does best

---

## 🎯 Prerequisites

Before starting, ensure you have:

- [ ] **AWS Account** ([Sign up here](https://aws.amazon.com/free/))
- [ ] **GitHub Account** ([Sign up here](https://github.com/join))
- [ ] **Vercel Account** ([Sign up here](https://vercel.com/signup))
- [ ] **Windows PC** with PowerShell
- [ ] **Your project code** (you have this ✅)

---

## 📦 Part 1: Install Required Tools

### For CLI Method:

Open **PowerShell as Administrator** and run:

```powershell
# Install AWS CLI
winget install Amazon.AWSCLI

# Install Terraform (optional, for infrastructure as code)
winget install Hashicorp.Terraform

# Install Vercel CLI
npm install -g vercel

# Verify installations
aws --version
terraform --version
vercel --version
```

---

## 🔐 Part 2: Configure AWS Credentials

### Option A: Web Console Setup (Recommended for Beginners)

1. **Log in to AWS Console**: https://console.aws.amazon.com/
2. **You're ready!** The web console uses your login credentials automatically.

### Option B: CLI Setup

#### Step 2.1: Create AWS IAM User

1. **Log in to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to IAM**: Search for "IAM" in the top search bar
3. **Create User**:
   - Click **Users** → **Create user**
   - Username: `securescript-deployer`
   - Click **Next**
4. **Set Permissions**:
   - Select **Attach policies directly**
   - Search and select: `AdministratorAccess`
   - Click **Next** → **Create user**
5. **Create Access Keys**:
   - Click on the newly created user
   - Go to **Security credentials** tab
   - Click **Create access key**
   - Select **Command Line Interface (CLI)**
   - Check the confirmation box
   - Click **Create access key**
   - **IMPORTANT**: Copy both:
     - Access Key ID (starts with `AKIA...`)
     - Secret Access Key (long random string)
   - Click **Done**

#### Step 2.2: Configure AWS CLI

```powershell
aws configure
```

Enter when prompted:
```
AWS Access Key ID: [paste your Access Key ID]
AWS Secret Access Key: [paste your Secret Access Key]
Default region name: us-east-1
Default output format: json
```

#### Step 2.3: Verify AWS Configuration

```powershell
aws sts get-caller-identity
```

✅ If you see your account details, AWS is configured correctly!

---

## 🔧 Part 3: Prepare Backend Package

**This step is required for BOTH methods.**

### Step 3.1: Package Backend for Lambda

```powershell
# Navigate to your project
cd d:\LLM\end-end\deployment-production\code-saftey-analyzer\cyber

# Navigate to backend directory
cd backend

# Create a temporary package directory
New-Item -Path "package" -ItemType Directory -Force

# Install dependencies (Lambda-compatible)
pip install fastapi mangum slowapi pyjwt httpx python-dotenv openai -t package/

# Copy application files
Copy-Item server.py package/
Copy-Item context.py package/

# Create deployment zip
cd package
Compress-Archive -Path * -DestinationPath ..\backend.zip -Force
cd ..

# Clean up
Remove-Item -Recurse -Force package

# Return to project root
cd ..
```

✅ You now have `backend/backend.zip` ready for deployment!

---

## 🚀 Part 4: Deploy Backend to AWS Lambda

**Choose ONE method:**

---

### 🖥️ METHOD A: Web Console Deployment (Beginner-Friendly)

#### Step 4A.1: Create Lambda Function

1. **Open AWS Lambda Console**: https://console.aws.amazon.com/lambda/
2. **Click "Create function"**
3. **Configure function**:
   - Select: **Author from scratch**
   - Function name: `securescript-api-prod`
   - Runtime: **Python 3.12**
   - Architecture: **x86_64**
   - Click **Create function**

#### Step 4A.2: Upload Code

1. In the **Code** tab, scroll down to **Code source**
2. Click **Upload from** → **.zip file**
3. Click **Upload**
4. Select your `backend/backend.zip` file
5. Click **Save**
6. Wait for upload to complete (~30 seconds)

#### Step 4A.3: Configure Function Settings

1. **Go to Configuration tab** → **General configuration**
2. Click **Edit**
3. Set:
   - **Timeout**: 60 seconds
   - **Memory**: 512 MB
4. Click **Save**

#### Step 4A.4: Set Environment Variables

1. **Go to Configuration tab** → **Environment variables**
2. Click **Edit** → **Add environment variable**
3. Add the following variables:

| Key | Value |
|-----|-------|
| `GROQ_API_KEY` | `gsk_YOUR_GROQ_API_KEY_HERE` |
| `CLERK_FRONTEND_API` | `communal-turkey-46.clerk.accounts.dev` |
| `REQUIRE_JWT_VERIFICATION` | `true` |
| `ALLOWED_ORIGINS` | `*` (will update later with Vercel URL) |

4. Click **Save**

#### Step 4A.5: Update Handler

1. **Go to Code tab** → **Runtime settings**
2. Click **Edit**
3. Set **Handler** to: `server.handler`
4. Click **Save**

#### Step 4A.6: Create API Gateway

1. **Go to Configuration tab** → **Function URL**
2. Click **Create function URL**
3. **Auth type**: Select **NONE** (we handle auth in code)
4. **Configure CORS**:
   - Check **Configure cross-origin resource sharing (CORS)**
   - Allow origin: `*`
   - Allow methods: `GET, POST, PUT, DELETE, OPTIONS`
   - Allow headers: `*`
5. Click **Save**

6. **Copy the Function URL** (looks like: `https://abc123xyz.lambda-url.us-east-1.on.aws/`)

✅ **Backend is deployed!** Test it:

```powershell
curl https://YOUR_FUNCTION_URL/health
```

Expected: `{"status":"ok","service":"Cybersecurity Analyzer"}`

---

### ⌨️ METHOD B: CLI Deployment with Terraform (Advanced)

#### Step 4B.1: Create Terraform Configuration

Navigate to terraform directory:

```powershell
cd terraform\aws
```

Create `terraform.tfvars`:

```powershell
New-Item -Path "terraform.tfvars" -ItemType File -Force
```

Add this content to `terraform.tfvars`:

```hcl
aws_region          = "us-east-1"
stage               = "prod"
groq_api_key        = "gsk_YOUR_GROQ_API_KEY_HERE"
clerk_frontend_api  = "communal-turkey-46.clerk.accounts.dev"
```

#### Step 4B.2: Update Lambda Configuration

Open `main.tf` and update the `aws_lambda_function` resource (around line 100):

```hcl
resource "aws_lambda_function" "api" {
  function_name = "securescript-api-${var.stage}"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "server.handler"
  runtime       = "python3.12"
  filename      = "../../backend/backend.zip"  # Updated path
  
  timeout       = 60      # ADD THIS
  memory_size   = 512     # ADD THIS

  environment {
    variables = {
      GROQ_API_KEY             = var.groq_api_key
      CLERK_FRONTEND_API       = var.clerk_frontend_api
      REQUIRE_JWT_VERIFICATION = "true"
      ALLOWED_ORIGINS          = "*"
    }
  }
}
```

#### Step 4B.3: Deploy with Terraform

```powershell
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy
terraform apply
# Type 'yes' when prompted
```

⏳ Deployment takes 3-5 minutes.

#### Step 4B.4: Get API URL

```powershell
terraform output api_gateway_url
```

Copy this URL!

✅ **Backend is deployed!** Test it:

```powershell
curl https://YOUR_API_GATEWAY_URL/health
```

---

## 🌐 Part 5: Deploy Frontend to Vercel

**Choose ONE method:**

---

### 🖥️ METHOD A: Vercel Dashboard (Recommended for Beginners)

#### Step 5A.1: Push Code to GitHub

```powershell
# Navigate to project root
cd d:\LLM\end-end\deployment-production\code-saftey-analyzer\cyber

# Check git status
git status

# If not initialized, initialize git
git init
git add .
git commit -m "Ready for deployment"

# Create repository on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/securescript.git
git branch -M main
git push -u origin main
```

#### Step 5A.2: Import Project to Vercel

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Click "Add New"** → **Project**
3. **Import Git Repository**:
   - Click **Import** next to your GitHub repository
   - If not connected, click **Add GitHub Account** and authorize Vercel

#### Step 5A.3: Configure Project

1. **Configure Project**:
   - **Project Name**: `securescript` (or your choice)
   - **Framework Preset**: Next.js (auto-detected ✅)
   - **Root Directory**: Click **Edit** → Enter `frontend` → **Continue**
   - **Build Command**: `npm run build` (default ✅)
   - **Output Directory**: `.next` (default ✅)

#### Step 5A.4: Add Environment Variables

Click **Environment Variables** and add:

| Name | Value | Environment |
|------|-------|-------------|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | `pk_test_Y29tbXVuYWwtdHVya2V5LTQ2LmNsZXJrLmFjY291bnRzLmRldiQ` | Production, Preview, Development |
| `CLERK_SECRET_KEY` | `sk_test_ILa3SqbRBL1A1fbGNoZPwciDpDTLw8ef6O5HSxgWnE` | Production, Preview, Development |
| `NEXT_PUBLIC_API_URL` | `https://YOUR_AWS_API_URL` (from Part 4) | Production, Preview, Development |

#### Step 5A.5: Deploy

1. Click **Deploy**
2. ⏳ Wait 2-3 minutes for build to complete
3. **Copy your Vercel URL** (e.g., `https://securescript-xyz123.vercel.app`)

✅ **Frontend is live!**

---

### ⌨️ METHOD B: Vercel CLI (Advanced)

#### Step 5B.1: Login to Vercel

```powershell
# Navigate to frontend directory
cd d:\LLM\end-end\deployment-production\code-saftey-analyzer\cyber\frontend

# Login to Vercel
vercel login
# Follow the browser authentication
```

#### Step 5B.2: Deploy to Production

```powershell
# Deploy to production
vercel --prod

# Follow the prompts:
# Set up and deploy? Yes
# Which scope? Your account
# Link to existing project? No
# Project name? securescript
# Directory? ./ (current directory)
```

#### Step 5B.3: Add Environment Variables

```powershell
# Add environment variables
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY production
# Paste: pk_test_Y29tbXVuYWwtdHVya2V5LTQ2LmNsZXJrLmFjY291bnRzLmRldiQ

vercel env add CLERK_SECRET_KEY production
# Paste: sk_test_ILa3SqbRBL1A1fbGNoZPwciDpDTLw8ef6O5HSxgWnE

vercel env add NEXT_PUBLIC_API_URL production
# Paste: https://YOUR_AWS_API_URL
```

#### Step 5B.4: Redeploy with Environment Variables

```powershell
vercel --prod
```

✅ **Frontend is live!** The CLI will show your deployment URL.

---

## 🔗 Part 6: Connect Frontend & Backend

### Update Backend CORS Settings

**Web Console Method:**

1. Go to **Lambda Console**: https://console.aws.amazon.com/lambda/
2. Select your function: `securescript-api-prod`
3. Go to **Configuration** → **Environment variables**
4. Click **Edit**
5. Update `ALLOWED_ORIGINS` to: `https://YOUR_VERCEL_URL.vercel.app`
6. Click **Save**

**CLI Method:**

```powershell
aws lambda update-function-configuration `
  --function-name securescript-api-prod `
  --environment "Variables={
    GROQ_API_KEY=gsk_YOUR_GROQ_API_KEY_HERE,
    CLERK_FRONTEND_API=communal-turkey-46.clerk.accounts.dev,
    REQUIRE_JWT_VERIFICATION=true,
    ALLOWED_ORIGINS=https://YOUR_VERCEL_URL.vercel.app
  }"
```

---

## ✅ Part 7: Test Your Deployment

### Test 1: Frontend Loads

1. Open your Vercel URL in browser
2. ✅ You should see the SecureScript landing page

### Test 2: Authentication

1. Click **Sign In**
2. Sign up/sign in with Clerk
3. ✅ You should be redirected to the dashboard

### Test 3: Security Analysis

1. Upload or paste this vulnerable code:
```python
import os
password = "hardcoded_secret_123"
user_input = input("Enter command: ")
os.system(user_input)
```

2. Click **Analyze**
3. ✅ Security report should appear in 2-5 seconds

### Test 4: Auto-Fix

1. Click **Fix All**
2. ✅ Watch the streaming code fix

### Test 5: Rate Limiting

1. Perform 8 analysis requests quickly
2. ✅ The 8th should show "Rate limit exceeded"

---

## 📊 Monitoring & Logs

### AWS Lambda Logs

**Web Console:**
1. Go to **Lambda Console** → Your function
2. Click **Monitor** tab
3. Click **View CloudWatch logs**

**CLI:**
```powershell
aws logs tail /aws/lambda/securescript-api-prod --follow
```

### Vercel Logs

**Dashboard:**
1. Go to **Vercel Dashboard**
2. Select your project
3. Click **Deployments** → Latest deployment
4. View **Runtime Logs**

**CLI:**
```powershell
vercel logs
```

---

## 💰 Cost Monitoring

### Set Up AWS Billing Alerts

1. Go to **AWS Billing Console**: https://console.aws.amazon.com/billing/
2. Click **Budgets** → **Create budget**
3. Select **Zero spend budget**
4. Enter your email
5. Click **Create budget**

### Expected Costs

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| Lambda | 1M requests/month | ~1K/month | $0 |
| API Gateway | 1M requests/month | ~1K/month | $0 |
| Vercel | Unlimited | Unlimited | $0 |
| **Total** | | | **$0/month** |

---

## 🔧 Troubleshooting

### Issue: Lambda "Access Denied" Error

**Solution**: Ensure IAM role has `AWSLambdaBasicExecutionRole` policy.

**Web Console Fix:**
1. Go to **IAM Console** → **Roles**
2. Find your Lambda execution role
3. Click **Attach policies**
4. Search and attach: `AWSLambdaBasicExecutionRole`

### Issue: Lambda Timeout Errors

**Solution**: Increase timeout to 60+ seconds.

**Web Console Fix:**
1. Lambda Console → Your function → **Configuration** → **General configuration**
2. Click **Edit** → Set timeout to 60 seconds

**CLI Fix:**
```powershell
aws lambda update-function-configuration `
  --function-name securescript-api-prod `
  --timeout 60
```

### Issue: CORS Errors in Browser

**Solution**: Update Lambda CORS settings (see Part 6).

### Issue: "Module not found" in Lambda

**Solution**: Ensure all dependencies are in `backend.zip`. Re-package:

```powershell
cd backend
pip install -r pyproject.toml -t package/
# Copy files and re-zip
```

### Issue: Vercel Build Fails

**Solution**: Check build logs in Vercel dashboard. Common issues:
- Missing environment variables
- Incorrect root directory (should be `frontend`)
- Node.js version mismatch

**Fix**: In Vercel Dashboard → Project Settings → General → Node.js Version → Select 18.x or 20.x

---

## 🎉 Success!

You now have:
- ✅ Backend running on AWS Lambda
- ✅ Frontend running on Vercel
- ✅ Full authentication with Clerk
- ✅ AI-powered security analysis
- ✅ $0/month hosting costs

### Your Live URLs:
- **Frontend**: `https://YOUR_PROJECT.vercel.app`
- **Backend API**: `https://YOUR_FUNCTION_URL.lambda-url.us-east-1.on.aws/` or `https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com`

---

## 🚀 Next Steps

### 1. Custom Domain (Optional)

**Vercel:**
- Dashboard → Project → Settings → Domains → Add Domain

**AWS:**
- Use Route 53 to configure custom domain for API Gateway

### 2. CI/CD Setup (Optional)

**GitHub Actions** (already configured in `.github/workflows/`):

1. Add AWS credentials to GitHub Secrets:
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Add: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`

2. Push to main branch → Auto-deploy!

**Vercel** (automatic):
- Already set up! Every push to main auto-deploys.

### 3. Monitoring & Analytics

**AWS CloudWatch:**
- Set up dashboards for Lambda metrics
- Create alarms for errors

**Vercel Analytics:**
- Enable in Project Settings → Analytics

### 4. Share Your Project

- Add live URL to `README.md`
- Share on LinkedIn/Twitter
- Add to your portfolio

---

## 📞 Support Resources

### AWS Lambda
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/)

### Vercel
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Reference](https://vercel.com/docs/cli)

### Troubleshooting
- **CloudWatch Logs**: `aws logs tail /aws/lambda/securescript-api-prod`
- **Vercel Logs**: Dashboard → Deployments → Runtime Logs

---

## 🎓 Deployment Method Comparison

| Feature | Web Console | CLI/Terraform |
|---------|-------------|---------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Beginner-friendly | ⭐⭐⭐ Requires technical knowledge |
| **Speed** | ⭐⭐⭐ Slower (manual clicks) | ⭐⭐⭐⭐⭐ Faster (automated) |
| **Automation** | ❌ Manual only | ✅ CI/CD ready |
| **Version Control** | ❌ No infrastructure versioning | ✅ Infrastructure as Code |
| **Repeatability** | ⭐⭐ Manual process | ⭐⭐⭐⭐⭐ Fully repeatable |
| **Best For** | Learning, testing, one-time deploys | Production, teams, multiple environments |

**Recommendation:**
- **First deployment?** Use Web Console to understand the process
- **Production/Team?** Use CLI/Terraform for automation and consistency

---

**Congratulations on your deployment! 🎊**
