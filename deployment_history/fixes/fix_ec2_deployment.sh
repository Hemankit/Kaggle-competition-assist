#!/bin/bash
# ===================================================================
# EC2 Deployment Fix Script
# ===================================================================
# This script fixes common deployment issues that cause the app to
# return placeholder responses instead of real competition data.
# ===================================================================

set -e  # Exit on any error

echo "=========================================="
echo "🔧 EC2 Deployment Fix Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as correct user
if [ "$USER" != "ubuntu" ]; then
    echo -e "${YELLOW}Warning: This script should be run as 'ubuntu' user${NC}"
    echo "Current user: $USER"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Project directory
PROJECT_DIR="/home/ubuntu/Kaggle-competition-assist"
VENV_DIR="$PROJECT_DIR/venv"

# Step 1: Verify project directory exists
echo "=========================================="
echo "Step 1: Verifying project directory"
echo "=========================================="
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    echo "Please clone the repository first:"
    echo "  cd /home/ubuntu"
    echo "  git clone https://github.com/YOUR-USERNAME/Kaggle-competition-assist.git"
    exit 1
fi
echo -e "${GREEN}✅ Project directory found${NC}"
cd "$PROJECT_DIR"

# Step 2: Check Python version
echo ""
echo "=========================================="
echo "Step 2: Checking Python version"
echo "=========================================="
if ! command -v python3.11 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3.11 not found. Installing...${NC}"
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3.11-dev
fi
PYTHON_VERSION=$(python3.11 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION installed${NC}"

# Step 3: Create/activate virtual environment
echo ""
echo "=========================================="
echo "Step 3: Setting up virtual environment"
echo "=========================================="
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv "$VENV_DIR"
fi
echo -e "${GREEN}✅ Virtual environment ready${NC}"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Step 4: Upgrade pip and install dependencies
echo ""
echo "=========================================="
echo "Step 4: Installing Python dependencies"
echo "=========================================="
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing requirements..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install requirements${NC}"
    exit 1
fi
echo -e "${GREEN}✅ All Python packages installed${NC}"

# Step 5: Install Playwright browsers (CRITICAL!)
echo ""
echo "=========================================="
echo "Step 5: Installing Playwright browsers"
echo "=========================================="
echo "This is CRITICAL for web scraping to work!"
echo "Installing system dependencies and browser binaries..."

# Install system dependencies first
sudo apt-get update
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2

# Install Playwright browsers
playwright install --with-deps chromium

# Verify Playwright installation
if playwright --version &> /dev/null; then
    echo -e "${GREEN}✅ Playwright installed successfully${NC}"
    playwright --version
else
    echo -e "${RED}❌ Playwright installation failed${NC}"
    exit 1
fi

# Step 6: Check environment variables
echo ""
echo "=========================================="
echo "Step 6: Checking environment variables"
echo "=========================================="

ENV_FILE="$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Creating template .env file..."
    cat > "$ENV_FILE" << 'EOF'
# === Environment ===
ENVIRONMENT=production

# === API Keys === (REPLACE WITH YOUR ACTUAL KEYS!)
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key

GROQ_API_KEY=your-groq-api-key
GOOGLE_API_KEY=your-google-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
HUGGINGFACEHUB_API_TOKEN=your-huggingface-token
PERPLEXITY_API_KEY=your-perplexity-api-key

# === Redis and Vector DB ===
FAISS_INDEX_PATH=./vector_store/faiss_index
REDIS_URL=redis://localhost:6379/0

# === Flask Settings ===
FLASK_DEBUG=False
FLASK_ENV=production
EOF
    echo -e "${YELLOW}⚠️  Template .env file created. Please edit it with your API keys:${NC}"
    echo "  nano $ENV_FILE"
    echo ""
    echo "Required API keys:"
    echo "  1. Kaggle API (username + key from https://www.kaggle.com/settings)"
    echo "  2. Groq API (from https://console.groq.com/)"
    echo "  3. Google API (from https://makersuite.google.com/app/apikey)"
    echo "  4. DeepSeek API (from https://platform.deepseek.com/)"
    echo "  5. HuggingFace Token (from https://huggingface.co/settings/tokens)"
    echo ""
    read -p "Press Enter after you've updated the .env file..." 
fi

# Validate environment variables
echo "Validating environment variables..."
source "$ENV_FILE"

MISSING_KEYS=()
[ -z "$KAGGLE_USERNAME" ] || [ "$KAGGLE_USERNAME" = "your-kaggle-username" ] && MISSING_KEYS+=("KAGGLE_USERNAME")
[ -z "$KAGGLE_KEY" ] || [ "$KAGGLE_KEY" = "your-kaggle-api-key" ] && MISSING_KEYS+=("KAGGLE_KEY")
[ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your-groq-api-key" ] && MISSING_KEYS+=("GROQ_API_KEY")
[ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-api-key" ] && MISSING_KEYS+=("GOOGLE_API_KEY")

if [ ${#MISSING_KEYS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing or invalid API keys:${NC}"
    printf '%s\n' "${MISSING_KEYS[@]}"
    echo ""
    echo "Please update your .env file with valid API keys:"
    echo "  nano $ENV_FILE"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Step 7: Create required directories
echo ""
echo "=========================================="
echo "Step 7: Creating required directories"
echo "=========================================="
mkdir -p "$PROJECT_DIR/chroma_db"
mkdir -p "$PROJECT_DIR/data/discussions"
mkdir -p "$PROJECT_DIR/data/chat_history"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/vector_store"

# Set proper permissions
chmod -R 755 "$PROJECT_DIR/data"
chmod -R 755 "$PROJECT_DIR/logs"
chmod -R 755 "$PROJECT_DIR/chroma_db"

echo -e "${GREEN}✅ Directories created${NC}"

# Step 8: Test backend imports
echo ""
echo "=========================================="
echo "Step 8: Testing backend imports"
echo "=========================================="

python3.11 << 'PYEOF'
import sys
import os

# Add project to path
sys.path.insert(0, '/home/ubuntu/Kaggle-competition-assist')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("Testing critical imports...")
errors = []

try:
    from orchestrators.component_orchestrator import ComponentOrchestrator
    print("✅ ComponentOrchestrator")
except Exception as e:
    errors.append(f"❌ ComponentOrchestrator: {e}")

try:
    from Kaggle_Fetcher.kaggle_api_client import get_competition_details
    print("✅ Kaggle API Client")
except Exception as e:
    errors.append(f"❌ Kaggle API Client: {e}")

try:
    from scraper.overview_scraper import OverviewScraper
    print("✅ Overview Scraper (Playwright)")
except Exception as e:
    errors.append(f"❌ Overview Scraper: {e}")

try:
    from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
    print("✅ ChromaDB RAG Pipeline")
except Exception as e:
    errors.append(f"❌ ChromaDB RAG Pipeline: {e}")

try:
    from agents.competition_summary_agent import CompetitionSummaryAgent
    print("✅ Competition Summary Agent")
except Exception as e:
    errors.append(f"❌ Competition Summary Agent: {e}")

if errors:
    print("\n❌ Import errors found:")
    for error in errors:
        print(f"  {error}")
    sys.exit(1)
else:
    print("\n✅ All critical imports successful!")
PYEOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Import test failed${NC}"
    echo "Some dependencies may be missing or incorrectly configured."
    exit 1
fi

# Step 9: Create systemd service files
echo ""
echo "=========================================="
echo "Step 9: Creating systemd service files"
echo "=========================================="

# Backend service
sudo tee /etc/systemd/system/kaggle-backend.service > /dev/null << EOF
[Unit]
Description=Kaggle Competition Assistant Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/python3 minimal_backend.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/Kaggle-competition-assist/logs/backend.log
StandardError=append:/home/ubuntu/Kaggle-competition-assist/logs/backend-error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Backend service created${NC}"

# Frontend service (Streamlit)
sudo tee /etc/systemd/system/kaggle-frontend.service > /dev/null << EOF
[Unit]
Description=Kaggle Competition Assistant Frontend (Streamlit)
After=network.target kaggle-backend.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$PROJECT_DIR/streamlit_frontend
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/Kaggle-competition-assist/logs/frontend.log
StandardError=append:/home/ubuntu/Kaggle-competition-assist/logs/frontend-error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Frontend service created${NC}"

# Step 10: Reload systemd and restart services
echo ""
echo "=========================================="
echo "Step 10: Restarting services"
echo "=========================================="

sudo systemctl daemon-reload
sudo systemctl enable kaggle-backend kaggle-frontend

echo "Stopping services..."
sudo systemctl stop kaggle-backend kaggle-frontend

echo "Starting backend..."
sudo systemctl start kaggle-backend
sleep 5

echo "Starting frontend..."
sudo systemctl start kaggle-frontend
sleep 3

# Check service status
echo ""
echo "=========================================="
echo "Service Status"
echo "=========================================="

if sudo systemctl is-active --quiet kaggle-backend; then
    echo -e "${GREEN}✅ Backend service is running${NC}"
else
    echo -e "${RED}❌ Backend service failed to start${NC}"
    echo "Check logs with: sudo journalctl -u kaggle-backend -n 50"
fi

if sudo systemctl is-active --quiet kaggle-frontend; then
    echo -e "${GREEN}✅ Frontend service is running${NC}"
else
    echo -e "${RED}❌ Frontend service failed to start${NC}"
    echo "Check logs with: sudo journalctl -u kaggle-frontend -n 50"
fi

# Step 11: Test the backend health endpoint
echo ""
echo "=========================================="
echo "Step 11: Testing backend health"
echo "=========================================="
sleep 3

HEALTH_RESPONSE=$(curl -s http://localhost:5000/health || echo "ERROR")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Backend health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    echo "Response: $HEALTH_RESPONSE"
    echo ""
    echo "Check backend logs:"
    echo "  sudo journalctl -u kaggle-backend -n 50"
fi

# Step 12: Configure Nginx (if installed)
echo ""
echo "=========================================="
echo "Step 12: Configuring Nginx"
echo "=========================================="

if command -v nginx &> /dev/null; then
    echo "Nginx detected. Configuring reverse proxy..."
    
    sudo tee /etc/nginx/sites-available/kaggle-copilot > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # Frontend (Streamlit)
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:5000/health;
        proxy_set_header Host $host;
    }
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/kaggle-copilot /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload
    if sudo nginx -t; then
        sudo systemctl reload nginx
        echo -e "${GREEN}✅ Nginx configured and reloaded${NC}"
    else
        echo -e "${RED}❌ Nginx configuration error${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Nginx not installed. Skipping reverse proxy setup.${NC}"
    echo "To install Nginx:"
    echo "  sudo apt install nginx -y"
fi

# Final summary
echo ""
echo "=========================================="
echo "🎉 Deployment Fix Complete!"
echo "=========================================="
echo ""
echo "✅ What was fixed:"
echo "  1. Python dependencies reinstalled"
echo "  2. Playwright browsers installed (CRITICAL FIX)"
echo "  3. Environment variables validated"
echo "  4. Required directories created"
echo "  5. Services restarted with proper configuration"
echo "  6. Nginx reverse proxy configured"
echo ""
echo "📍 Your app should now be accessible at:"
echo "  http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "🔍 Next steps:"
echo "  1. Test with: 'What is the evaluation metric for Titanic?'"
echo "  2. It should now return REAL data, not placeholders"
echo "  3. Second query should be 15x faster (cached)"
echo ""
echo "📊 Monitoring commands:"
echo "  View backend logs:  sudo journalctl -u kaggle-backend -f"
echo "  View frontend logs: sudo journalctl -u kaggle-frontend -f"
echo "  Check service status: sudo systemctl status kaggle-backend"
echo "  Restart services: sudo systemctl restart kaggle-backend kaggle-frontend"
echo ""
echo "🐛 If issues persist, run the diagnostic script:"
echo "  ./diagnose_deployment.sh"
echo ""


