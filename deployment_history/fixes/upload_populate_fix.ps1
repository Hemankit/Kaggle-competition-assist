Write-Host "Uploading corrected populate_all_competition_data.py..." -ForegroundColor Cyan

$key = "C:\Users\heman\Downloads\Key__2__Success.pem"
$host_ip = "ubuntu@18.219.148.57"

# Upload the file
scp -i $key -o ConnectTimeout=10 populate_all_competition_data.py ${host_ip}:/home/ubuntu/Kaggle-competition-assist/

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] File uploaded successfully!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Upload failed" -ForegroundColor Red
    exit 1
}


