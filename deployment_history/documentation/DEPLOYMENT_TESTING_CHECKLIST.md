# 🧪 Deployment Testing Checklist
## Ensuring Deployed Version = Local Version

---

## 📋 Pre-Deployment Verification

### 1. Local Environment Check
```bash
# On your local machine, test these queries and record responses

# Start local backend
python minimal_backend.py

# Start local frontend (in another terminal)
streamlit run streamlit_frontend/app.py

# Test these queries:
1. "What is the evaluation metric for Titanic?"
2. "Give me ideas for Titanic competition"
3. "Review my code: df['target_mean'] = df['target'].mean()"
```

**Record Results:**
- [ ] Query 1 response time: _____ seconds
- [ ] Query 2 response time: _____ seconds  
- [ ] Query 3 detects data leakage: YES / NO
- [ ] ChromaDB cache working: YES / NO
- [ ] All agents responding: YES / NO

---

## 🚀 Deployment Steps

### Step 1: Connect to EC2
```bash
# Replace with your actual key and IP
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR-EC2-IP
```

**Verification:**
- [ ] Successfully connected to EC2 instance

---

### Step 2: Run Deployment Script
```bash
# On EC2 instance
cd /home/ubuntu
wget https://raw.githubusercontent.com/YOUR-USERNAME/Kaggle-competition-assist/main/deployment_script.sh
chmod +x deployment_script.sh
./deployment_script.sh
```

**Verification:**
- [ ] Python 3.11 installed: `python3.11 --version`
- [ ] Node.js installed: `node --version`
- [ ] Nginx installed: `nginx -v`
- [ ] Repository cloned: `ls -la Kaggle-competition-assist`
- [ ] Virtual environment created: `ls -la Kaggle-competition-assist/venv`
- [ ] Playwright installed: `venv/bin/playwright --version`

---

### Step 3: Configure Environment Variables

```bash
cd /home/ubuntu/Kaggle-competition-assist
nano .env
```

**Copy these from your local .env:**
```env
ENVIRONMENT=production
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key
GROQ_API_KEY=your-groq-api-key
GOOGLE_API_KEY=your-google-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
HUGGINGFACEHUB_API_TOKEN=your-huggingface-token
PERPLEXITY_API_KEY=your-perplexity-api-key
FAISS_INDEX_PATH=./vector_store/faiss_index
REDIS_URL=redis://localhost:6379/0
```

**⚠️ IMPORTANT:** Change `ENVIRONMENT=production` (uses Groq instead of Ollama)

**Verification:**
- [ ] .env file created: `cat .env | head -n 5`
- [ ] All API keys present: `grep -c "API_KEY" .env` (should be 5+)
- [ ] Environment set to production: `grep ENVIRONMENT .env`

---

### Step 4: Set Up Services

```bash
cd /home/ubuntu/Kaggle-competition-assist
chmod +x setup_services.sh
./setup_services.sh
```

**Verification:**
- [ ] Backend service created: `sudo systemctl status kaggle-backend`
- [ ] Frontend service created: `sudo systemctl status kaggle-frontend`
- [ ] Nginx running: `sudo systemctl status nginx`
- [ ] All services "active (running)" - no errors

---

### Step 5: Check Service Logs

```bash
# Check for errors in backend
sudo journalctl -u kaggle-backend -n 50

# Check for errors in frontend  
sudo journalctl -u kaggle-frontend -n 50

# Check Nginx errors
sudo tail -n 50 /var/log/nginx/error.log
```

**Verification:**
- [ ] No "ERROR" messages in backend logs
- [ ] No "ERROR" messages in frontend logs
- [ ] No critical errors in Nginx logs
- [ ] Backend shows "Running on http://0.0.0.0:5000"
- [ ] Frontend shows "You can now view your Streamlit app"

---

## 🧪 Functional Testing

### Test 1: Health Check
```bash
# On EC2 instance
curl http://localhost:5000/health

# From your local machine
curl http://YOUR-EC2-IP/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-15T...",
  "version": "1.0.0"
}
```

**Verification:**
- [ ] Local health check works
- [ ] Remote health check works
- [ ] Response time < 2 seconds

---

### Test 2: Frontend Access

**Open in browser:** `http://YOUR-EC2-IP`

**Verification:**
- [ ] Frontend loads successfully
- [ ] Dark theme displays correctly
- [ ] Competition input box visible
- [ ] Chat interface responsive
- [ ] No console errors (F12 Developer Tools)

---

### Test 3: Query Testing (Match Local Responses)

**Query 1: Simple Competition Query**
```
Input: "What is the evaluation metric for Titanic?"
Competition: titanic
```

**Verification:**
- [ ] Response mentions "accuracy" or "survival prediction"
- [ ] Response time (first time): 20-30 seconds
- [ ] Ask SAME question again
- [ ] Response time (cached): 1-3 seconds ✅ **15x speedup!**
- [ ] Cached response identical to first response

---

**Query 2: Code Review**
```
Input: "Review my code: df['target_mean'] = df['target'].mean()"
Competition: titanic
```

**Verification:**
- [ ] Response mentions "data leakage"
- [ ] Response mentions "fit on training data only"
- [ ] Response provides corrected code
- [ ] Response matches local version output

---

**Query 3: Ideas Generation**
```
Input: "Give me ideas for Titanic competition"
Competition: titanic
```

**Verification:**
- [ ] Response includes multiple specific ideas (3+)
- [ ] Ideas are competition-specific (mentions Titanic features)
- [ ] Response includes feature engineering suggestions
- [ ] Response includes ensemble methods
- [ ] Response quality matches local version

---

**Query 4: Discussion Helper**
```
Input: "What are people discussing about Titanic?"
Competition: titanic
```

**Verification:**
- [ ] Response includes discussion insights
- [ ] Mentions specific discussion topics
- [ ] Scraping works (no errors)
- [ ] Response matches local version

---

### Test 4: Cache Verification

```bash
# On EC2, check ChromaDB
ls -la /home/ubuntu/Kaggle-competition-assist/chroma_db/
```

**Verification:**
- [ ] chroma_db directory exists
- [ ] Contains .sqlite3 file
- [ ] File size > 0 bytes
- [ ] New queries get cached (file grows)

---

### Test 5: Multi-Agent Testing

**Query:** "Analyze Titanic competition and give me a complete strategy"

**Verification:**
- [ ] Multiple agents respond (check logs)
- [ ] Response includes: evaluation metric, data description, ideas
- [ ] Response coherent and well-structured
- [ ] No agent failures in logs
- [ ] Response quality = local version

---

## 🔍 Performance Comparison

### Local vs Deployed Metrics

| Metric | Local | Deployed | Match? |
|--------|-------|----------|--------|
| First query response time | ___s | ___s | [ ] |
| Cached query response time | ___s | ___s | [ ] |
| Cache hit rate | ___% | ___% | [ ] |
| Code review accuracy | ___/10 | ___/10 | [ ] |
| Ideas quality | ___/10 | ___/10 | [ ] |
| UI responsiveness | ___/10 | ___/10 | [ ] |

**Target:** All metrics should be within 10% of local version

---

## 🐛 Troubleshooting Common Issues

### Issue 1: Services Not Starting

```bash
# Check detailed logs
sudo journalctl -u kaggle-backend -n 100 --no-pager
sudo journalctl -u kaggle-frontend -n 100 --no-pager

# Common fixes:
# 1. Missing dependencies
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
pip install -r requirements.txt

# 2. Port already in use
sudo netstat -tulpn | grep :5000
sudo netstat -tulpn | grep :8501

# 3. Permission issues
sudo chown -R ubuntu:ubuntu /home/ubuntu/Kaggle-competition-assist
```

---

### Issue 2: Frontend Loads but Can't Connect to Backend

```bash
# Check Nginx configuration
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/kaggle-copilot

# Check backend is running
curl http://localhost:5000/health

# Check firewall (AWS Security Group)
# Ensure ports 80, 443, 5000, 8501 are open
```

---

### Issue 3: Slow Response Times

```bash
# Check EC2 instance resources
htop  # Install if needed: sudo apt install htop

# Check memory
free -h

# Check disk space
df -h

# Add swap if low memory
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### Issue 4: Playwright/Scraping Errors

```bash
# Reinstall Playwright with dependencies
cd /home/ubuntu/Kaggle-competition-assist
source venv/bin/activate
playwright install --with-deps

# Check browser binaries
playwright install --help
```

---

## ✅ Final Verification Checklist

Before marking deployment as complete:

### Functionality
- [ ] Health endpoint responds
- [ ] Frontend loads correctly
- [ ] All 10 agents working
- [ ] Cache working (15x speedup)
- [ ] Scraping working (no Playwright errors)
- [ ] Code review working
- [ ] Ideas generation working
- [ ] Discussion helper working

### Performance
- [ ] First query: 20-30s (acceptable)
- [ ] Cached query: 1-3s (acceptable)
- [ ] UI responsive (<1s load)
- [ ] No timeouts on complex queries

### Reliability
- [ ] Services auto-restart on failure
- [ ] Nginx reverse proxy working
- [ ] Error handling working
- [ ] Logs accessible and readable

### Security
- [ ] SSH access restricted to your IP
- [ ] .env file not exposed
- [ ] Debug endpoints secured (if applicable)
- [ ] Nginx security headers configured

---

## 🎉 Success Criteria

✅ **Deployment is successful if:**

1. All functional tests pass
2. Response quality = local version
3. Performance within 10% of local
4. No critical errors in logs
5. Cache speedup working (15x)
6. All 10 agents responding

---

## 📞 Support

If you encounter issues:

1. **Check logs first:**
   ```bash
   sudo journalctl -u kaggle-backend -f
   sudo journalctl -u kaggle-frontend -f
   ```

2. **Common commands:**
   ```bash
   # Restart services
   sudo systemctl restart kaggle-backend kaggle-frontend
   
   # Check status
   sudo systemctl status kaggle-backend
   
   # View configuration
   cat /etc/systemd/system/kaggle-backend.service
   ```

3. **Debug mode:**
   Edit `.env` and add:
   ```
   DEBUG=True
   FLASK_DEBUG=True
   ```
   Then restart: `sudo systemctl restart kaggle-backend`

---

## 📊 Performance Monitoring

### Set up CloudWatch (Optional)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

### Monitor logs in real-time

```bash
# Terminal 1: Backend logs
sudo journalctl -u kaggle-backend -f

# Terminal 2: Frontend logs  
sudo journalctl -u kaggle-frontend -f

# Terminal 3: Nginx logs
sudo tail -f /var/log/nginx/access.log
```

---

**🚀 Once all checks pass, your deployed version is working exactly like local!**

**Next steps:**
1. Share the URL with testers
2. Monitor logs for first 24 hours
3. Gather feedback
4. Iterate and improve

---

**Last Updated:** October 15, 2025

