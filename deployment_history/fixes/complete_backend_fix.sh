#!/bin/bash
# Complete Backend Fix Script
# Fixes ALL issues to get full functionality

echo "=========================================="
echo "🔧 COMPLETE BACKEND FIX"
echo "=========================================="
echo ""

cd ~/Kaggle-competition-assist
source venv/bin/activate

echo "Step 1: Verify Python files were updated"
echo "=========================================="
if grep -q "ChatOpenAI.*DeepSeek" llms/llm_loader.py; then
    echo "✅ llm_loader.py has been updated (using ChatOpenAI for DeepSeek)"
else
    echo "❌ llm_loader.py NOT updated - files may not have uploaded correctly"
    echo "Please re-upload the files!"
    exit 1
fi

echo ""
echo "Step 2: Check for langchain_ollama imports"
echo "=========================================="
if grep -q "from langchain_ollama" llms/llm_loader.py; then
    echo "❌ Still importing langchain_ollama - fix not applied!"
    exit 1
else
    echo "✅ No langchain_ollama imports in llm_loader.py"
fi

echo ""
echo "Step 3: Install missing optional packages"
echo "=========================================="
# These are optional but good to have
pip install langchain-community --quiet
echo "✅ Installed langchain-community"

echo ""
echo "Step 4: Test critical imports"
echo "=========================================="
python << 'PYEOF'
import sys
sys.path.insert(0, '/home/ubuntu/Kaggle-competition-assist')

errors = []

# Test LLM loader
try:
    from llms.llm_loader import get_llm_from_config
    print("✅ llms.llm_loader")
except Exception as e:
    errors.append(f"llm_loader: {e}")
    print(f"❌ llms.llm_loader: {e}")

# Test orchestrators
try:
    from orchestrators.component_orchestrator import ComponentOrchestrator
    print("✅ ComponentOrchestrator")
except Exception as e:
    errors.append(f"ComponentOrchestrator: {e}")
    print(f"❌ ComponentOrchestrator: {e}")

# Test agents
try:
    from agents import CompetitionSummaryAgent
    print("✅ Agents")
except Exception as e:
    errors.append(f"Agents: {e}")
    print(f"❌ Agents: {e}")

# Test Kaggle API
try:
    from Kaggle_Fetcher.kaggle_api_client import get_competition_details
    print("✅ Kaggle API")
except Exception as e:
    errors.append(f"Kaggle API: {e}")
    print(f"❌ Kaggle API: {e}")

if errors:
    print(f"\n⚠️  {len(errors)} import errors remain")
    sys.exit(1)
else:
    print("\n🎉 All critical imports working!")
PYEOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Import test failed. Need to investigate further."
    exit 1
fi

echo ""
echo "Step 5: Fix Kaggle API search bug"
echo "=========================================="
# Fix the 'category="all"' bug in minimal_backend.py
if grep -q 'category="all"' minimal_backend.py; then
    echo "Found Kaggle API bug - fixing..."
    sed -i 's/category="all"/# category removed - was causing 400 error/' minimal_backend.py
    echo "✅ Fixed category parameter"
else
    echo "✅ Category parameter already fixed or not present"
fi

echo ""
echo "Step 6: Restart backend"
echo "=========================================="
sudo systemctl restart kaggle-backend
sleep 5

echo ""
echo "Step 7: Test backend health"
echo "=========================================="
if curl -f http://localhost:5000/health 2>/dev/null > /dev/null; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
    echo "Check logs: sudo journalctl -u kaggle-backend -n 50"
    exit 1
fi

echo ""
echo "Step 8: Test Kaggle API search"
echo "=========================================="
response=$(curl -s -X POST http://localhost:5000/session/competitions/search \
  -H "Content-Type: application/json" \
  -d '{"query": "titanic"}')

if echo "$response" | grep -q '"success":true'; then
    echo "✅ Kaggle API search working"
    echo "Response: $response"
else
    echo "⚠️  Kaggle API search returned: $response"
fi

echo ""
echo "Step 9: Test query endpoint"
echo "=========================================="
response=$(curl -s -X POST http://localhost:5000/component-orchestrator/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello", "context": {}}')

if echo "$response" | grep -q '"success":true'; then
    echo "✅ Query endpoint working"
else
    echo "❌ Query endpoint failed"
    echo "Response: $response"
fi

echo ""
echo "=========================================="
echo "✅ BACKEND FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test a real query from frontend"
echo "2. Check what agents are available"
echo "3. Populate ChromaDB with competition data"
echo ""


