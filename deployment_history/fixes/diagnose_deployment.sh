#!/bin/bash
# ===================================================================
# Deployment Diagnostic Script
# ===================================================================
# Run this script to identify why the deployed app returns placeholder
# responses instead of real competition data.
# ===================================================================

echo "=========================================="
echo "🔍 Deployment Diagnostic Tool"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/ubuntu/Kaggle-competition-assist"
VENV_DIR="$PROJECT_DIR/venv"

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local success_message="$3"
    local failure_message="$4"
    
    echo -e "${BLUE}[TEST]${NC} $test_name"
    
    if eval "$test_command"; then
        echo -e "${GREEN}  ✅ PASS${NC} - $success_message"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}  ❌ FAIL${NC} - $failure_message"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "Running diagnostics..."
echo ""

# ===================================================================
# 1. PROJECT STRUCTURE
# ===================================================================
echo "=========================================="
echo "1. Project Structure"
echo "=========================================="

run_test "Project directory exists" \
    "[ -d '$PROJECT_DIR' ]" \
    "Project directory found" \
    "Project directory not found at $PROJECT_DIR"

run_test "minimal_backend.py exists" \
    "[ -f '$PROJECT_DIR/minimal_backend.py' ]" \
    "Backend file found" \
    "Backend file missing"

run_test "Virtual environment exists" \
    "[ -d '$VENV_DIR' ]" \
    "Virtual environment found" \
    "Virtual environment not found"

run_test ".env file exists" \
    "[ -f '$PROJECT_DIR/.env' ]" \
    ".env file found" \
    ".env file missing - create it!"

echo ""

# ===================================================================
# 2. PYTHON ENVIRONMENT
# ===================================================================
echo "=========================================="
echo "2. Python Environment"
echo "=========================================="

run_test "Python 3.11 installed" \
    "command -v python3.11 &> /dev/null" \
    "$(python3.11 --version 2>&1)" \
    "Python 3.11 not found"

if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate" 2>/dev/null
    
    run_test "Flask installed" \
        "python -c 'import flask' 2>/dev/null" \
        "Flask available" \
        "Flask not installed in venv"
    
    run_test "Playwright installed" \
        "python -c 'import playwright' 2>/dev/null" \
        "Playwright package available" \
        "Playwright not installed"
    
    run_test "Playwright browsers installed" \
        "playwright --version &> /dev/null" \
        "$(playwright --version 2>&1)" \
        "Playwright browsers not installed - run: playwright install --with-deps"
    
    run_test "ChromaDB installed" \
        "python -c 'import chromadb' 2>/dev/null" \
        "ChromaDB available" \
        "ChromaDB not installed"
    
    run_test "LangChain installed" \
        "python -c 'import langchain' 2>/dev/null" \
        "LangChain available" \
        "LangChain not installed"
fi

echo ""

# ===================================================================
# 3. ENVIRONMENT VARIABLES
# ===================================================================
echo "=========================================="
echo "3. Environment Variables"
echo "=========================================="

if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
    
    run_test "KAGGLE_USERNAME set" \
        "[ ! -z '$KAGGLE_USERNAME' ] && [ '$KAGGLE_USERNAME' != 'your-kaggle-username' ]" \
        "Kaggle username configured" \
        "KAGGLE_USERNAME not set or using placeholder"
    
    run_test "KAGGLE_KEY set" \
        "[ ! -z '$KAGGLE_KEY' ] && [ '$KAGGLE_KEY' != 'your-kaggle-api-key' ]" \
        "Kaggle API key configured" \
        "KAGGLE_KEY not set or using placeholder"
    
    run_test "GROQ_API_KEY set" \
        "[ ! -z '$GROQ_API_KEY' ] && [ '$GROQ_API_KEY' != 'your-groq-api-key' ]" \
        "Groq API key configured" \
        "GROQ_API_KEY not set or using placeholder"
    
    run_test "GOOGLE_API_KEY set" \
        "[ ! -z '$GOOGLE_API_KEY' ] && [ '$GOOGLE_API_KEY' != 'your-google-api-key' ]" \
        "Google API key configured" \
        "GOOGLE_API_KEY not set or using placeholder"
    
    run_test "ENVIRONMENT set to production" \
        "[ '$ENVIRONMENT' = 'production' ] || [ '$ENVIRONMENT' = 'development' ]" \
        "Environment: $ENVIRONMENT" \
        "ENVIRONMENT variable not set properly"
else
    echo -e "${RED}  ❌ .env file not found - skipping environment checks${NC}"
    ((TESTS_FAILED+=5))
fi

echo ""

# ===================================================================
# 4. REQUIRED DIRECTORIES
# ===================================================================
echo "=========================================="
echo "4. Required Directories"
echo "=========================================="

run_test "chroma_db directory exists" \
    "[ -d '$PROJECT_DIR/chroma_db' ]" \
    "ChromaDB directory found" \
    "ChromaDB directory missing"

run_test "data directory exists" \
    "[ -d '$PROJECT_DIR/data' ]" \
    "Data directory found" \
    "Data directory missing"

run_test "logs directory exists" \
    "[ -d '$PROJECT_DIR/logs' ]" \
    "Logs directory found" \
    "Logs directory missing"

echo ""

# ===================================================================
# 5. SERVICES STATUS
# ===================================================================
echo "=========================================="
echo "5. System Services"
echo "=========================================="

run_test "Backend service exists" \
    "systemctl list-unit-files | grep -q kaggle-backend" \
    "Backend service registered" \
    "Backend service not registered"

if systemctl list-unit-files | grep -q kaggle-backend; then
    run_test "Backend service running" \
        "sudo systemctl is-active --quiet kaggle-backend" \
        "Backend is active" \
        "Backend is not running - check logs: sudo journalctl -u kaggle-backend -n 50"
fi

run_test "Frontend service exists" \
    "systemctl list-unit-files | grep -q kaggle-frontend" \
    "Frontend service registered" \
    "Frontend service not registered"

if systemctl list-unit-files | grep -q kaggle-frontend; then
    run_test "Frontend service running" \
        "sudo systemctl is-active --quiet kaggle-frontend" \
        "Frontend is active" \
        "Frontend is not running - check logs: sudo journalctl -u kaggle-frontend -n 50"
fi

echo ""

# ===================================================================
# 6. NETWORK & PORTS
# ===================================================================
echo "=========================================="
echo "6. Network & Ports"
echo "=========================================="

run_test "Port 5000 (backend) listening" \
    "netstat -tuln 2>/dev/null | grep -q ':5000' || ss -tuln 2>/dev/null | grep -q ':5000'" \
    "Backend port is listening" \
    "Backend not listening on port 5000"

run_test "Port 8501 (frontend) listening" \
    "netstat -tuln 2>/dev/null | grep -q ':8501' || ss -tuln 2>/dev/null | grep -q ':8501'" \
    "Frontend port is listening" \
    "Frontend not listening on port 8501"

run_test "Backend health endpoint responds" \
    "curl -s -f http://localhost:5000/health > /dev/null 2>&1" \
    "Health check successful" \
    "Health check failed - backend may not be running"

if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost:5000/health)
    echo "  Health response: $HEALTH_RESPONSE"
fi

echo ""

# ===================================================================
# 7. CRITICAL IMPORTS TEST
# ===================================================================
echo "=========================================="
echo "7. Python Imports (Critical Components)"
echo "=========================================="

if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    cd "$PROJECT_DIR"
    
    # Create a test script
    cat > /tmp/test_imports.py << 'EOF'
import sys
import os
sys.path.insert(0, '/home/ubuntu/Kaggle-competition-assist')

from dotenv import load_dotenv
load_dotenv()

tests = []

try:
    from orchestrators.component_orchestrator import ComponentOrchestrator
    tests.append(("ComponentOrchestrator", True, "Multi-agent system available"))
except Exception as e:
    tests.append(("ComponentOrchestrator", False, str(e)))

try:
    from Kaggle_Fetcher.kaggle_api_client import get_competition_details
    tests.append(("Kaggle API", True, "Can fetch competition data"))
except Exception as e:
    tests.append(("Kaggle API", False, str(e)))

try:
    from scraper.overview_scraper import OverviewScraper
    tests.append(("Playwright Scraper", True, "Web scraping available"))
except Exception as e:
    tests.append(("Playwright Scraper", False, str(e)))

try:
    from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline
    tests.append(("ChromaDB RAG", True, "Cache system available"))
except Exception as e:
    tests.append(("ChromaDB RAG", False, str(e)))

try:
    from agents.competition_summary_agent import CompetitionSummaryAgent
    tests.append(("Agents", True, "All agents loaded"))
except Exception as e:
    tests.append(("Agents", False, str(e)))

for name, success, message in tests:
    if success:
        print(f"PASS|{name}|{message}")
    else:
        print(f"FAIL|{name}|{message}")
EOF
    
    # Run the test
    IMPORT_RESULTS=$(python /tmp/test_imports.py 2>&1)
    
    while IFS='|' read -r status name message; do
        if [ "$status" = "PASS" ]; then
            echo -e "${GREEN}  ✅ $name${NC} - $message"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}  ❌ $name${NC} - $message"
            ((TESTS_FAILED++))
        fi
    done <<< "$IMPORT_RESULTS"
    
    rm /tmp/test_imports.py
fi

echo ""

# ===================================================================
# 8. RECENT ERROR LOGS
# ===================================================================
echo "=========================================="
echo "8. Recent Error Logs"
echo "=========================================="

echo -e "${YELLOW}Backend errors (last 10 lines):${NC}"
if [ -f "$PROJECT_DIR/logs/backend-error.log" ]; then
    tail -n 10 "$PROJECT_DIR/logs/backend-error.log" | grep -i error || echo "  No recent errors"
else
    sudo journalctl -u kaggle-backend -n 10 --no-pager | grep -i error || echo "  No recent errors"
fi

echo ""
echo -e "${YELLOW}Frontend errors (last 10 lines):${NC}"
if [ -f "$PROJECT_DIR/logs/frontend-error.log" ]; then
    tail -n 10 "$PROJECT_DIR/logs/frontend-error.log" | grep -i error || echo "  No recent errors"
else
    sudo journalctl -u kaggle-frontend -n 10 --no-pager | grep -i error || echo "  No recent errors"
fi

echo ""

# ===================================================================
# 9. FUNCTIONAL TEST
# ===================================================================
echo "=========================================="
echo "9. Functional Test (API Call)"
echo "=========================================="

if curl -s -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Testing query endpoint with Titanic competition..."
    
    # Test the actual query endpoint
    TEST_QUERY='{"query": "What is the evaluation metric?", "competition_slug": "titanic", "user_id": "test-diagnostic"}'
    
    echo "Sending test query..."
    RESPONSE=$(curl -s -X POST http://localhost:5000/session/new \
        -H "Content-Type: application/json" \
        -d "$TEST_QUERY" \
        --max-time 30)
    
    if echo "$RESPONSE" | grep -q "accuracy\|classification\|survival\|metric"; then
        echo -e "${GREEN}  ✅ API returns real competition data${NC}"
        echo "  Response preview: $(echo $RESPONSE | cut -c1-200)..."
        ((TESTS_PASSED++))
    elif echo "$RESPONSE" | grep -q "Check competition description\|Not specified"; then
        echo -e "${RED}  ❌ API returns placeholder data (THE MAIN ISSUE!)${NC}"
        echo "  This means scraping/fetching is not working properly"
        echo "  Most likely cause: Playwright browsers not installed"
        echo "  Fix: Run 'playwright install --with-deps' in the virtual environment"
        ((TESTS_FAILED++))
    else
        echo -e "${YELLOW}  ⚠️  Unexpected response${NC}"
        echo "  Response: $RESPONSE"
    fi
else
    echo -e "${RED}  ❌ Cannot test - backend not responding${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# ===================================================================
# SUMMARY & RECOMMENDATIONS
# ===================================================================
echo "=========================================="
echo "📊 Diagnostic Summary"
echo "=========================================="
echo ""
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Your deployment should be working correctly.${NC}"
    echo ""
    echo "If you're still seeing placeholder responses:"
    echo "  1. Clear browser cache"
    echo "  2. Try a different competition (e.g., 'house-prices-advanced-regression-techniques')"
    echo "  3. Wait 30 seconds for first query (scraping takes time)"
else
    echo -e "${YELLOW}⚠️  Issues detected. Recommendations:${NC}"
    echo ""
    
    # Specific recommendations based on failures
    if echo "$IMPORT_RESULTS" | grep -q "FAIL|Playwright"; then
        echo "🔧 CRITICAL: Playwright not working"
        echo "   Fix: Run these commands:"
        echo "   cd $PROJECT_DIR"
        echo "   source venv/bin/activate"
        echo "   playwright install --with-deps chromium"
        echo ""
    fi
    
    if [ ! -f "$PROJECT_DIR/.env" ] || [ -z "$KAGGLE_KEY" ]; then
        echo "🔧 CRITICAL: API keys not configured"
        echo "   Fix: Edit .env file with your actual API keys:"
        echo "   nano $PROJECT_DIR/.env"
        echo ""
    fi
    
    if ! sudo systemctl is-active --quiet kaggle-backend; then
        echo "🔧 Backend service not running"
        echo "   Fix: Check logs and restart:"
        echo "   sudo journalctl -u kaggle-backend -n 50"
        echo "   sudo systemctl restart kaggle-backend"
        echo ""
    fi
    
    echo "💡 Quick fix: Run the automated fix script:"
    echo "   cd $PROJECT_DIR"
    echo "   bash fix_ec2_deployment.sh"
fi

echo ""
echo "=========================================="
echo "📝 Useful Commands"
echo "=========================================="
echo ""
echo "View backend logs:  sudo journalctl -u kaggle-backend -f"
echo "View frontend logs: sudo journalctl -u kaggle-frontend -f"
echo "Restart services:   sudo systemctl restart kaggle-backend kaggle-frontend"
echo "Check service:      sudo systemctl status kaggle-backend"
echo "Run fix script:     bash $PROJECT_DIR/fix_ec2_deployment.sh"
echo ""
echo "=========================================="


