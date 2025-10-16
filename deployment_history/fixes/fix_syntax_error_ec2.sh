#!/bin/bash
# Quick fix for the syntax error on EC2

echo "🔧 Fixing syntax error in llm_loader.py..."

# Navigate to project directory
cd /home/ubuntu/Kaggle-competition-assist

# Activate virtual environment
source venv/bin/activate

# Remove the extra closing parenthesis
sed -i '686d' llms/llm_loader.py

# Verify the fix
echo ""
echo "Testing imports..."
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

if not errors:
    print("\n🎉 ALL IMPORTS WORKING!")
else:
    print(f"\n⚠️  {len(errors)} errors remain")
PYEOF

echo ""
echo "Restarting backend service..."
sudo systemctl restart kaggle-backend

echo ""
echo "Waiting for service to start..."
sleep 5

echo ""
echo "Checking backend status..."
sudo systemctl status kaggle-backend --no-pager -n 10

echo ""
echo "Testing health endpoint..."
sleep 2
curl -f http://localhost:5000/health && echo "✅ Backend is healthy!" || echo "❌ Health check failed"


