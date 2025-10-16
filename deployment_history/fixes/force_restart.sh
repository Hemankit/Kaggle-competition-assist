#!/bin/bash
cd ~/Kaggle-competition-assist

echo "🧹 Step 1: Clearing ALL Python cache..."
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -delete 2>/dev/null || true
find . -name '*.pyo' -delete 2>/dev/null || true
echo "✅ Python cache cleared"

echo ""
echo "🔄 Step 2: Stopping backend..."
sudo systemctl stop kaggle-backend
sleep 2
echo "✅ Backend stopped"

echo ""
echo "🚀 Step 3: Starting backend with fresh imports..."
sudo systemctl start kaggle-backend
sleep 15  # Give it time to fully initialize

echo ""
echo "✅ Backend should be ready now!"
echo ""
echo "Testing backend health..."
curl -s http://localhost:5000/health || echo "Health check failed - backend may still be starting"


