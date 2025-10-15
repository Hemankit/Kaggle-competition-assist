# 🚀 DEPLOYMENT IN PROGRESS - COPY/PASTE THESE COMMANDS

**GitHub Username:** ✅ `Hemankit` (UPDATED!)  
**Status:** READY TO DEPLOY  
**Time:** ~30 minutes

---

## 📤 STEP 1: PUSH TO GITHUB (DO THIS NOW - 2 MIN)

**Copy and paste these commands in PowerShell:**

```powershell
cd C:\Users\heman\Kaggle-competition-assist

# Stage all files
git add .

# Commit with clear message
git commit -m "Production deployment ready - AWS EC2 automation complete"

# Push to GitHub
git push origin main
```

**After pushing, verify:**
1. Go to https://github.com/Hemankit/Kaggle-competition-assist
2. Confirm you see: `deployment_script.sh`, `setup_services.sh`, `DEPLOYMENT_NOW.md`
3. ✅ If you see them, proceed to Step 2!

---

## 🖥️ STEP 2: CONNECT TO YOUR AWS EC2 INSTANCE (5 MIN)

### Get Your EC2 IP Address:
1. Go to AWS Console → EC2 → Instances
2. Find your instance
3. Copy the **Public IPv4 address**
4. Write it here: `_____________________`

### Connect via SSH:

**In PowerShell:**
```powershell
# Navigate to where your .pem key is (probably Downloads)
cd C:\Users\heman\Downloads

# Fix key permissions (Windows security requirement)
icacls "Key__2__Success.pem" /inheritance:r
icacls "Key__2__Success.pem" /grant:r "heman:(R)"

# Connect to EC2 (replace YOUR-EC2-IP with the IP you copied above)
ssh -i Key__2__Success.pem ubuntu@YOUR-EC2-IP
```

**Expected result:**
```
ubuntu@ip-172-31-xx-xx:~$
```

✅ **If you see this prompt, you're connected!**

---

## 🚀 STEP 3: RUN AUTOMATED DEPLOYMENT ON EC2 (15 MIN)

**Copy and paste these commands ON YOUR EC2 INSTANCE:**

### 3A. Download and Run Deployment Script

```bash
# Download the deployment script from YOUR GitHub
wget https://raw.githubusercontent.com/Hemankit/Kaggle-competition-assist/main/deployment_script.sh

# Make it executable
chmod +x deployment_script.sh

# Run it! (This takes ~10-15 minutes)
./deployment_script.sh
```

**What this does (all automatic):**
- ✅ Updates Ubuntu
- ✅ Installs Python 3.11
- ✅ Installs Node.js 20
- ✅ Installs Nginx
- ✅ Installs system dependencies
- ✅ Clones your GitHub repo
- ✅ Creates Python virtual environment
- ✅ Installs all Python packages
- ✅ Installs Playwright browsers

**Just wait and watch the progress!** ⏳

When it finishes, you'll see:
```
✅ Base installation complete!

⚠️  NEXT STEPS (MANUAL):
1. Create .env file: nano /home/ubuntu/Kaggle-competition-assist/.env
2. Copy your API keys from local .env to server .env
3. Run the service setup script: ./setup_services.sh
```

---

### 3B. Transfer Your .env File

**IMPORTANT:** Keep your EC2 SSH connection open!

**Open a NEW PowerShell window on your Windows machine:**

```powershell
cd C:\Users\heman\Kaggle-competition-assist

# Run the automated transfer script
.\transfer_env_to_ec2.ps1
```

**The script will ask you:**
1. EC2 IP address → Enter the IP you copied earlier
2. Path to .pem key → Enter: `C:\Users\heman\Downloads\Key__2__Success.pem`

**The script automatically:**
- ✅ Changes ENVIRONMENT from "development" to "production"
- ✅ Transfers .env securely via SCP
- ✅ Verifies the transfer worked

**Alternative (Manual Method):**

If the script doesn't work, do this on EC2:
```bash
cd /home/ubuntu/Kaggle-competition-assist
nano .env
```

Copy your entire `.env` file content from Windows, BUT change line 2 to:
```
ENVIRONMENT=production
```

Save with: `Ctrl+X`, then `Y`, then `Enter`

**Verify the .env file:**
```bash
cat .env | grep ENVIRONMENT
# Should show: ENVIRONMENT=production
```

✅ **If you see "ENVIRONMENT=production", continue!**

---

### 3C. Setup Services (Final Step!)

**Back on your EC2 SSH connection:**

```bash
cd /home/ubuntu/Kaggle-competition-assist

# Download service setup script
wget https://raw.githubusercontent.com/Hemankit/Kaggle-competition-assist/main/setup_services.sh

# Make executable
chmod +x setup_services.sh

# Run it!
./setup_services.sh
```

**This script (takes ~2-3 minutes):**
- ✅ Creates backend systemd service
- ✅ Creates frontend systemd service
- ✅ Configures Nginx reverse proxy
- ✅ Starts all services
- ✅ Enables auto-restart on crash

**Expected output:**
```
✅ Setup complete!

🌐 Your application is now running at:
   Frontend: http://YOUR-EC2-IP
   Backend Health: http://YOUR-EC2-IP/health

📋 Useful commands:
   View backend logs: sudo journalctl -u kaggle-backend -f
   View frontend logs: sudo journalctl -u kaggle-frontend -f
```

🎉 **IF YOU SEE THIS, YOUR APP IS LIVE!**

---

## ✅ STEP 4: VERIFY IT WORKS (5 MIN)

### Test 1: Health Check (On EC2)

```bash
curl http://localhost:5000/health
```

**Expected:**
```json
{"status":"healthy","timestamp":"2025-10-15T..."}
```

✅ **If you see this, backend is running!**

---

### Test 2: Frontend Access (In Your Browser)

**Open your browser and go to:**
```
http://YOUR-EC2-IP
```

**You should see:**
- 🌙 Beautiful dark theme UI
- 🎯 "Initialize Session" form
- ✅ Backend Connected (green) in sidebar
- 🧠 "Kaggle Copilot Assistant" header

✅ **If you see the UI, frontend is working!**

---

### Test 3: Full Functionality Test

**In the browser UI:**

1. **Initialize Session:**
   - Kaggle Username: `hemankit`
   - Competition: `titanic`
   - Click "🚀 Initialize Session"
   - Wait ~10 seconds
   - Should show "Session initialized successfully!" ✅

2. **First Query (Tests Multi-Agent System):**
   ```
   What is the evaluation metric for Titanic?
   ```
   - Click "🚀 Send Query"
   - Wait 20-30 seconds (this is normal!)
   - Should get intelligent response about accuracy/classification
   - Response should be detailed and competition-specific

3. **🔥 CRITICAL TEST - Cache Speedup:**
   - Ask the **EXACT SAME** question again:
   ```
   What is the evaluation metric for Titanic?
   ```
   - **Should respond in 1-3 seconds!** 🚀
   - **This proves your cache is working = 15x speedup!**

4. **Code Review Test:**
   ```
   Review my code: df['target_mean'] = df['target'].mean()
   ```
   - Should detect data leakage issue
   - Should suggest using train data only
   - Should explain why it's wrong

**If all 4 tests pass:**
```
╔════════════════════════════════════════╗
║  🎉 DEPLOYMENT SUCCESSFUL! 🎉          ║
║                                        ║
║  Your Kaggle Copilot is LIVE on AWS!  ║
╚════════════════════════════════════════╝
```

---

## 📊 MONITOR YOUR DEPLOYMENT

### View Live Logs (On EC2):

```bash
# Backend logs (live)
sudo journalctl -u kaggle-backend -f

# Frontend logs (live)
sudo journalctl -u kaggle-frontend -f

# Press Ctrl+C to stop viewing logs
```

### Check Service Status:

```bash
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend
sudo systemctl status nginx
```

All should show: `Active: active (running)`

---

## 🐛 TROUBLESHOOTING

### Issue: Services Not Starting

```bash
# Check what went wrong
sudo journalctl -u kaggle-backend -n 100 --no-pager

# Try reinstalling dependencies
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo systemctl restart kaggle-backend kaggle-frontend
```

### Issue: Out of Memory

```bash
# t3.micro has only 1GB RAM, add swap space:
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify swap is active
free -h
```

### Issue: Playwright Errors

```bash
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
playwright install --with-deps
sudo systemctl restart kaggle-backend
```

### Issue: Frontend Can't Reach Backend

```bash
# Verify backend is actually running
curl http://localhost:5000/health

# Check .env has production mode
cat /home/ubuntu/Kaggle-competition-assist/.env | grep ENVIRONMENT

# Restart everything
sudo systemctl restart kaggle-backend kaggle-frontend nginx
```

---

## 🔒 SECURITY (DO THIS AFTER TESTING!)

### 1. Restrict SSH Access

**AWS Console → EC2 → Security Groups:**
1. Find your security group
2. Edit inbound rules
3. Find SSH (port 22) rule
4. Change source from `0.0.0.0/0` to `My IP` (or manually enter `YOUR.IP.ADDRESS/32`)
5. Save rules

This restricts SSH to only your IP address!

### 2. Set Up Billing Alert

**AWS Console → Billing & Cost Management → Budgets:**
1. Create budget
2. Budget name: "Monthly Budget"
3. Amount: $10.00
4. Alert threshold: 80% ($8.00)
5. Add your email
6. Create budget

You'll get email alerts if costs exceed $8!

---

## 🎉 CELEBRATE & SHARE!

### Update Your README:

**On your local machine:**
```powershell
cd C:\Users\heman\Kaggle-competition-assist
# Edit README.md and update line 223 to:
# **Live Demo:** http://YOUR-EC2-IP
git add README.md
git commit -m "Add live demo URL"
git push origin main
```

### Share on LinkedIn:

```
🚀 Just deployed my Kaggle Competition Assistant to AWS!

✨ What it does:
• 10 specialized AI agents for Kaggle competition strategy
• 15x faster with smart caching (25s → 1.5s)
• Multi-model LLM architecture (Groq, Gemini, Perplexity, Ollama)
• Real-time competition data scraping with Playwright
• Beautiful dark theme UI built with Streamlit

🔧 Tech Stack:
Python, Flask, Streamlit, LangChain, CrewAI, AutoGen, LangGraph, ChromaDB
Deployed on AWS EC2 with Nginx + systemd for production reliability

🎯 Why I built this:
ChatGPT loses context and gives generic advice. This tool provides 
competition-specific guidance, tracks progress, and integrates with 
Kaggle's ecosystem for targeted insights.

📊 Performance:
- First query: ~25s (multi-agent processing)
- Cached queries: 1-2s (15x speedup!)
- 10 specialized agents working together
- RAG pipeline with ChromaDB for intelligent context

Try it live: http://YOUR-EC2-IP

Check out the code: https://github.com/Hemankit/Kaggle-competition-assist

#MachineLearning #AWS #Kaggle #AI #Python #DeepLearning #LLM #DataScience
```

---

## 📋 QUICK REFERENCE COMMANDS

### Service Management:
```bash
sudo systemctl restart kaggle-backend      # Restart backend
sudo systemctl restart kaggle-frontend     # Restart frontend
sudo systemctl status kaggle-backend       # Check backend status
```

### View Logs:
```bash
sudo journalctl -u kaggle-backend -f       # Live backend logs
sudo journalctl -u kaggle-backend -n 100   # Last 100 lines
```

### Update Application:
```bash
cd /home/ubuntu/Kaggle-competition-assist
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kaggle-backend kaggle-frontend
```

### Check What's Running:
```bash
sudo netstat -tulpn | grep :5000    # Backend (Flask)
sudo netstat -tulpn | grep :8501    # Frontend (Streamlit)
sudo netstat -tulpn | grep :80      # Nginx
```

---

## ✅ COMPLETION CHECKLIST

**Deployment:**
- [ ] Pushed code to GitHub
- [ ] Connected to EC2 via SSH
- [ ] Ran deployment_script.sh
- [ ] Transferred .env file (ENVIRONMENT=production)
- [ ] Ran setup_services.sh
- [ ] All services showing "active (running)"

**Verification:**
- [ ] Health check works (curl returns JSON)
- [ ] Frontend loads in browser
- [ ] Session initializes successfully
- [ ] First query works (~25s)
- [ ] Cache test works (1-3s = 15x faster!)
- [ ] Code review detects data leakage

**Post-Deployment:**
- [ ] Restricted SSH to my IP only
- [ ] Set up AWS billing alert ($10/month)
- [ ] Updated README with live URL
- [ ] Shared on LinkedIn
- [ ] Monitoring logs for stability

---

**🎯 Your live URLs:**
- Frontend: `http://YOUR-EC2-IP`
- Health Check: `http://YOUR-EC2-IP/health`
- Backend API: `http://YOUR-EC2-IP/api/*`

**💪 You've got this! Follow the steps above and you'll be live in 30 minutes!**

