#!/bin/bash
# ===================================================
# AWS EC2 Deployment Script - Kaggle Competition Assistant
# Run this on your AWS EC2 instance after SSH connection
# ===================================================

set -e  # Exit on error

echo "🚀 Starting deployment of Kaggle Competition Assistant..."

# Step 1: Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install Python 3.11
echo "🐍 Installing Python 3.11..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Step 3: Install Node.js (for Playwright)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Step 4: Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y git build-essential libssl-dev libffi-dev python3-pip
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 
sudo apt install -y libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 
sudo apt install -y libxrandr2 libgbm1 libasound2

# Step 5: Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install nginx -y

# Step 6: Clone repository
echo "📥 Cloning repository..."
cd /home/ubuntu
if [ -d "Kaggle-competition-assist" ]; then
    echo "⚠️  Directory already exists. Pulling latest changes..."
    cd Kaggle-competition-assist
    git pull origin main
else
    # Replace YOUR-GITHUB-USERNAME with your actual GitHub username
    git clone https://github.com/Hemankit/Kaggle-competition-assist.git
    cd Kaggle-competition-assist
fi

# Step 7: Create virtual environment
echo "🔧 Setting up Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Step 8: Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 9: Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
playwright install
playwright install-deps

echo ""
echo "✅ Base installation complete!"
echo ""
echo "⚠️  NEXT STEPS (MANUAL):"
echo "1. Create .env file: nano /home/ubuntu/Kaggle-competition-assist/.env"
echo "2. Copy your API keys from local .env to server .env"
echo "3. Run the service setup script: ./setup_services.sh"
echo ""

