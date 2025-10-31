# Backend V2.0 - Quick Start Guide

## ✅ **What We Just Created**

### **backend_v2.py**
- ✅ Same structure as `minimal_backend.py`
- ✅ **MasterOrchestrator** integrated (V2.0 intelligence!)
- ✅ All session management endpoints
- ✅ Health check endpoint
- ✅ Query endpoint at `/component-orchestrator/query`

### **Key Differences from V1.0:**
```python
# V1.0 (minimal_backend.py)
ComponentOrchestrator → Simple routing

# V2.0 (backend_v2.py)
MasterOrchestrator → Intelligent routing with:
  - UnifiedIntelligenceLayer (smart query classification)
  - HybridAgentRouter (intelligent agent selection)
  - Multiple orchestration modes (CrewAI, AutoGen, LangGraph, Dynamic)
```

---

## 🚀 **How to Start Backend V2.0**

### **Step 1: Stop Current Backend**
In your backend terminal:
```powershell
Ctrl+C
```

### **Step 2: Start Backend V2.0**
```powershell
python backend_v2.py
```

### **Step 3: Wait for Initialization**
Look for these messages:
```
[OK] Environment variables loaded from .env file
[OK] Kaggle API integration loaded successfully
[OK] V2.0 MasterOrchestrator loaded successfully
[INITIALIZING] V2.0 MasterOrchestrator...
[OK] V2.0 MasterOrchestrator initialized successfully
[OK]   - CrewAI, AutoGen, LangGraph, Dynamic modes ready
[OK]   - Unified Intelligence Layer active
[OK]   - Hybrid Agent Router active
[OK] ChromaDB pipeline initialized successfully
================================================================================
KAGGLE COPILOT ASSISTANT - BACKEND V2.0
================================================================================
[INFO] Health check: http://localhost:5000/health
[INFO] Query endpoint: http://localhost:5000/component-orchestrator/query
[INFO] V2.0 MasterOrchestrator: ACTIVE
================================================================================
 * Running on http://127.0.0.1:5000
```

---

## ✅ **Frontend Already Compatible!**

**Good news:** The frontend is already pointing to the correct endpoint!
```python
# streamlit_frontend/app.py
f"{BACKEND_URL}/component-orchestrator/query"  # ✅ This works with V2.0!
```

**No frontend changes needed!** Just refresh the Streamlit page after starting backend_v2.py.

---

## 🧪 **How to Test V2.0**

### **Test 1: Health Check**
```powershell
curl http://localhost:5000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "version": "2.0",
  "orchestrator": "MasterOrchestrator",
  "timestamp": "..."
}
```

### **Test 2: Initialize Session**
1. Refresh Streamlit page
2. Enter username and competition (e.g., `titanic`)
3. Click "Initialize Session"
4. Should see: "Session initialized successfully!"

### **Test 3: Send Query**
Ask: **"What is the evaluation metric?"**

**Expected in backend logs:**
```
[V2.0 QUERY] User: your_username
[V2.0 QUERY] Competition: titanic
[V2.0 QUERY] Query: What is the evaluation metric?
[V2.0] Routing through MasterOrchestrator...
[V2.0] Query processed in X.XXs
[V2.0] Strategy: simple_agent / multi_agent / langgraph / etc.
[V2.0] Agents: [list of agents used]
[V2.0] Mode: dynamic
```

---

## 📊 **What You Should See**

### **Simple Queries:**
- Query: "What is the evaluation metric?"
- Strategy: `simple_agent`
- Agents: `['CompetitionSummaryAgent']` (1 agent)
- Mode: `dynamic`

### **Complex Queries:**
- Query: "Give me ideas to improve my model"
- Strategy: `multi_agent` or `langgraph`
- Agents: `['IdeaInitiatorAgent', 'NotebookExplainerAgent', 'DataSectionAgent']` (multiple agents)
- Mode: `crewai` or `langgraph`

---

## ⚠️ **Expected Behavior (For Now)**

### ✅ **Working:**
- Session initialization
- Query routing through MasterOrchestrator
- Intelligent agent selection
- Multi-agent orchestration

### ⚠️ **Empty Responses:**
- RAG agents may return empty responses
- **Why?** ChromaDB has no data yet
- **Fix:** Phase 4 (populate ChromaDB) - we'll do this next!

### ✅ **No Errors:**
- No timeout errors
- No connection errors
- No crashes

---

## 🎯 **Next Steps**

1. **Start backend_v2.py** ✅
2. **Test with Streamlit** ✅
3. **Verify V2.0 routing works** ✅
4. **Populate ChromaDB** (Phase 4 - optional for now)
5. **Validate agents** (Phase 5 - optional for now)

---

## 🚀 **Ready to Launch!**

**In your backend terminal:**
```powershell
python backend_v2.py
```

**Then refresh your Streamlit page and test!**

Let me know when you see the initialization messages! 🎉

