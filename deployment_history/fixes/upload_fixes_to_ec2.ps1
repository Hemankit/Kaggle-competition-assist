# Upload Fixed Files to EC2
# Run this from your local Windows machine

$EC2_IP = Read-Host "Enter your EC2 IP address"
$EC2_USER = "ubuntu"
$KEY_FILE = Read-Host "Enter path to your .pem key file"

Write-Host "🚀 Uploading fixed files to EC2..." -ForegroundColor Cyan

# Upload fixed Python files
Write-Host "`n📤 Uploading llm_loader.py..." -ForegroundColor Yellow
scp -i $KEY_FILE llms/llm_loader.py "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/llms/"

Write-Host "📤 Uploading model_registry.py..." -ForegroundColor Yellow
scp -i $KEY_FILE llms/model_registry.py "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/llms/"

Write-Host "📤 Uploading fixed test file..." -ForegroundColor Yellow
scp -i $KEY_FILE tests/test_working_llms.py "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/tests/"

# Upload the fix script
Write-Host "📤 Uploading verification script..." -ForegroundColor Yellow
scp -i $KEY_FILE fix_syntax_error_ec2.sh "${EC2_USER}@${EC2_IP}:~/Kaggle-competition-assist/"

Write-Host "`n✅ Files uploaded successfully!" -ForegroundColor Green
Write-Host "`nNext steps on EC2:" -ForegroundColor Cyan
Write-Host "1. SSH into EC2: ssh -i $KEY_FILE ${EC2_USER}@${EC2_IP}" -ForegroundColor White
Write-Host "2. Run: cd ~/Kaggle-competition-assist" -ForegroundColor White
Write-Host "3. Run: chmod +x fix_syntax_error_ec2.sh" -ForegroundColor White
Write-Host "4. Run: ./fix_syntax_error_ec2.sh" -ForegroundColor White
Write-Host "`nOR simply restart the service:" -ForegroundColor Cyan
Write-Host "sudo systemctl restart kaggle-backend" -ForegroundColor White
Write-Host "curl http://localhost:5000/health" -ForegroundColor White

Write-Host "`n🎉 Your backend should be ready!" -ForegroundColor Green

