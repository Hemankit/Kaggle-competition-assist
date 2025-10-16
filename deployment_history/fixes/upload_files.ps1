# Upload Fixed Files to EC2
# Simple version without special characters

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       KAGGLE COPILOT - FILE UPLOAD TO EC2            " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# Get EC2 details
$EC2_IP = (Read-Host "Enter your EC2 IP address").Trim()
Write-Host ""
$KEY_FILE = (Read-Host "Enter full path to your .pem key file").Trim().Trim('"')

$EC2_USER = "ubuntu"

# Validate inputs
if ([string]::IsNullOrWhiteSpace($EC2_IP)) {
    Write-Host "Error: EC2 IP address is required" -ForegroundColor Red
    exit 1
}

if ([string]::IsNullOrWhiteSpace($KEY_FILE)) {
    Write-Host "Error: Key file path is required" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $KEY_FILE)) {
    Write-Host "Error: Key file not found at: $KEY_FILE" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Using EC2 IP: $EC2_IP" -ForegroundColor Cyan
Write-Host "Using Key: $KEY_FILE" -ForegroundColor Cyan

Write-Host ""
Write-Host "Uploading fixed files to EC2..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Gray
Write-Host ""

# Upload fixed LLM files
Write-Host "[1/3] Uploading llm_loader.py..." -ForegroundColor Yellow
scp -i $KEY_FILE llms/llm_loader.py "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/llms/"
if ($LASTEXITCODE -eq 0) { 
    Write-Host "      SUCCESS" -ForegroundColor Green 
} else { 
    Write-Host "      FAILED" -ForegroundColor Red 
    exit 1
}

Write-Host "[2/3] Uploading model_registry.py..." -ForegroundColor Yellow
scp -i $KEY_FILE llms/model_registry.py "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/llms/"
if ($LASTEXITCODE -eq 0) { 
    Write-Host "      SUCCESS" -ForegroundColor Green 
} else { 
    Write-Host "      FAILED" -ForegroundColor Red 
    exit 1
}

Write-Host "[3/3] Uploading test file..." -ForegroundColor Yellow
scp -i $KEY_FILE tests/test_working_llms.py "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/tests/"
if ($LASTEXITCODE -eq 0) { 
    Write-Host "      SUCCESS" -ForegroundColor Green 
} else { 
    Write-Host "      FAILED" -ForegroundColor Red 
    exit 1
}

Write-Host ""
Write-Host "All files uploaded successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "NEXT STEPS - Run these commands on EC2:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. SSH to EC2:" -ForegroundColor Yellow
Write-Host "   ssh -i $KEY_FILE ${EC2_USER}@${EC2_IP}" -ForegroundColor White
Write-Host ""
Write-Host "2. Then run these commands:" -ForegroundColor Yellow
Write-Host "   cd ~/Kaggle-competition-assist" -ForegroundColor White
Write-Host "   source venv/bin/activate" -ForegroundColor White
Write-Host "   sudo systemctl restart kaggle-backend" -ForegroundColor White
Write-Host "   sleep 5" -ForegroundColor White
Write-Host "   curl http://localhost:5000/health" -ForegroundColor White
Write-Host ""
Write-Host "Expected output: {""status"": ""healthy""}" -ForegroundColor Green
Write-Host ""
Write-Host "========================================================" -ForegroundColor Gray
Write-Host ""

# Offer to open SSH
$openSSH = Read-Host "Open SSH connection now? (y/n)"
if ($openSSH -eq "y" -or $openSSH -eq "Y") {
    Write-Host ""
    Write-Host "Connecting to EC2..." -ForegroundColor Green
    Write-Host ""
    ssh -i $KEY_FILE "${EC2_USER}@${EC2_IP}"
} else {
    Write-Host ""
    Write-Host "Files uploaded successfully. Connect to EC2 when ready!" -ForegroundColor Green
    Write-Host ""
}

