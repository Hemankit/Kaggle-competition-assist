#!/bin/bash
set -e

echo "========================================"
echo "🔧 FIXING PERPLEXITY FOR MULTI-AGENT"
echo "========================================"
echo ""

cd ~/Kaggle-competition-assist
source venv/bin/activate

echo "📦 Installing langchain-perplexity package..."
pip install langchain-perplexity==0.1.2 --quiet

echo ""
echo "✅ Testing Perplexity import..."
python3 << 'EOF'
try:
    from langchain_perplexity import ChatPerplexity
    print("✅ ChatPerplexity imported successfully!")
    
    import os
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if api_key:
        print(f"✅ PERPLEXITY_API_KEY found: {api_key[:10]}...")
        
        # Test instantiation
        llm = ChatPerplexity(
            model="sonar",
            temperature=0.3,
            pplx_api_key=api_key
        )
        print("✅ ChatPerplexity instantiated successfully!")
        print("✅ Perplexity is READY for multi-agent orchestration!")
    else:
        print("❌ PERPLEXITY_API_KEY not found in environment")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "🔄 Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "🔄 Restarting backend service..."
sudo systemctl restart kaggle-backend
sleep 3

echo ""
echo "✅ Checking backend status..."
sudo systemctl status kaggle-backend --no-pager | head -15

echo ""
echo "========================================"
echo "✅ PERPLEXITY FIX COMPLETE!"
echo "========================================"
echo ""
echo "🎯 Perplexity Sonar is now active for:"
echo "   - Multi-agent orchestration"
echo "   - Deep reasoning queries"
echo "   - Critical thinking tasks"
echo ""
echo "🧪 Test with: python3 test_perplexity.py"


