# 🔧 Deployment Troubleshooting Guide

## Problem: Deployed App Returns Placeholder Responses

### Symptom
When you ask "What is the evaluation metric?" for a competition, you get:
```
Metric: Check competition description
Evaluation Details: Check the competition page for detailed evaluation criteria.
```

Instead of actual competition data like:
```
Metric: Accuracy
This competition uses classification accuracy to evaluate submissions...
```

---

## Root Causes & Solutions

### 🎯 Most Common Issue: Playwright Browsers Not Installed

**Why this happens:**
- Playwright requires browser binaries (Chromium, Firefox, WebKit)
- Installing the Python package alone is NOT enough
- Without browsers, web scraping fails silently
- The app returns placeholder data instead of scraped data

**How to fix:**
```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Navigate to project
cd /home/ubuntu/Kaggle-competition-assist

# Activate virtual environment
source venv/bin/activate

# Install Playwright browsers (CRITICAL!)
playwright install --with-deps chromium

# Restart backend service
sudo systemctl restart kaggle-backend

# Wait 30 seconds for service to fully restart
sleep 30

# Test it
curl http://localhost:5000/health
```

**Verification:**
```bash
# Check if Playwright is working
playwright --version

# Should output: Version 1.41.0 (or similar)
```

---

## 🚀 Quick Fix: Automated Script

We've created a comprehensive fix script that addresses all common issues:

```bash
# On your EC2 instance
cd /home/ubuntu/Kaggle-competition-assist

# Make scripts executable
chmod +x fix_ec2_deployment.sh
chmod +x diagnose_deployment.sh

# First, diagnose the issue
./diagnose_deployment.sh

# Then run the automated fix
./fix_ec2_deployment.sh
```

The fix script will:
1. ✅ Reinstall all Python dependencies
2. ✅ Install Playwright browsers with system dependencies
3. ✅ Verify environment variables
4. ✅ Create required directories
5. ✅ Restart services with proper configuration
6. ✅ Test backend health endpoint

---

## 🔍 Diagnostic Checklist

Run through this checklist to identify the exact issue:

### 1. Check if Backend is Running
```bash
sudo systemctl status kaggle-backend
```

**Expected:** `Active: active (running)`
**If not running:**
```bash
sudo systemctl start kaggle-backend
sudo journalctl -u kaggle-backend -n 50
```

### 2. Check Backend Logs for Errors
```bash
sudo journalctl -u kaggle-backend -n 100 | grep -i error
```

**Common errors to look for:**
- `playwright._impl._api_types.Error: Executable doesn't exist` → Playwright browsers not installed
- `ModuleNotFoundError` → Missing Python dependencies
- `API key not found` → Environment variables not set
- `Permission denied` → File permissions issue

### 3. Test Backend Health
```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T...",
  "version": "1.0.0"
}
```

### 4. Check Environment Variables
```bash
cat /home/ubuntu/Kaggle-competition-assist/.env | grep -E "KAGGLE|GROQ|GOOGLE"
```

**Must have:**
- `KAGGLE_USERNAME` (not placeholder)
- `KAGGLE_KEY` (not placeholder)
- `GROQ_API_KEY` (not placeholder)
- `GOOGLE_API_KEY` (not placeholder)
- `ENVIRONMENT=production`

### 5. Verify Python Dependencies
```bash
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
python -c "import playwright; print('Playwright OK')"
python -c "from orchestrators.component_orchestrator import ComponentOrchestrator; print('Orchestrator OK')"
python -c "from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline; print('ChromaDB OK')"
```

All should print "OK" without errors.

### 6. Test Playwright Browsers
```bash
source venv/bin/activate
playwright --version
```

**If command not found or error:**
```bash
pip install playwright
playwright install --with-deps chromium
```

### 7. Check Port Accessibility
```bash
netstat -tuln | grep -E '5000|8501'
```

**Should show:**
- Port 5000 (backend) LISTENING
- Port 8501 (frontend) LISTENING

### 8. Test Actual Query
```bash
curl -X POST http://localhost:5000/session/new \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the evaluation metric?", "competition_slug": "titanic", "user_id": "test"}' \
  --max-time 30
```

**If you see "Check competition description"** → Main issue confirmed
**If you see actual accuracy/metrics data** → Working correctly!

---

## 🐛 Common Issues & Fixes

### Issue 1: Playwright Executable Missing
**Error in logs:**
```
playwright._impl._api_types.Error: Executable doesn't exist at /home/ubuntu/.cache/ms-playwright/chromium-1097/chrome-linux/chrome
```

**Fix:**
```bash
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
playwright install --with-deps chromium
sudo systemctl restart kaggle-backend
```

---

### Issue 2: Missing Environment Variables
**Symptom:** Backend starts but returns generic errors

**Fix:**
```bash
# Edit .env file
nano /home/ubuntu/Kaggle-competition-assist/.env

# Add your actual API keys:
ENVIRONMENT=production
KAGGLE_USERNAME=your-actual-username
KAGGLE_KEY=your-actual-key
GROQ_API_KEY=your-groq-key
GOOGLE_API_KEY=your-google-key
DEEPSEEK_API_KEY=your-deepseek-key
HUGGINGFACEHUB_API_TOKEN=your-hf-token

# Save and restart
sudo systemctl restart kaggle-backend
```

---

### Issue 3: Services Not Starting
**Check logs:**
```bash
sudo journalctl -u kaggle-backend -n 100 --no-pager
```

**Common fixes:**

**a) Port already in use:**
```bash
# Find process using port 5000
sudo netstat -tulpn | grep :5000
# Kill it if needed
sudo kill <PID>
# Restart service
sudo systemctl start kaggle-backend
```

**b) Permission issues:**
```bash
# Fix ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/Kaggle-competition-assist
# Restart
sudo systemctl restart kaggle-backend
```

**c) Missing dependencies:**
```bash
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kaggle-backend
```

---

### Issue 4: Slow or Timeout Responses
**Symptom:** First query takes >60 seconds or times out

**Causes:**
1. EC2 instance too small (needs at least t3.medium)
2. Scraping taking too long
3. LLM API rate limits

**Fixes:**
```bash
# 1. Add swap memory (if instance has <4GB RAM)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 2. Check instance resources
htop
free -h
df -h

# 3. Upgrade to larger instance if needed (t3.medium recommended)
```

---

### Issue 5: ChromaDB Cache Not Working
**Symptom:** Queries always slow, no speedup on repeated queries

**Check ChromaDB:**
```bash
ls -la /home/ubuntu/Kaggle-competition-assist/chroma_db/
```

**Should contain:**
- `chroma.sqlite3` file
- UUID directories with data

**Fix:**
```bash
# Ensure directory exists and has correct permissions
mkdir -p /home/ubuntu/Kaggle-competition-assist/chroma_db
chmod -R 755 /home/ubuntu/Kaggle-competition-assist/chroma_db

# Restart backend
sudo systemctl restart kaggle-backend
```

---

### Issue 6: Frontend Loads but Can't Connect to Backend
**Symptom:** Frontend UI loads but queries fail with "Network Error"

**Check Nginx configuration:**
```bash
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/kaggle-copilot
```

**Ensure proxy_pass is correct:**
```nginx
location /api/ {
    proxy_pass http://localhost:5000/;
    ...
}
```

**Restart Nginx:**
```bash
sudo systemctl restart nginx
```

**Check backend is reachable:**
```bash
curl http://localhost:5000/health
```

---

## 📊 Performance Expectations

### First Query (No Cache)
- **Time:** 20-30 seconds
- **Why:** Scraping competition page + LLM processing
- **Normal behavior:** This is expected for cold starts

### Cached Query (Same question)
- **Time:** 1-3 seconds
- **Why:** Data retrieved from ChromaDB cache
- **Speedup:** ~15x faster! 🚀

### If Different from Above
- First query >60s → Instance too small or missing dependencies
- Cached query >10s → ChromaDB not working or not activated

---

## 🎯 Verification: Working vs Not Working

### ✅ WORKING (What you should see)

**Query:** "What is the evaluation metric for Titanic?"

**Response:**
```
📊 Evaluation Metric for titanic

🎯 How Your Submission Will Be Scored:

Metric: Classification Accuracy
This competition evaluates submissions based on accuracy - the percentage 
of passengers you correctly predict as surviving or not surviving.

Formula: (Number of Correct Predictions) / (Total Predictions)

📋 Evaluation Details:
Your submission file should contain exactly 418 entries plus a header row.
Each entry should predict 0 (did not survive) or 1 (survived).
```

### ❌ NOT WORKING (Placeholder response)

**Query:** "What is the evaluation metric for Titanic?"

**Response:**
```
📊 Evaluation Metric for titanic

🎯 How Your Submission Will Be Scored:

Metric: Check competition description
Competition: titanic
Category: Not specified
Deadline: Not specified

📋 Evaluation Details: Check the competition page for detailed evaluation criteria.
```

**If you see the second response → Scraping is not working!**

---

## 🔄 Complete Reset Procedure

If nothing else works, do a complete reset:

```bash
# 1. Stop services
sudo systemctl stop kaggle-backend kaggle-frontend

# 2. Backup .env file (contains your API keys!)
cp /home/ubuntu/Kaggle-competition-assist/.env ~/env_backup

# 3. Remove and reclone
cd /home/ubuntu
rm -rf Kaggle-competition-assist
git clone https://github.com/YOUR-USERNAME/Kaggle-competition-assist.git

# 4. Restore .env
cp ~/env_backup Kaggle-competition-assist/.env

# 5. Run fix script
cd Kaggle-competition-assist
chmod +x fix_ec2_deployment.sh
./fix_ec2_deployment.sh

# 6. Verify
./diagnose_deployment.sh
```

---

## 📞 Getting Help

If you've tried everything and it's still not working:

### 1. Run Diagnostic Script and Save Output
```bash
./diagnose_deployment.sh > diagnostic_output.txt 2>&1
cat diagnostic_output.txt
```

### 2. Check Logs
```bash
# Last 100 lines of backend logs
sudo journalctl -u kaggle-backend -n 100 --no-pager > backend_logs.txt

# Last 100 lines of frontend logs
sudo journalctl -u kaggle-frontend -n 100 --no-pager > frontend_logs.txt
```

### 3. Get System Info
```bash
# Instance details
cat /proc/cpuinfo | grep "model name" | head -1
free -h
df -h
uname -a
```

### 4. Provide This Information
- Diagnostic output
- Backend logs (last 100 lines)
- EC2 instance type (e.g., t2.micro, t3.medium)
- Specific error message you're seeing

---

## ✅ Success Criteria

Your deployment is working correctly when:

1. ✅ `./diagnose_deployment.sh` passes all tests
2. ✅ Query "What is the evaluation metric?" returns actual metrics
3. ✅ First query: 20-30 seconds (acceptable)
4. ✅ Second query (same): 1-3 seconds (15x speedup!)
5. ✅ No errors in `sudo journalctl -u kaggle-backend -n 50`
6. ✅ Frontend loads and connects to backend
7. ✅ Code review works ("Review my code: df['target_mean'] = df['target'].mean()")
8. ✅ Ideas generation works ("Give me ideas for Titanic")

---

## 🎉 Next Steps After Fix

Once everything is working:

1. **Test thoroughly** with different competitions
2. **Monitor logs** for first 24 hours
3. **Set up monitoring** (optional: CloudWatch)
4. **Share with users** and gather feedback
5. **Iterate and improve** based on usage

---

**Last Updated:** October 15, 2025

**Quick Commands Reference:**
```bash
# Diagnose
./diagnose_deployment.sh

# Fix
./fix_ec2_deployment.sh

# View logs
sudo journalctl -u kaggle-backend -f

# Restart
sudo systemctl restart kaggle-backend kaggle-frontend

# Check status
sudo systemctl status kaggle-backend
```


