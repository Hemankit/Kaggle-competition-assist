# Upload ALL Fixed Files to EC2
# This script uploads everything needed for full functionality

$IP = "18.219.148.57"
$KEY = "C:\Users\heman\Downloads\Key__2__Success.pem"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  UPLOADING ALL FIXES TO EC2" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$files = @(
    @{local="minimal_backend.py"; remote="~/Kaggle-competition-assist/minimal_backend.py"; desc="Fixed backend (Kaggle API bug)"},
    @{local="llms/llm_loader.py"; remote="~/Kaggle-competition-assist/llms/llm_loader.py"; desc="Fixed LLM loader (DeepSeek)"},
    @{local="llms/model_registry.py"; remote="~/Kaggle-competition-assist/llms/model_registry.py"; desc="Fixed model registry"},
    @{local="complete_backend_fix.sh"; remote="~/Kaggle-competition-assist/complete_backend_fix.sh"; desc="Complete fix script"}
)

$success = 0
$failed = 0

foreach ($file in $files) {
    Write-Host "[$($success + $failed + 1)/$($files.Count)] Uploading $($file.desc)..." -ForegroundColor Yellow
    
    scp -i $KEY $file.local ubuntu@${IP}:$file.remote 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✅ Success" -ForegroundColor Green
        $success++
    } else {
        Write-Host "    ❌ Failed" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload Summary:" -ForegroundColor Cyan
Write-Host "  ✅ Success: $success" -ForegroundColor Green
Write-Host "  ❌ Failed: $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($failed -gt 0) {
    Write-Host "⚠️  Some files failed to upload. Please check connection." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ All files uploaded successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps on EC2:" -ForegroundColor Cyan
Write-Host "1. cd ~/Kaggle-competition-assist" -ForegroundColor White
Write-Host "2. chmod +x complete_backend_fix.sh" -ForegroundColor White
Write-Host "3. ./complete_backend_fix.sh" -ForegroundColor White
Write-Host ""

$openSSH = Read-Host "Open SSH connection now? (y/n)"
if ($openSSH -eq "y" -or $openSSH -eq "Y") {
    Write-Host ""
    Write-Host "Connecting to EC2..." -ForegroundColor Green
    ssh -i $KEY ubuntu@${IP}
}


