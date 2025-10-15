# 🚀 Quick Deployment Guide - Next Steps After Creating AWS Instance

## ✅ You are here: AWS EC2 instance created

---

## 📋 Quick Summary (30 minutes total)

1. **Connect to EC2** (2 min)
2. **Run deployment script** (10 min)
3. **Configure .env** (2 min)
4. **Run services setup** (5 min)
5. **Test deployment** (10 min)

---

## 🎯 Step-by-Step Instructions

### Step 1: Get Your EC2 IP Address

1. Go to AWS Console → EC2 → Instances
2. Click on your instance
3. Copy the **Public IPv4 address** (e.g., `3.87.45.123`)

**Your EC2 IP:** `___________________` ← Write it down!

---

### Step 2: Connect to EC2 Instance

**On Windows (PowerShell):**
```powershell
# Navigate to where your .pem key is
cd ~\Downloads

# Connect to EC2
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
```

**If you get permission error on Windows:**
```powershell
icacls your-key.pem /inheritance:r
icacls your-key.pem /grant:r "%username%":"(R)"
```

✅ **Verification:** You should see `ubuntu@ip-xxx-xxx-xxx-xxx:~$`

---

### Step 3: Run Automated Deployment Script

```bash
# Download and run deployment script
wget https://raw.githubusercontent.com/YOUR-USERNAME/Kaggle-competition-assist/main/deployment_script.sh
chmod +x deployment_script.sh
./deployment_script.sh
```

This script will:
- ✅ Install Python 3.11
- ✅ Install Node.js and npm
- ✅ Install Nginx
- ✅ Clone your repository
- ✅ Set up virtual environment
- ✅ Install all dependencies
- ✅ Install Playwright browsers

**Time:** ~10 minutes

✅ **Verification:** Script completes without errors

---

### Step 4: Configure Environment Variables

**Option A: Transfer from Local Machine (Recommended)**

On your **local machine** (Windows PowerShell):
```powershell
# Navigate to your project
cd C:\Users\heman\Kaggle-competition-assist

# Copy .env to EC2
scp -i path\to\your-key.pem .env ubuntu@YOUR-EC2-IP:/home/ubuntu/Kaggle-competition-assist/.env
```

**Option B: Create Manually on EC2**

On **EC2 instance**:
```bash
cd /home/ubuntu/Kaggle-competition-assist
nano .env
```

Copy and paste from your local `.env` file, then:
- Change `ENVIRONMENT=development` to `ENVIRONMENT=production`
- Press `Ctrl+X`, then `Y`, then `Enter` to save

**⚠️ CRITICAL:** Make sure `ENVIRONMENT=production` (uses Groq instead of Ollama)

✅ **Verification:**
```bash
cat .env | grep ENVIRONMENT
# Should show: ENVIRONMENT=production
```

---

### Step 5: Set Up Services

```bash
cd /home/ubuntu/Kaggle-competition-assist
wget https://raw.githubusercontent.com/YOUR-USERNAME/Kaggle-competition-assist/main/setup_services.sh
chmod +x setup_services.sh
./setup_services.sh
```

This script will:
- ✅ Create backend systemd service
- ✅ Create frontend systemd service
- ✅ Configure Nginx reverse proxy
- ✅ Start all services
- ✅ Enable auto-restart

**Time:** ~2 minutes

✅ **Verification:** All services show "active (running)"

---

### Step 6: Test Your Deployment

#### 6.1 Test Health Endpoint

```bash
# On EC2
curl http://localhost:5000/health
```

Expected: `{"status": "healthy", ...}`

#### 6.2 Test Frontend Access

**Open in browser:** `http://YOUR-EC2-IP`

Expected: See Streamlit frontend with dark theme

#### 6.3 Test Query (The Big Test!)

1. Enter competition: `titanic`
2. Ask: `"What is the evaluation metric for Titanic?"`
3. Wait ~20-30 seconds for first response
4. Ask THE SAME question again
5. Response should come back in 1-3 seconds! ✅ **15x speedup!**

---

## 🎯 Success Criteria

Your deployment works exactly like local if:

✅ **Functional:**
- [ ] Health endpoint responds
- [ ] Frontend loads
- [ ] Queries return intelligent responses
- [ ] Cache speedup working (15x)

✅ **Performance:**
- [ ] First query: 20-30s (normal)
- [ ] Cached query: 1-3s (fast!)
- [ ] No timeout errors

✅ **Quality:**
- [ ] Responses same quality as local
- [ ] Code review detects data leakage
- [ ] Ideas generation gives specific suggestions

---

## 🐛 Troubleshooting

### Problem: Services won't start

```bash
# Check logs
sudo journalctl -u kaggle-backend -n 50
sudo journalctl -u kaggle-frontend -n 50

# Common fix: Reinstall dependencies
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kaggle-backend kaggle-frontend
```

### Problem: Frontend loads but queries fail

```bash
# Check backend is running
curl http://localhost:5000/health

# Check .env file exists
cat /home/ubuntu/Kaggle-competition-assist/.env | head -n 5

# Restart backend
sudo systemctl restart kaggle-backend
```

### Problem: Playwright errors

```bash
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
playwright install --with-deps
sudo systemctl restart kaggle-backend
```

### Problem: Out of memory

```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📊 Useful Commands

```bash
# View live backend logs
sudo journalctl -u kaggle-backend -f

# View live frontend logs
sudo journalctl -u kaggle-frontend -f

# Restart services
sudo systemctl restart kaggle-backend
sudo systemctl restart kaggle-frontend

# Check service status
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend
sudo systemctl status nginx

# Check what's using ports
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :8501

# Update application
cd /home/ubuntu/Kaggle-competition-assist
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kaggle-backend kaggle-frontend
```

---

## 🔒 Security Checklist

After deployment works:

1. **Restrict SSH access** (AWS Console → Security Groups)
   - Change SSH (port 22) from `0.0.0.0/0` to your IP only

2. **Monitor costs** (AWS Console → Billing)
   - Set up billing alert at $10/month
   - t3.micro is FREE with AWS Free Tier

3. **Backup ChromaDB** (Optional)
   ```bash
   # Manual backup
   tar -czf chromadb-backup.tar.gz /home/ubuntu/Kaggle-competition-assist/chroma_db
   ```

---

## ✅ Final Checklist

Before announcing your deployment:

- [ ] All queries work correctly
- [ ] Response quality = local version
- [ ] Cache speedup working (15x)
- [ ] No errors in logs
- [ ] SSH access restricted
- [ ] Billing alert set up
- [ ] Tested all 10 agents

---

## 🎉 You're Done!

**Your URLs:**
- **Frontend:** `http://YOUR-EC2-IP`
- **Health Check:** `http://YOUR-EC2-IP/health`

**Next Steps:**
1. ✅ Share URL with friends for testing
2. ✅ Monitor logs for first 24 hours
3. ✅ Collect feedback
4. ✅ Update LinkedIn/GitHub

---

## 📝 Testing Script

Run these queries to verify everything works:

### Query 1: Evaluation Metric
```
Competition: titanic
Query: What is the evaluation metric for Titanic?
Expected: Mentions accuracy/survival prediction
```

### Query 2: Cache Test
```
Ask SAME question as Query 1 again
Expected: 15x faster response (1-3s vs 20-30s)
```

### Query 3: Code Review
```
Competition: titanic
Query: Review my code: df['target_mean'] = df['target'].mean()
Expected: Detects data leakage, suggests fix
```

### Query 4: Ideas Generation
```
Competition: titanic  
Query: Give me ideas for Titanic competition
Expected: 3+ specific, competition-aware ideas
```

---

## 📞 Need Help?

1. **Check logs:**
   ```bash
   sudo journalctl -u kaggle-backend -n 100
   ```

2. **Check detailed testing guide:**
   See `DEPLOYMENT_TESTING_CHECKLIST.md`

3. **Verify AWS Security Groups:**
   - Port 22 (SSH): Your IP only
   - Port 80 (HTTP): 0.0.0.0/0
   - Port 443 (HTTPS): 0.0.0.0/0
   - Port 5000 (Backend): 0.0.0.0/0
   - Port 8501 (Frontend): 0.0.0.0/0

---

**🚀 Total Time: ~30 minutes from AWS instance creation to fully working deployment!**

**Good luck! You've got this! 💪**

