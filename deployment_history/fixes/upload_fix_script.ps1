# Upload Complete Fix Script to EC2

$IP = "18.219.148.57"
$KEY = "C:\Users\heman\Downloads\Key__2__Success.pem"

Write-Host "Uploading complete fix script to EC2..." -ForegroundColor Green

scp -i $KEY complete_backend_fix.sh ubuntu@${IP}:~/Kaggle-competition-assist/

Write-Host "`n✅ Script uploaded!" -ForegroundColor Green
Write-Host "`nNow SSH to EC2 and run:" -ForegroundColor Cyan
Write-Host "cd ~/Kaggle-competition-assist" -ForegroundColor White
Write-Host "chmod +x complete_backend_fix.sh" -ForegroundColor White
Write-Host "./complete_backend_fix.sh" -ForegroundColor White
Write-Host ""

$openSSH = Read-Host "Open SSH connection now? (y/n)"
if ($openSSH -eq "y" -or $openSSH -eq "Y") {
    ssh -i $KEY ubuntu@${IP}
}


