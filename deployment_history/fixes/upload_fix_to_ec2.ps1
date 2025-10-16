# PowerShell Script to Upload Fix Scripts to EC2
# ===================================================================
# This script uploads the deployment fix files to your EC2 instance
# Run this from your Windows machine (PowerShell)
# ===================================================================

Write-Host "=========================================="
Write-Host "EC2 Deployment Fix - File Upload Script"
Write-Host "=========================================="
Write-Host ""

# Configuration - UPDATED WITH YOUR VALUES!
$EC2_KEY_PATH = "C:\Users\heman\Downloads\Key__2__Success.pem"
$EC2_IP = "18.219.148.57"
$EC2_USER = "ubuntu"
$PROJECT_DIR = "/home/ubuntu/Kaggle-competition-assist"

# Check if key file exists
if (-not (Test-Path $EC2_KEY_PATH)) {
    Write-Host "ERROR: Key file not found at: $EC2_KEY_PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please update the EC2_KEY_PATH variable in this script with your actual .pem file path"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Key file: $EC2_KEY_PATH"
Write-Host "  EC2 IP: $EC2_IP"
Write-Host "  User: $EC2_USER"
Write-Host "  Destination: $PROJECT_DIR"
Write-Host ""

$continue = Read-Host "Is this correct? (y/n)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "Please edit this script and update the configuration at the top."
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host ""
Write-Host "Uploading files to EC2..." -ForegroundColor Yellow
Write-Host ""

# Files to upload
$files = @(
    "fix_ec2_deployment.sh",
    "diagnose_deployment.sh",
    "QUICK_FIX_GUIDE.md",
    "DEPLOYMENT_TROUBLESHOOTING.md",
    "EC2_FIX_README.md",
    "START_HERE_EC2_FIX.md"
)

$uploadedCount = 0
$failedCount = 0

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Uploading $file..." -ForegroundColor Green
        
        try {
            # Use scp to upload file
            $destination = "$EC2_USER@${EC2_IP}:$PROJECT_DIR/"
            & scp -i $EC2_KEY_PATH $file $destination 2>&1 | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Success" -ForegroundColor Green
                $uploadedCount++
            } else {
                Write-Host "  Failed" -ForegroundColor Red
                $failedCount++
            }
        }
        catch {
            Write-Host "  Error: $_" -ForegroundColor Red
            $failedCount++
        }
    }
    else {
        Write-Host "Warning: $file not found, skipping..." -ForegroundColor Yellow
        $failedCount++
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Upload Summary"
Write-Host "=========================================="
Write-Host "Files uploaded: $uploadedCount" -ForegroundColor Green

if ($failedCount -gt 0) {
    Write-Host "Files failed: $failedCount" -ForegroundColor Red
} else {
    Write-Host "Files failed: $failedCount" -ForegroundColor Green
}

Write-Host ""

if ($uploadedCount -gt 0) {
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. SSH to your EC2 instance:" -ForegroundColor White
    Write-Host "   ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_IP" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Navigate to project directory:" -ForegroundColor White
    Write-Host "   cd $PROJECT_DIR" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Make scripts executable:" -ForegroundColor White
    Write-Host "   chmod +x fix_ec2_deployment.sh diagnose_deployment.sh" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Run the fix script:" -ForegroundColor White
    Write-Host "   ./fix_ec2_deployment.sh" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Or diagnose first:" -ForegroundColor White
    Write-Host "   ./diagnose_deployment.sh" -ForegroundColor Gray
    Write-Host ""
    Write-Host "=========================================="
    Write-Host ""
    
    # Ask if user wants to SSH now
    $sshNow = Read-Host "Do you want to SSH to EC2 now? (y/n)"
    if ($sshNow -eq "y" -or $sshNow -eq "Y") {
        Write-Host ""
        Write-Host "Connecting to EC2..." -ForegroundColor Green
        & ssh -i $EC2_KEY_PATH "$EC2_USER@$EC2_IP"
    }
}
else {
    Write-Host "No files were uploaded successfully." -ForegroundColor Red
    Write-Host "Please check your EC2 key path and IP address." -ForegroundColor Red
}

Write-Host ""
Write-Host "Done!"
