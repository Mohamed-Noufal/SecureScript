# Destroy Script for AWS Backend
# Run this script to remove all AWS resources and stop billing

Write-Host "⚠️  WARNING: This will destroy all AWS resources!" -ForegroundColor Red
Write-Host ""
Write-Host "Resources that will be deleted:" -ForegroundColor Yellow
Write-Host "  - Lambda function: securescript-api-prod" -ForegroundColor White
Write-Host "  - API Gateway: securescript-gw-prod" -ForegroundColor White
Write-Host "  - IAM roles and policies" -ForegroundColor White
Write-Host ""

# Show current resources
Write-Host "📋 Current resources:" -ForegroundColor Cyan
terraform show
Write-Host ""

# Confirm destruction
Write-Host "⚠️  Are you absolutely sure?" -ForegroundColor Red
$confirmation = Read-Host "Type 'destroy' to confirm"
if ($confirmation -ne "destroy") {
    Write-Host "❌ Destruction cancelled" -ForegroundColor Green
    exit 0
}
Write-Host ""

# Destroy
Write-Host "💥 Destroying AWS resources..." -ForegroundColor Red
terraform destroy -auto-approve
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Destruction failed!" -ForegroundColor Red
    Write-Host "You may need to manually delete resources in AWS Console" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

Write-Host "✅ All resources destroyed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "💰 Your AWS bill should now be $0/month" -ForegroundColor Cyan
Write-Host ""
Write-Host "To redeploy, run: .\deploy.ps1" -ForegroundColor Yellow
