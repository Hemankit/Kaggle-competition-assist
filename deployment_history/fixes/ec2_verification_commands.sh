#!/bin/bash
# EC2 Backend Verification Script
# Copy and paste this entire script into your EC2 terminal

echo "╔════════════════════════════════════════════════════════╗"
echo "║       BACKEND VERIFICATION & RESTART                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Navigate to project
cd ~/Kaggle-competition-assist

# Activate virtual environment
source venv/bin/activate

# Test imports
echo ""
echo "🔍 Testing all critical imports..."
echo "════════════════════════════════════════════════════════"
python << 'PYEOF'
import sys
sys.path.insert(0, '/home/ubuntu/Kaggle-competition-assist')
from dotenv import load_dotenv
load_dotenv()

errors = []

try:
    from orchestrators.component_orchestrator import ComponentOrchestrator
    print("✅ ComponentOrchestrator")
except Exception as e:
    errors.append(f"ComponentOrchestrator: {e}")
    print(f"❌ ComponentOrchestrator: {e}")

try:
    from agents.competition_summary_agent import CompetitionSummaryAgent
    print("✅ CompetitionSummaryAgent")
except Exception as e:
    errors.append(f"CompetitionSummaryAgent: {e}")
    print(f"❌ CompetitionSummaryAgent: {e}")

try:
    from Kaggle_Fetcher.kaggle_api_client import get_competition_details
    print("✅ Kaggle API Client")
except Exception as e:
    errors.append(f"Kaggle API Client: {e}")
    print(f"❌ Kaggle API Client: {e}")

try:
    from llms.llm_loader import get_llm_from_config
    print("✅ LLM Loader")
except Exception as e:
    errors.append(f"LLM Loader: {e}")
    print(f"❌ LLM Loader: {e}")

try:
    from RAG_pipeline_chromadb.chromadb_rag_pipeline import ChromaDBRAGPipeline
    print("✅ ChromaDB RAG Pipeline")
except Exception as e:
    errors.append(f"ChromaDB RAG Pipeline: {e}")
    print(f"❌ ChromaDB RAG Pipeline: {e}")

print("")
if not errors:
    print("🎉 ALL IMPORTS SUCCESSFUL!")
else:
    print(f"⚠️  {len(errors)} import errors detected")
    for error in errors:
        print(f"   • {error}")
PYEOF

# Restart backend service
echo ""
echo "════════════════════════════════════════════════════════"
echo "🔄 Restarting backend service..."
sudo systemctl restart kaggle-backend

# Wait for service to start
echo "⏳ Waiting 5 seconds for service to start..."
sleep 5

# Check service status
echo ""
echo "════════════════════════════════════════════════════════"
echo "📊 Service Status:"
sudo systemctl status kaggle-backend --no-pager -n 15

# Test health endpoint
echo ""
echo "════════════════════════════════════════════════════════"
echo "🏥 Testing health endpoint..."
sleep 2

if curl -f http://localhost:5000/health 2>/dev/null; then
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "✅ BACKEND IS HEALTHY AND READY!"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL! 🎉"
    echo ""
    echo "Your backend is now running at:"
    echo "  • Health: http://localhost:5000/health"
    echo "  • API: http://localhost:5000/api/chat"
    echo ""
    echo "To test with a query:"
    echo "  curl -X POST http://localhost:5000/api/chat \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"competition_id\": \"titanic\", \"user_query\": \"What is this competition about?\"}'"
    echo ""
else
    echo ""
    echo "════════════════════════════════════════════════════════"
    echo "❌ HEALTH CHECK FAILED"
    echo "════════════════════════════════════════════════════════"
    echo ""
    echo "Troubleshooting steps:"
    echo ""
    echo "1. Check recent logs:"
    echo "   sudo journalctl -u kaggle-backend -n 50 --no-pager"
    echo ""
    echo "2. Check if port 5000 is in use:"
    echo "   sudo netstat -tlnp | grep 5000"
    echo ""
    echo "3. Try running manually to see errors:"
    echo "   cd ~/Kaggle-competition-assist"
    echo "   source venv/bin/activate"
    echo "   python minimal_backend.py"
    echo ""
fi


