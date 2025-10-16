# PowerShell Script to Transfer .env to EC2
# Run this from your local machine (Windows)

Write-Host "🚀 Transfer .env to EC2 Instance" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Get EC2 IP
$ec2_ip = Read-Host "Enter your EC2 IP address"

# Get key file path
$key_path = Read-Host "Enter path to your .pem key file (e.g., C:\Users\heman\Downloads\my-key.pem)"

# Verify files exist
if (-not (Test-Path ".env")) {
    Write-Host "❌ ERROR: .env file not found in current directory!" -ForegroundColor Red
    Write-Host "Make sure you're running this from C:\Users\heman\Kaggle-competition-assist" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $key_path)) {
    Write-Host "❌ ERROR: Key file not found at $key_path" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Found .env file" -ForegroundColor Green
Write-Host "✅ Found key file" -ForegroundColor Green
Write-Host ""

# Create a temporary .env with ENVIRONMENT=production
Write-Host "📝 Creating production .env..." -ForegroundColor Cyan
$env_content = Get-Content .env
$env_content = $env_content -replace 'ENVIRONMENT=development', 'ENVIRONMENT=production'
$env_content | Out-File -FilePath .env.production -Encoding UTF8

Write-Host "✅ Production .env created" -ForegroundColor Green
Write-Host ""

# Transfer file
Write-Host "📤 Transferring .env to EC2..." -ForegroundColor Cyan
try {
    scp -i $key_path .env.production ubuntu@${ec2_ip}:/home/ubuntu/Kaggle-competition-assist/.env
    Write-Host "✅ Transfer complete!" -ForegroundColor Green
} catch {
    Write-Host "❌ Transfer failed: $_" -ForegroundColor Red
    exit 1
}

# Clean up
Remove-Item .env.production

Write-Host ""
Write-Host "🎉 Success! Your .env file is now on EC2" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Connect to EC2: ssh -i $key_path ubuntu@$ec2_ip"
Write-Host "2. Verify .env: cat /home/ubuntu/Kaggle-competition-assist/.env | head -n 5"
Write-Host "3. Run setup: cd /home/ubuntu/Kaggle-competition-assist && ./setup_services.sh"
Write-Host ""

