#!/bin/bash
set -e

echo "========================================"
echo "🔄 RESTARTING STREAMLIT FRONTEND"
echo "========================================"
echo ""

cd ~/Kaggle-competition-assist

echo "🛑 Stopping existing Streamlit..."
pkill -9 -f "streamlit run" || echo "No existing Streamlit process"
sleep 3

# Verify port is free
if lsof -i:8501 > /dev/null 2>&1; then
    echo "  ⚠️  Port 8501 still in use, force killing..."
    fuser -k 8501/tcp || true
    sleep 2
fi

echo ""
echo "✅ Verifying backend is running..."
curl -s http://localhost:5000/health > /dev/null && echo "  Backend is UP" || echo "  ⚠️  Backend may be down"

echo ""
echo "🚀 Starting Streamlit frontend..."
source venv/bin/activate

# Set backend URL
export BACKEND_URL="http://localhost:5000"

# Start Streamlit in background
nohup streamlit run streamlit_frontend/app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    > logs/streamlit.log 2>&1 &

STREAMLIT_PID=$!
echo "  Streamlit started (PID: $STREAMLIT_PID)"

sleep 3

echo ""
echo "✅ Checking Streamlit status..."
if ps -p $STREAMLIT_PID > /dev/null; then
    echo "  ✅ Streamlit is running"
    echo "  📱 Access at: http://18.219.148.57:8501"
else
    echo "  ❌ Streamlit failed to start"
    echo "  Check logs: tail -f logs/streamlit.log"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ STREAMLIT FRONTEND READY!"
echo "========================================"
echo ""
echo "🎯 Autocomplete features:"
echo "   • Type 3+ characters in Competition Slug"
echo "   • Suggestions will appear automatically"
echo "   • Click a suggestion to auto-fill"
echo ""
echo "🔗 URLs:"
echo "   Frontend: http://18.219.148.57:8501"
echo "   Backend:  http://18.219.148.57:5000"

