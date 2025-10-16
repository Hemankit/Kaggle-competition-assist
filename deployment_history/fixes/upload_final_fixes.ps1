# Upload FINAL Fixed Files - Conditional Imports
$IP = "18.219.148.57"
$KEY = "C:\Users\heman\Downloads\Key__2__Success.pem"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPLOADING FINAL FIXES TO EC2" -ForegroundColor Cyan  
Write-Host "  (Conditional Ollama/HuggingFace imports)" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Uploading llm_loader.py (with conditional imports)..." -ForegroundColor Yellow
scp -i $KEY llms/llm_loader.py ubuntu@${IP}:~/Kaggle-competition-assist/llms/
if ($LASTEXITCODE -eq 0) { Write-Host "    ✅ Success" -ForegroundColor Green } else { Write-Host "    ❌ Failed" -ForegroundColor Red; exit 1 }

Write-Host "[2/3] Uploading model_registry.py (with conditional imports)..." -ForegroundColor Yellow
scp -i $KEY llms/model_registry.py ubuntu@${IP}:~/Kaggle-competition-assist/llms/
if ($LASTEXITCODE -eq 0) { Write-Host "    ✅ Success" -ForegroundColor Green } else { Write-Host "    ❌ Failed" -ForegroundColor Red; exit 1 }

Write-Host "[3/3] Uploading fixed minimal_backend.py (Kaggle API bug)..." -ForegroundColor Yellow
scp -i $KEY minimal_backend.py ubuntu@${IP}:~/Kaggle-competition-assist/
if ($LASTEXITCODE -eq 0) { Write-Host "    ✅ Success" -ForegroundColor Green } else { Write-Host "    ❌ Failed" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ All files uploaded!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Cyan
Write-Host "  • Ollama import now conditional (won't break production)" -ForegroundColor White
Write-Host "  • HuggingFace import now conditional" -ForegroundColor White
Write-Host "  • Kaggle API category bug fixed" -ForegroundColor White
Write-Host ""
Write-Host "Next: Restart backend on EC2" -ForegroundColor Cyan
Write-Host ""

$openSSH = Read-Host "Open SSH and restart backend? (y/n)"
if ($openSSH -eq "y" -or $openSSH -eq "Y") {
    Write-Host ""
    Write-Host "Connecting to EC2..." -ForegroundColor Green
    Write-Host "Commands to run:" -ForegroundColor Yellow
    Write-Host "  cd ~/Kaggle-competition-assist" -ForegroundColor White
    Write-Host "  source venv/bin/activate" -ForegroundColor White
    Write-Host "  sudo systemctl restart kaggle-backend" -ForegroundColor White
    Write-Host "  sleep 5" -ForegroundColor White
    Write-Host "  curl http://localhost:5000/health" -ForegroundColor White
    Write-Host ""
    ssh -i $KEY ubuntu@${IP}
}


