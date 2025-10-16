#!/usr/bin/env pwsh
# Upload Perplexity fix to EC2

$EC2_HOST = "ubuntu@18.219.148.57"
$KEY_PATH = "C:\Users\heman\Downloads\Key__2__Success.pem"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "UPLOADING PERPLEXITY FIX TO EC2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$files = @(
    @{Name="Fixed LLM Loader"; File="llms/llm_loader.py"},
    @{Name="Updated Requirements"; File="requirements.txt"},
    @{Name="Perplexity Fix Script"; File="fix_perplexity_ec2.sh"},
    @{Name="Perplexity Test Script"; File="test_perplexity_multiagent.py"}
)

$success = 0
$failed = 0

foreach ($item in $files) {
    Write-Host "Uploading: $($item.Name)..." -ForegroundColor Yellow
    
    $result = scp -i $KEY_PATH $item.File "${EC2_HOST}:~/Kaggle-competition-assist/$($item.File)" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Success" -ForegroundColor Green
        $success++
    } else {
        Write-Host "   Failed" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Upload Summary:" -ForegroundColor White
Write-Host "  Success: $success" -ForegroundColor Green
Write-Host "  Failed: $failed" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($failed -eq 0) {
    Write-Host "All files uploaded successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps on EC2:" -ForegroundColor Yellow
    Write-Host "  1. chmod +x fix_perplexity_ec2.sh"
    Write-Host "  2. ./fix_perplexity_ec2.sh"
    Write-Host "  3. python3 test_perplexity_multiagent.py"
    Write-Host ""
    
    $response = Read-Host "Open SSH connection now? (y/n)"
    if ($response -eq "y") {
        Write-Host "Connecting to EC2..." -ForegroundColor Cyan
        ssh -i $KEY_PATH $EC2_HOST
    }
} else {
    Write-Host "Some uploads failed. Please check and retry." -ForegroundColor Yellow
}
