# 📤 Upload Deployment Scripts to GitHub

Before deploying, you need to push these new scripts to GitHub so they can be downloaded on EC2.

## Quick Steps:

### Option 1: Using Git Command Line

```powershell
# In your project directory
cd C:\Users\heman\Kaggle-competition-assist

# Add new files
git add deployment_script.sh
git add setup_services.sh
git add DEPLOYMENT_TESTING_CHECKLIST.md
git add DEPLOYMENT_QUICK_GUIDE.md
git add transfer_env_to_ec2.ps1

# Commit
git commit -m "Add AWS deployment automation scripts"

# Push to GitHub
git push origin main
```

### Option 2: Using VS Code / Cursor

1. Open Source Control panel (Ctrl+Shift+G)
2. Stage the new files (click + icon)
3. Enter commit message: "Add AWS deployment automation scripts"
4. Click ✓ Commit
5. Click "Sync Changes" or "Push"

---

## Files to Upload:

- ✅ `deployment_script.sh` - Main installation script
- ✅ `setup_services.sh` - Service configuration script
- ✅ `DEPLOYMENT_TESTING_CHECKLIST.md` - Comprehensive testing guide
- ✅ `DEPLOYMENT_QUICK_GUIDE.md` - Quick reference guide
- ✅ `transfer_env_to_ec2.ps1` - Windows script to transfer .env

---

## After Pushing:

Verify on GitHub:
1. Go to https://github.com/YOUR-USERNAME/Kaggle-competition-assist
2. Check that all 5 files appear in the repository
3. Click on `deployment_script.sh` and verify you can see the "Raw" button

---

## Alternative: Manual Upload to EC2

If you don't want to push to GitHub, you can transfer files directly:

```powershell
# From local machine (Windows PowerShell)
cd C:\Users\heman\Kaggle-competition-assist

# Transfer deployment script
scp -i path\to\your-key.pem deployment_script.sh ubuntu@YOUR-EC2-IP:/home/ubuntu/

# Transfer setup script
scp -i path\to\your-key.pem setup_services.sh ubuntu@YOUR-EC2-IP:/home/ubuntu/

# Then on EC2, make executable:
chmod +x deployment_script.sh setup_services.sh
```

---

**Recommended:** Use GitHub (Option 1) for cleaner deployment process.

