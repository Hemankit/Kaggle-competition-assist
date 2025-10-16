# 🎨 Frontend Deployment Guide

Your Streamlit frontend is ready! You have **2 options**:

---

## 🎯 **Option 1: Run Frontend on EC2** (Recommended for Production)

### Benefits:
- Everything in one place
- No CORS issues
- Can access publicly via EC2 IP

### Steps:

**1. Install Streamlit on EC2:**

```bash
# On EC2 (you're already connected)
cd ~/Kaggle-competition-assist/streamlit_frontend
source ../venv/bin/activate
pip install -r requirements.txt
```

**2. Run Streamlit:**

```bash
# Run in background
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

**3. Configure AWS Security Group:**
- Go to AWS Console → EC2 → Security Groups
- Add inbound rule: Port 8501, Source: Your IP (or 0.0.0.0/0 for public)

**4. Access your frontend:**
```
http://18.219.148.57:8501
```

**5. Create systemd service (optional, for auto-restart):**

```bash
sudo nano /etc/systemd/system/kaggle-frontend.service
```

Paste this:
```ini
[Unit]
Description=Kaggle Copilot Frontend (Streamlit)
After=network.target kaggle-backend.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Kaggle-competition-assist/streamlit_frontend
Environment="PATH=/home/ubuntu/Kaggle-competition-assist/venv/bin"
ExecStart=/home/ubuntu/Kaggle-competition-assist/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable kaggle-frontend
sudo systemctl start kaggle-frontend
sudo systemctl status kaggle-frontend
```

---

## 💻 **Option 2: Run Frontend Locally** (Easiest for Testing)

### Benefits:
- No EC2 configuration needed
- Easier to develop/test
- Use your local browser

### Steps:

**1. Update backend URL (on Windows):**

Open `streamlit_frontend/app.py` and update line 154:

```python
BACKEND_URL = os.getenv("BACKEND_URL", "http://18.219.148.57:5000")
```

**2. Install Streamlit locally:**

```powershell
# On your Windows machine
cd C:\Users\heman\Kaggle-competition-assist\streamlit_frontend
pip install -r requirements.txt
```

**3. Run Streamlit:**

```powershell
streamlit run app.py
```

**4. Configure EC2 Security Group:**
- Go to AWS Console → EC2 → Security Groups
- Add inbound rule: Port 5000, Source: Your IP

**5. Open your browser:**
```
http://localhost:8501
```

---

## 🚀 **Quick Start Commands**

### For Option 1 (EC2):

```bash
# You're already on EC2, so just run:
cd ~/Kaggle-competition-assist/streamlit_frontend
source ../venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Then open: `http://18.219.148.57:8501` (after configuring security group)

### For Option 2 (Local):

```powershell
# On Windows PowerShell
cd C:\Users\heman\Kaggle-competition-assist\streamlit_frontend
pip install streamlit requests
$env:BACKEND_URL="http://18.219.148.57:5000"
streamlit run app.py
```

Then open: `http://localhost:8501`

---

## 🎨 **What Your Frontend Has:**

✅ **Beautiful Dark Theme** - Modern, professional UI  
✅ **User Profiles** - Save Kaggle username & competition  
✅ **Real-time Chat** - Interactive with multi-agent system  
✅ **Chat History** - Save/load conversations  
✅ **Status Indicators** - Backend connection status  
✅ **Error Handling** - Clear troubleshooting messages  
✅ **Mobile Responsive** - Works on all devices  

---

## 🔧 **Troubleshooting**

### "Connection Refused" Error
- Make sure backend is running: `curl http://localhost:5000/health`
- Check EC2 security groups (ports 5000 and 8501)
- Verify BACKEND_URL is correct in app.py

### Streamlit Not Found
```bash
pip install streamlit requests
```

### Can't Access from Browser
- Check EC2 security group has port 8501 open
- Verify you're using `--server.address 0.0.0.0`
- Try accessing from EC2 IP, not localhost

### Backend Connection Failed
- Ensure backend is healthy: `curl http://localhost:5000/health`
- Check firewall/security group settings
- Verify BACKEND_URL points to correct address

---

## 🎯 **Recommended Setup**

For quick testing: **Option 2** (Local)  
For production: **Option 1** (EC2 with systemd)

---

## 📊 **Architecture**

```
┌─────────────────┐
│  Your Browser   │
│  (port 8501)    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Streamlit UI    │ ← Option 1: On EC2
│                 │   Option 2: On Windows
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Flask Backend   │
│ (port 5000)     │ ← On EC2
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Multi-Agent     │
│ System + LLMs   │
└─────────────────┘
```

---

## 🎉 **Ready to Launch?**

Pick your option and run the commands above! The frontend will be live in ~1 minute! 🚀


