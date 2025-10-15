# ✅ AWS Deployment Checklist - Print This!

## 📋 Quick Reference Checklist

**Date Started:** ___________  
**EC2 IP Address:** ___________________  
**Completion Time:** ___________

---

## Step 1: Push to GitHub (5 min)
```bash
cd C:\Users\heman\Kaggle-competition-assist
git add .
git commit -m "Add AWS deployment automation"
git push origin main
```
- [ ] Scripts pushed to GitHub
- [ ] Verified on GitHub website

---

## Step 2: Connect to EC2 (2 min)
```bash
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
```
- [ ] Connected successfully
- [ ] See ubuntu@ip-xxx prompt

---

## Step 3: Run Deployment (10 min)
```bash
wget https://raw.githubusercontent.com/YOUR-USERNAME/Kaggle-competition-assist/main/deployment_script.sh
chmod +x deployment_script.sh
./deployment_script.sh
```
- [ ] Python 3.11 installed
- [ ] Node.js installed
- [ ] Nginx installed
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Playwright installed

---

## Step 4: Configure .env (2 min)

**Windows (Local Machine):**
```powershell
.\transfer_env_to_ec2.ps1
```

**OR Manually on EC2:**
```bash
nano /home/ubuntu/Kaggle-competition-assist/.env
```

- [ ] .env file created/transferred
- [ ] ENVIRONMENT=production ⚠️
- [ ] All API keys present
- [ ] Verified with: `cat .env | grep ENVIRONMENT`

---

## Step 5: Setup Services (5 min)
```bash
cd /home/ubuntu/Kaggle-competition-assist
wget https://raw.githubusercontent.com/YOUR-USERNAME/Kaggle-competition-assist/main/setup_services.sh
chmod +x setup_services.sh
./setup_services.sh
```
- [ ] Backend service created
- [ ] Frontend service created
- [ ] Nginx configured
- [ ] All services "active (running)"

---

## Step 6: Test Deployment (5 min)

### Test 1: Health Check
```bash
curl http://localhost:5000/health
```
- [ ] Returns {"status": "healthy"}

### Test 2: Frontend
**Browser:** `http://YOUR-EC2-IP`
- [ ] Frontend loads
- [ ] Dark theme displays
- [ ] No console errors

### Test 3: Query Test
**Query:** "What is the evaluation metric for Titanic?"
- [ ] First response: 20-30s
- [ ] Response is intelligent
- [ ] Ask SAME question again
- [ ] Second response: 1-3s ✅ **15x speedup!**

### Test 4: Code Review
**Query:** "Review my code: df['target_mean'] = df['target'].mean()"
- [ ] Detects data leakage
- [ ] Suggests fix
- [ ] Quality = local version

---

## ✅ Final Verification

- [ ] All 4 test queries pass
- [ ] Performance matches local
- [ ] No errors in logs
- [ ] Cache working (15x speedup)
- [ ] All 10 agents responding

---

## 🎉 Success!

**Live URLs:**
- Frontend: `http://___________________`
- Health: `http://___________________/health`

**Deployment Time:** _______ minutes

---

## 🐛 Quick Troubleshooting

### Services not starting:
```bash
sudo journalctl -u kaggle-backend -n 50
sudo systemctl restart kaggle-backend kaggle-frontend
```

### Frontend can't reach backend:
```bash
curl http://localhost:5000/health
cat .env | grep ENVIRONMENT
sudo systemctl restart kaggle-backend
```

### Playwright errors:
```bash
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
playwright install --with-deps
sudo systemctl restart kaggle-backend
```

---

## 📊 Useful Commands

```bash
# View logs
sudo journalctl -u kaggle-backend -f
sudo journalctl -u kaggle-frontend -f

# Restart services
sudo systemctl restart kaggle-backend
sudo systemctl restart kaggle-frontend

# Check status
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend
```

---

## 🔒 Security (After Testing)

- [ ] Restrict SSH to your IP only (AWS Console)
- [ ] Set up billing alert ($10/month)
- [ ] Verify .env not exposed

---

**📱 Screenshot this page for quick reference!**

