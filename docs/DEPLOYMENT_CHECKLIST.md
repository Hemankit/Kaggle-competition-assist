# ✅ AWS Deployment Checklist

## 🚀 **Quick Start: Deploy in 30 Minutes**

---

### **Phase 1: AWS Setup** (5 minutes)

- [ ] Log into AWS Console with student account
- [ ] Navigate to EC2
- [ ] Launch Instance (t2.medium, Ubuntu 22.04)
- [ ] Configure Security Group (ports 22, 80, 443, 5000, 8501)
- [ ] Download key pair (.pem file)
- [ ] Note Public IPv4 address

---

### **Phase 2: Server Setup** (10 minutes)

```bash
# Connect
ssh -i your-key.pem ubuntu@<YOUR-IP>

# Install everything
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv python3.11-dev git nginx -y
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

---

### **Phase 3: Project Setup** (10 minutes)

```bash
# Clone (replace with your repo)
cd /home/ubuntu
git clone https://github.com/YOUR-USERNAME/Kaggle-competition-assist.git
cd Kaggle-competition-assist

# Setup environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
playwright install-deps

# Configure .env
nano .env
```

**Add your API keys:**
```
ENVIRONMENT=production
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-key
GROQ_API_KEY=your-key
GOOGLE_API_KEY=your-key
PERPLEXITY_API_KEY=your-key
```

---

### **Phase 4: Service Setup** (5 minutes)

```bash
# Backend service
sudo nano /etc/systemd/system/kaggle-backend.service
```

Paste from `docs/AWS_DEPLOYMENT_GUIDE.md`

```bash
# Frontend service
sudo nano /etc/systemd/system/kaggle-frontend.service
```

Paste from `docs/AWS_DEPLOYMENT_GUIDE.md`

```bash
# Start services
sudo systemctl daemon-reload
sudo systemctl enable kaggle-backend kaggle-frontend
sudo systemctl start kaggle-backend kaggle-frontend
sudo systemctl status kaggle-backend
sudo systemctl status kaggle-frontend
```

---

### **Phase 5: Nginx Setup** (5 minutes)

```bash
# Configure reverse proxy
sudo nano /etc/nginx/sites-available/kaggle-copilot
```

Paste from `docs/AWS_DEPLOYMENT_GUIDE.md` (replace <YOUR-EC2-IP>)

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/kaggle-copilot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### **Phase 6: Verify & Test** (5 minutes)

```bash
# Check health
curl http://localhost:5000/health
curl http://localhost:8501

# Check logs
sudo journalctl -u kaggle-backend -f
sudo journalctl -u kaggle-frontend -f
```

**Open browser:** `http://<YOUR-EC2-IP>`

✅ **Should see your Streamlit frontend!**

---

## 📸 **Take Screenshots for LinkedIn**

Now that it's live, take screenshots:

1. **Dark Mode UI**
   - Query example
   - Detailed response
   - Cache indicator

2. **LangGraph Diagram**
   - Open: `http://<YOUR-IP>/debug/dashboard`
   - Screenshot the graph

3. **Architecture**
   - Create simple diagram

---

## 📝 **Post to LinkedIn**

1. **Choose version** from `docs/LINKEDIN_POST.md`
2. **Customize** with your details
3. **Add screenshots**
4. **Include hashtags**
5. **Post at optimal time** (Tue-Thu, 8-10 AM)

---

## 🔗 **Update GitHub**

```bash
# Add deployment info to README
git add .
git commit -m "Add AWS deployment configuration"
git push origin main
```

Update `README.md` with:
- Live demo URL
- Deployment details
- Screenshots
- Architecture diagram

---

## 🎯 **Optimization (Later)**

After initial deployment:

- [ ] Setup HTTPS with Let's Encrypt
- [ ] Configure CloudWatch monitoring
- [ ] Setup automated backups
- [ ] Add IP whitelist for /debug
- [ ] Create AMI for quick recovery
- [ ] Setup cost alerts

---

## 💰 **Monitor Costs**

Check AWS Billing Dashboard:
- Expected: $15-20/month for t2.medium
- Student credits: $100 (5-6 months free!)

---

## 🎉 **Success Metrics**

Track after posting:

- LinkedIn post views
- Profile views
- Connection requests
- Job inquiries
- GitHub stars
- Demo site visits

---

## 📞 **Need Help?**

If something breaks:

1. Check logs: `sudo journalctl -u kaggle-backend -f`
2. Verify services: `sudo systemctl status kaggle-backend`
3. Test endpoints: `curl http://localhost:5000/health`
4. Check Nginx: `sudo nginx -t`
5. Review security group (ports open?)

---

**✅ You're live! Time to blow up LinkedIn! 🚀**
