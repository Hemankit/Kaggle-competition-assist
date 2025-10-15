#!/bin/bash
# ===================================================
# Service Setup Script - Creates systemd services
# Run AFTER deployment_script.sh and .env configuration
# ===================================================

set -e

echo "🔧 Setting up systemd services..."

# Get the EC2 IP address automatically
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "📍 Detected EC2 IP: $EC2_IP"

# Step 1: Create backend service
echo "📝 Creating backend service..."
sudo tee /etc/systemd/system/kaggle-backend.service > /dev/null <<EOF
[Unit]
Description=Kaggle Copilot Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Kaggle-competition-assist
Environment="PATH=/home/ubuntu/Kaggle-competition-assist/venv/bin"
ExecStart=/home/ubuntu/Kaggle-competition-assist/venv/bin/python minimal_backend.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 2: Create frontend service
echo "📝 Creating frontend service..."
sudo tee /etc/systemd/system/kaggle-frontend.service > /dev/null <<EOF
[Unit]
Description=Kaggle Copilot Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Kaggle-competition-assist
Environment="PATH=/home/ubuntu/Kaggle-competition-assist/venv/bin"
Environment="BACKEND_URL=http://localhost:5000"
ExecStart=/home/ubuntu/Kaggle-competition-assist/venv/bin/streamlit run streamlit_frontend/app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 3: Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/kaggle-copilot > /dev/null <<EOF
server {
    listen 80;
    server_name $EC2_IP;

    # Frontend (Streamlit)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Backend API
    location /api {
        rewrite ^/api/(.*) /\$1 break;
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:5000/health;
        proxy_set_header Host \$host;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/kaggle-copilot /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo "✅ Testing Nginx configuration..."
sudo nginx -t

# Step 4: Start all services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable kaggle-backend kaggle-frontend nginx
sudo systemctl restart nginx
sudo systemctl restart kaggle-backend
sudo systemctl restart kaggle-frontend

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
echo "===================="
sudo systemctl status kaggle-backend --no-pager | grep Active
sudo systemctl status kaggle-frontend --no-pager | grep Active
sudo systemctl status nginx --no-pager | grep Active

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Your application is now running at:"
echo "   Frontend: http://$EC2_IP"
echo "   Backend Health: http://$EC2_IP/health"
echo ""
echo "📋 Useful commands:"
echo "   View backend logs: sudo journalctl -u kaggle-backend -f"
echo "   View frontend logs: sudo journalctl -u kaggle-frontend -f"
echo "   Restart backend: sudo systemctl restart kaggle-backend"
echo "   Restart frontend: sudo systemctl restart kaggle-frontend"
echo ""

