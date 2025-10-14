# 🚀 AWS Deployment Guide - Kaggle Competition Assistant

## 🎓 **Using AWS Student Credits (Free Tier)**

---

## ✅ **Prerequisites**

1. **AWS Account** with student credits activated
2. **AWS CLI** installed: https://aws.amazon.com/cli/
3. **Git** installed
4. **SSH key** for EC2 access

---

## 🎯 **Option 1: AWS EC2 (Recommended - Most Impressive)**

### **Step 1: Launch EC2 Instance**

1. **Go to AWS Console** → EC2 → Launch Instance

2. **Configure Instance:**
   ```
   Name: kaggle-copilot-production
   AMI: Ubuntu Server 22.04 LTS (Free tier eligible)
   Instance Type: t3.micro (2 vCPU, 1 GB RAM) - FREE TIER ✅
                 OR t3.small (2 vCPU, 2 GB RAM) - if you need more power
   Key pair: Create new or use existing
   Security Group: 
     - SSH (22) - Your IP only
     - HTTP (80) - 0.0.0.0/0
     - HTTPS (443) - 0.0.0.0/0
     - Custom TCP (5000) - 0.0.0.0/0 (Backend)
     - Custom TCP (8501) - 0.0.0.0/0 (Frontend)
   Storage: 20 GB gp3 (30 GB free tier)
   ```
   
   **Note:** AWS has replaced t2 instances with newer t3 instances in free tier.
   **t3.micro is perfect for testing and initial launch (10-50 concurrent users).**

3. **Launch Instance** and note the **Public IPv4 address**

### **Step 2: Connect to EC2**

```bash
# Download your key pair (.pem file)
chmod 400 your-key.pem

# Connect via SSH
ssh -i your-key.pem ubuntu@<YOUR-EC2-IP>
```

### **Step 3: Setup Server**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install Node.js (for Playwright)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install system dependencies
sudo apt install -y git build-essential libssl-dev libffi-dev python3-pip
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 
sudo apt install -y libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 
sudo apt install -y libxrandr2 libgbm1 libasound2

# Install Nginx (reverse proxy)
sudo apt install nginx -y
```

### **Step 4: Clone & Setup Project**

```bash
# Clone repository
cd /home/ubuntu
git clone https://github.com/YOUR-USERNAME/Kaggle-competition-assist.git
cd Kaggle-competition-assist

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install
playwright install-deps

# Setup environment variables
nano .env
```

**Add to .env:**
```env
ENVIRONMENT=production
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-api-key
GROQ_API_KEY=your-groq-key
GOOGLE_API_KEY=your-gemini-key
PERPLEXITY_API_KEY=your-perplexity-key
```

### **Step 5: Setup Systemd Services**

**Backend Service:**
```bash
sudo nano /etc/systemd/system/kaggle-backend.service
```

```ini
[Unit]
Description=Kaggle Copilot Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Kaggle-competition-assist
Environment="PATH=/home/ubuntu/Kaggle-competition-assist/venv/bin"
ExecStart=/home/ubuntu/Kaggle-competition-assist/venv/bin/gunicorn minimal_backend:app --bind 0.0.0.0:5000 --workers 4 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend Service:**
```bash
sudo nano /etc/systemd/system/kaggle-frontend.service
```

```ini
[Unit]
Description=Kaggle Copilot Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Kaggle-competition-assist
Environment="PATH=/home/ubuntu/Kaggle-competition-assist/venv/bin"
ExecStart=/home/ubuntu/Kaggle-competition-assist/venv/bin/streamlit run streamlit_frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start Services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable kaggle-backend kaggle-frontend
sudo systemctl start kaggle-backend kaggle-frontend

# Check status
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend
```

### **Step 6: Configure Nginx Reverse Proxy**

```bash
sudo nano /etc/nginx/sites-available/kaggle-copilot
```

```nginx
server {
    listen 80;
    server_name <YOUR-EC2-IP>;

    # Frontend (Streamlit)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Debug endpoints (restrict access in production)
    location /debug {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        # Optional: Add IP whitelist
        # allow YOUR.IP.ADDRESS;
        # deny all;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/kaggle-copilot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Step 7: Verify Deployment**

```bash
# Check services
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend

# Check logs
sudo journalctl -u kaggle-backend -f
sudo journalctl -u kaggle-frontend -f

# Test endpoints
curl http://localhost:5000/health
curl http://localhost:8501
```

**Access your app:**
```
http://<YOUR-EC2-IP>
```

---

## 🎯 **Option 2: AWS Elastic Beanstalk (Easier)**

### **Step 1: Install EB CLI**

```bash
pip install awsebcli
```

### **Step 2: Initialize EB**

```bash
cd Kaggle-competition-assist
eb init -p python-3.11 kaggle-copilot --region us-east-1
```

### **Step 3: Create Environment**

```bash
eb create kaggle-copilot-prod --instance-type t2.medium
```

### **Step 4: Deploy**

```bash
eb deploy
```

### **Step 5: Open Application**

```bash
eb open
```

---

## 🔒 **Security Best Practices**

### **1. Restrict SSH Access**

```bash
# In AWS Console → EC2 → Security Groups
# Change SSH (22) from 0.0.0.0/0 to YOUR.IP.ADDRESS
```

### **2. Setup HTTPS (Optional but Recommended)**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d your-domain.com
```

### **3. Secure Debug Endpoints**

In `minimal_backend.py`, add IP whitelist:

```python
ALLOWED_DEBUG_IPS = ['YOUR.IP.ADDRESS']

@app.before_request
def restrict_debug():
    if request.path.startswith('/debug'):
        if request.remote_addr not in ALLOWED_DEBUG_IPS:
            return jsonify({"error": "Forbidden"}), 403
```

### **4. Environment Variables**

Never commit `.env` to Git. Use AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
    --name kaggle-copilot-secrets \
    --secret-string file://.env
```

---

## 📊 **Monitoring & Logs**

### **CloudWatch (AWS)**

- **Metrics**: CPU, Memory, Network
- **Logs**: Application logs
- **Alarms**: Set up alerts for high CPU/errors

### **Application Logs**

```bash
# Backend logs
sudo journalctl -u kaggle-backend -f

# Frontend logs
sudo journalctl -u kaggle-frontend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🚀 **Scaling & Performance**

### **Vertical Scaling (Bigger Instance)**

- t3.micro (free) → t3.small (~$15/mo) → t3.medium (~$30/mo) → t3.large (~$60/mo)
- Restart not required (stop → change type → start)
- **Recommendation:** Start with t3.micro, upgrade to t3.small if you get 50+ concurrent users

### **Horizontal Scaling (Load Balancer)**

1. Create AMI from current instance
2. Setup Auto Scaling Group
3. Add Application Load Balancer
4. Configure target groups

### **Database Optimization**

- Move ChromaDB to Amazon RDS or DynamoDB
- Use ElastiCache (Redis) for caching

---

## 💰 **Cost Optimization**

### **Free Tier Limits:**
- t3.micro: 750 hours/month (1 instance always running = FREE!)
- 30 GB EBS storage (free)
- 1 GB data transfer out (free)

### **Student Credits:**
- $100 AWS credits
- t3.micro: 100% free (within 750 hours/month)
- t3.small: ~$15/month = 6+ months free with credits
- **Perfect for launch and growth!**

### **Cost Monitoring:**
```bash
# Set up billing alert in AWS Console
# Budget: $10/month alert threshold
```

---

## 🔧 **Troubleshooting**

### **Service won't start:**
```bash
sudo journalctl -u kaggle-backend -n 50
# Check for missing dependencies or environment variables
```

### **Memory issues:**
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### **Playwright issues:**
```bash
# Reinstall browsers with dependencies
playwright install --with-deps
```

---

## 📝 **Maintenance**

### **Update Application:**
```bash
cd /home/ubuntu/Kaggle-competition-assist
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kaggle-backend kaggle-frontend
```

### **Backup ChromaDB:**
```bash
# Schedule daily backups
crontab -e

# Add:
0 2 * * * tar -czf /home/ubuntu/backups/chromadb-$(date +\%Y\%m\%d).tar.gz /home/ubuntu/Kaggle-competition-assist/chroma_db
```

---

## ✅ **Production Checklist**

Before going live:

- [ ] All API keys in `.env` file
- [ ] Security group configured (SSH restricted)
- [ ] Services running (`systemctl status`)
- [ ] Nginx configured and running
- [ ] Debug endpoints secured or disabled
- [ ] Monitoring setup (CloudWatch)
- [ ] Backup strategy in place
- [ ] Cost alerts configured
- [ ] SSL certificate installed (if using domain)
- [ ] Application tested end-to-end

---

## 🎉 **Your Live URLs**

After deployment:
- **Frontend**: `http://<YOUR-EC2-IP>`
- **Backend API**: `http://<YOUR-EC2-IP>/api`
- **Health Check**: `http://<YOUR-EC2-IP>/api/health`

---

## 💡 **For LinkedIn Post**

Use these impressive details:
- ✅ "Deployed to AWS EC2"
- ✅ "Production-grade infrastructure"
- ✅ "Nginx reverse proxy"
- ✅ "Systemd service management"
- ✅ "Scalable architecture"
- ✅ "CloudWatch monitoring"

---

**🚀 Ready to deploy! Follow the steps and you'll be live in ~30 minutes!**



