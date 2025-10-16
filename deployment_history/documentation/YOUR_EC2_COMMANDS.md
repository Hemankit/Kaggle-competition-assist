# 🚀 Your EC2 Deployment Fix - Personal Command Reference

## ✅ Your Configuration
- **EC2 IP:** 18.219.148.57
- **Key File:** C:\Users\heman\Downloads\Key__2__Success.pem
- **Project Location:** /home/ubuntu/Kaggle-competition-assist

---

## 📤 Step 1: Upload Fix Scripts to EC2

### Option A: Use PowerShell Script (Easiest)
```powershell
cd C:\Users\heman\Kaggle-competition-assist
.\upload_fix_to_ec2.ps1
```

### Option B: Manual Upload
```powershell
cd C:\Users\heman\Kaggle-competition-assist

scp -i "C:\Users\heman\Downloads\Key__2__Success.pem" fix_ec2_deployment.sh ubuntu@18.219.148.57:/home/ubuntu/Kaggle-competition-assist/

scp -i "C:\Users\heman\Downloads\Key__2__Success.pem" diagnose_deployment.sh ubuntu@18.219.148.57:/home/ubuntu/Kaggle-competition-assist/
```

---

## 🔌 Step 2: Connect to EC2

```powershell
ssh -i "C:\Users\heman\Downloads\Key__2__Success.pem" ubuntu@18.219.148.57
```

---

## 🛠️ Step 3: Run Fix on EC2 (After SSH)

```bash
cd /home/ubuntu/Kaggle-competition-assist

# Make scripts executable
chmod +x fix_ec2_deployment.sh diagnose_deployment.sh

# Run the fix
./fix_ec2_deployment.sh
```

**Wait 5-10 minutes for the script to complete**

---

## 🧪 Step 4: Test Your App

### Check Backend Health
```bash
curl http://localhost:5000/health
```

**Expected:** `{"status": "healthy"}`

### Open in Browser
```
http://18.219.148.57
```

### Test Query
- **Competition:** titanic
- **Query:** What is the evaluation metric?

**Expected:** Real competition data (not placeholder!)

---

## 🔍 If Issues Occur

### Run Diagnostics
```bash
./diagnose_deployment.sh
```

### Check Logs
```bash
sudo journalctl -u kaggle-backend -n 50
```

### Restart Services
```bash
sudo systemctl restart kaggle-backend kaggle-frontend
```

### Check Service Status
```bash
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend
```

---

## 📊 Expected Results After Fix

✅ Backend returns real competition data
✅ First query: 20-30 seconds
✅ Cached query: 1-3 seconds (15x faster!)
✅ All agents working
✅ Code review working
✅ No errors in logs

---

## 🎯 Quick Troubleshooting

### If "Permission denied" on SSH:
```powershell
# Fix key permissions (run in PowerShell as Admin)
icacls "C:\Users\heman\Downloads\Key__2__Success.pem" /inheritance:r
icacls "C:\Users\heman\Downloads\Key__2__Success.pem" /grant:r "$($env:USERNAME):(R)"
```

### If services won't start:
```bash
sudo journalctl -u kaggle-backend -n 100
# Look for specific errors
```

### If still showing placeholder data:
```bash
# Reinstall Playwright browsers
source venv/bin/activate
playwright install --with-deps chromium
sudo systemctl restart kaggle-backend
```

---

## 🎉 Success Indicators

1. ✅ Health check responds: `curl http://localhost:5000/health`
2. ✅ Frontend loads: `http://18.219.148.57`
3. ✅ Real competition data in responses
4. ✅ Cached queries are fast (1-3 seconds)
5. ✅ No errors in logs

---

## 📞 Documentation Files

- **START_HERE_EC2_FIX.md** - Complete guide
- **QUICK_FIX_GUIDE.md** - 5-minute reference
- **DEPLOYMENT_TROUBLESHOOTING.md** - Detailed troubleshooting

---

**You've got this! Your deployment will be working in ~10 minutes!** 🚀


