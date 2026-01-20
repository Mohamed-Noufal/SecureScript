# Deploy Script for AWS Backend
# Run this script to deploy your backend to AWS Lambda

Write-Host "🚀 Starting SecureScript Backend Deployment..." -ForegroundColor Cyan
Write-Host ""

# Check for Docker
if (Get-Command "docker" -ErrorAction SilentlyContinue) {
    Write-Host "🐳 Docker found. Building Linux-compatible dependencies..." -ForegroundColor Cyan
    $ProjectRoot = Resolve-Path "..\.."
    $BackendPath = "$ProjectRoot\backend"
    
    # Run Docker Build
    docker run --rm -v "${BackendPath}:/app" python:3.12-slim bash -c "pip install fastapi mangum slowapi pyjwt httpx python-dotenv openai -t /app/package_linux --quiet"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies built successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker build failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️  Docker not found. Skipping dependency build." -ForegroundColor Yellow
    Write-Host "   Ensure 'backend\package_linux' already exists." -ForegroundColor Yellow
}

# Create Zip Package using Python
Write-Host "📦 Creating deployment package..." -ForegroundColor Cyan
python "..\..\backend\create_package.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create deployment package" -ForegroundColor Red
    exit 1
}

# Check if backend.zip exists
if (-not (Test-Path "..\..\backend\backend.zip")) {
    Write-Host "❌ Error: backend.zip not found!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found backend.zip" -ForegroundColor Green
Write-Host ""

# Initialize Terraform
Write-Host "📦 Initializing Terraform..." -ForegroundColor Cyan
terraform init
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform init failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Validate configuration
Write-Host "🔍 Validating Terraform configuration..." -ForegroundColor Cyan
terraform validate
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform validation failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Configuration is valid" -ForegroundColor Green
Write-Host ""

# Show plan
Write-Host "📋 Generating deployment plan..." -ForegroundColor Cyan
terraform plan
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Terraform plan failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Confirm deployment
Write-Host "⚠️  Ready to deploy to AWS!" -ForegroundColor Yellow
$confirmation = Read-Host "Do you want to proceed? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}
Write-Host ""

# Apply
Write-Host "🚀 Deploying to AWS Lambda..." -ForegroundColor Cyan
terraform apply -auto-approve
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Show outputs
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Deployment Information:" -ForegroundColor Cyan
terraform output
Write-Host ""
Write-Host "🎉 Backend is now live!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update frontend env vars with the API Gateway URL above." -ForegroundColor White
Write-Host "2. Test the connection." -ForegroundColor White
