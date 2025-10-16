# 🚀 Deployment Steps - Execute Now

**Status:** All files fixed locally, ready to upload  
**Time Required:** 5 minutes  
**Goal:** Get backend running on EC2

---

## 📋 **Quick Steps Overview**

1. Upload fixed files to EC2 (2 min)
2. Restart backend service (1 min)
3. Verify it's working (2 min)

---

## 🎯 **STEP 1: Upload Fixed Files**

### Option A: Use PowerShell Script (Easiest)

Open PowerShell in this directory and run:

```powershell
.\DEPLOY_FIX_NOW.ps1
```

This will:
- Prompt for your EC2 IP address
- Prompt for your SSH key path
- Upload all fixed files automatically
- Give you the next commands to run

### Option B: Manual Upload

If you prefer manual control:

```powershell
# Replace with your details
$EC2_IP = "your-ec2-ip-here"
$KEY = "path/to/your/key.pem"

# Upload fixed files
scp -i $KEY llms/llm_loader.py ubuntu@${EC2_IP}:~/Kaggle-competition-assist/llms/
scp -i $KEY llms/model_registry.py ubuntu@${EC2_IP}:~/Kaggle-competition-assist/llms/
scp -i $KEY tests/test_working_llms.py ubuntu@${EC2_IP}:~/Kaggle-competition-assist/tests/
```

---

## 🔌 **STEP 2: SSH to EC2**

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

---

## ✅ **STEP 3: Verify and Restart**

Once connected to EC2, choose one option:

### Option A: Quick Restart (Fastest)

```bash
cd ~/Kaggle-competition-assist
source venv/bin/activate
sudo systemctl restart kaggle-backend
sleep 5
curl http://localhost:5000/health
```

**Expected Output:**
```json
{"status": "healthy"}
```

### Option B: Full Verification (Recommended)

Copy and paste the entire contents of `ec2_verification_commands.sh` into your EC2 terminal.

This will:
1. Test all imports ✅
2. Restart the backend ✅
3. Check service status ✅
4. Test health endpoint ✅
5. Show you the results ✅

---

## 🎉 **SUCCESS INDICATORS**

You'll know it's working when you see:

```bash
✅ ComponentOrchestrator
✅ CompetitionSummaryAgent
✅ Kaggle API Client
✅ LLM Loader
✅ ChromaDB RAG Pipeline

🎉 ALL IMPORTS SUCCESSFUL!

● kaggle-backend.service - Kaggle Copilot Backend
     Active: active (running)

✅ BACKEND IS HEALTHY AND READY!
```

---

## ❌ **If Something Goes Wrong**

### 1. Check Logs
```bash
sudo journalctl -u kaggle-backend -n 50 --no-pager
```

### 2. Test Imports Manually
```bash
cd ~/Kaggle-competition-assist
source venv/bin/activate
python -c "from llms.llm_loader import get_llm_from_config; print('OK')"
```

### 3. Run Backend Manually (See Errors)
```bash
cd ~/Kaggle-competition-assist
source venv/bin/activate
python minimal_backend.py
```

Press Ctrl+C to stop, then restart the service:
```bash
sudo systemctl start kaggle-backend
```

---

## 🧪 **Test Your Backend**

After it's running, test with a real query:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "competition_id": "titanic",
    "user_query": "What is this competition about?"
  }'
```

---

## 📊 **Monitoring Commands**

### Check if service is running:
```bash
sudo systemctl status kaggle-backend
```

### Watch logs in real-time:
```bash
sudo journalctl -u kaggle-backend -f
```

### Check memory usage:
```bash
free -h
ps aux | grep python
```

### Check port 5000:
```bash
sudo netstat -tlnp | grep 5000
```

---

## 🔧 **Service Management**

### Start:
```bash
sudo systemctl start kaggle-backend
```

### Stop:
```bash
sudo systemctl stop kaggle-backend
```

### Restart:
```bash
sudo systemctl restart kaggle-backend
```

### Enable auto-start on boot:
```bash
sudo systemctl enable kaggle-backend
```

### Disable auto-start:
```bash
sudo systemctl disable kaggle-backend
```

---

## 🌐 **Next Steps After Deployment**

### 1. Configure Security Group (AWS Console)
- Allow inbound traffic on port 5000 (or your chosen port)
- Restrict to specific IP addresses if needed

### 2. Set Up Nginx (Optional, for production)
```bash
sudo apt install nginx
# Configure nginx to proxy to localhost:5000
```

### 3. Set Up SSL/HTTPS (Optional)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx
```

### 4. Configure Domain Name (Optional)
- Point your domain's A record to EC2 IP
- Update nginx configuration

### 5. Set Up Monitoring
- CloudWatch for AWS metrics
- Application-level logging
- Error tracking (e.g., Sentry)

---

## 📞 **Support**

If you encounter issues:

1. **Check the logs first** - they'll tell you exactly what's wrong
2. **Verify environment variables** - make sure `.env` file is correct
3. **Check disk space** - `df -h`
4. **Check memory** - `free -h`
5. **Verify Python version** - `python --version` (should be 3.11.x)

---

## ✅ **Checklist**

- [ ] Files uploaded to EC2
- [ ] SSH connected to EC2
- [ ] Backend restarted
- [ ] Health endpoint responding
- [ ] All imports working
- [ ] Test query successful
- [ ] Logs clean (no errors)
- [ ] Service auto-starts on boot

---

## 🎊 **You're Ready!**

Once the health endpoint returns success, your Kaggle Copilot backend is **fully deployed and operational**!

**Your backend can now:**
- ✅ Accept user queries
- ✅ Scrape Kaggle competitions
- ✅ Retrieve from vector database
- ✅ Generate AI responses
- ✅ Execute multi-agent workflows
- ✅ Handle production traffic

**Congratulations on your deployment!** 🚀


