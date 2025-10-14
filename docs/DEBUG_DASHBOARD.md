# 🔧 LangGraph Debug Dashboard

## 📋 Overview

The debug dashboard allows you (the developer) to visualize LangGraph execution flows and see which agents were activated for each query. **This is hidden from end users** and only accessible via special `/debug/*` endpoints.

---

## 🎯 Purpose

- **Debugging**: See which agents were triggered for each query
- **Performance Analysis**: Track response times and cache hits
- **Agent Flow Visualization**: View LangGraph node activations
- **Query History**: Review recent queries and their routing

---

## 🔗 Access Points

### **1. Full Dashboard** (Recommended)
```
http://localhost:5000/debug/dashboard
```

**Features:**
- 📊 LangGraph visualization image
- 📋 Table of recent query executions
- ⚡ Cache hit/miss indicators
- 🤖 Agent activation list
- ⏱️ Response time tracking

### **2. LangGraph Visualization Only**
```
http://localhost:5000/debug/langgraph
```

Returns: PNG image of the LangGraph structure

### **3. Execution Traces (JSON)**
```
http://localhost:5000/debug/traces
```

Returns: JSON with last 10 query executions

Example response:
```json
{
  "total_traces": 25,
  "recent_traces": [
    {
      "query_id": "abc123...",
      "query": "What is the evaluation metric?",
      "timestamp": "2025-10-12T14:30:45",
      "agents_used": ["CompetitionSummaryAgent"],
      "nodes_activated": ["preprocessing", "router", "evaluation", "aggregation"],
      "response_time_ms": 1200,
      "cache_hit": false
    },
    ...
  ]
}
```

### **4. Trace-Specific Visualization**
```
http://localhost:5000/debug/langgraph/trace/<query_id>
```

Returns: PNG image with **highlighted nodes** for that specific query execution

---

## 🎨 Dashboard Features

### **Visual Elements:**

1. **Graph Visualization**
   - Shows all LangGraph nodes and edges
   - Displays workflow structure
   - Can highlight activated paths (if supported)

2. **Query Execution Table**
   - **Time**: When the query was executed
   - **Query**: User's question (truncated to 60 chars)
   - **Agents**: Which agents were used
   - **Response Time**: How long it took (ms)
   - **Cache Status**: 
     - ✅ **HIT** (green) = Retrieved from cache
     - ❌ **MISS** (red) = Full execution

3. **Color Coding**
   - 🟢 Green = Cache hits, fast responses
   - 🔴 Red = Cache misses, full execution
   - 🟡 Yellow = Agent names

---

## 📊 Understanding the Data

### **Nodes Activated:**

Different query types activate different node paths:

**Evaluation Query:**
```
preprocessing → router → evaluation → competition_summary → memory_update → meta_monitor → aggregation
```

**Cache Hit:**
```
preprocessing → cache_lookup → aggregation
```

**Error Diagnosis:**
```
preprocessing → router → error_diagnosis → memory_update → meta_monitor → aggregation
```

**Multi-Agent Orchestration:**
```
preprocessing → router → reasoning → execution_bridge → memory_update → meta_monitor → meta_intervention → aggregation
```

### **Agent Activation:**

- `CompetitionSummaryAgent` - Evaluation/overview queries
- `NotebookExplainerAgent` - Notebook analysis
- `DiscussionHelperAgent` - Community discussions
- `ErrorDiagnosisAgent` - Code error detection
- `CodeFeedbackAgent` - Code review
- `ProgressMonitorAgent` - Progress tracking
- `IdeaInitiatorAgent` - Idea generation
- `MultiHopReasoningAgent` - Complex reasoning
- `TimelineCoachAgent` - Timeline/planning
- `CommunityEngagementAgent` - Feedback analysis

---

## 🔍 Use Cases

### **1. Debugging Query Routing**

**Problem**: User asks "What is the evaluation metric?" but gets wrong response.

**Debug Steps:**
1. Open dashboard: `http://localhost:5000/debug/dashboard`
2. Find the query in the table
3. Check `Agents` column - should show `CompetitionSummaryAgent`
4. If wrong agent, check routing logic in `handle_component_query()`

### **2. Performance Analysis**

**Problem**: Queries are slow.

**Debug Steps:**
1. Check `Response Time` column
2. Look for `Cache` status
3. First query should be slow (25-30s) ❌ MISS
4. Repeat query should be fast (1-2s) ✅ HIT

### **3. Cache Verification**

**Problem**: Cache not working.

**Debug Steps:**
1. Ask a simple query: "What is the evaluation metric?"
2. Check dashboard - should show ❌ MISS, ~25s
3. Ask SAME query again
4. Check dashboard - should show ✅ HIT, ~1-2s

### **4. Agent Flow Visualization**

**Problem**: Want to see full LangGraph structure.

**Debug Steps:**
1. Open: `http://localhost:5000/debug/langgraph`
2. View the PNG image
3. Identify all nodes and edges
4. Understand workflow paths

---

## 🛡️ Security Note

**These endpoints are for DEBUGGING ONLY and should:**

- ❌ **NOT** be exposed to end users
- ❌ **NOT** be accessible in production (unless behind authentication)
- ✅ **ONLY** be used during development
- ✅ **BE** removed or protected in production deployment

---

## 🔧 Technical Details

### **Storage:**

Execution traces are stored in-memory:
```python
execution_traces = {}  # {query_id: trace_data}
MAX_TRACES = 50  # Keeps last 50 traces
```

**Note**: Traces are **lost on server restart** (not persistent).

### **Trace Data Structure:**

```python
{
    "query_id": "unique-uuid",
    "query": "User's question",
    "timestamp": "2025-10-12T14:30:45",
    "agents_used": ["agent1", "agent2"],
    "nodes": ["node1", "node2", "node3"],
    "response_time_ms": 1200,
    "cache_hit": True/False,
    "response_type": "evaluation"
}
```

---

## 🎯 Quick Start

1. **Start Backend:**
   ```bash
   python minimal_backend.py
   ```

2. **Open Dashboard:**
   ```
   http://localhost:5000/debug/dashboard
   ```

3. **Make Some Queries:**
   - Use the Streamlit frontend to ask questions
   - Each query will be tracked

4. **Refresh Dashboard:**
   - Click "🔄 Refresh" button
   - Or reload the page

5. **Analyze Results:**
   - Check which agents were used
   - Verify cache hits
   - Track response times

---

## 🚀 Future Enhancements

Potential additions:
- ✅ Persistent storage (SQLite/PostgreSQL)
- ✅ Authentication for production use
- ✅ Real-time updates (WebSockets)
- ✅ Export traces to CSV/JSON
- ✅ Filter by date/query type
- ✅ Advanced analytics dashboard

---

## 📞 Support

If the dashboard isn't working:

1. **Check Backend Logs:**
   ```
   [OK] LangGraph visualization loaded successfully
   ```

2. **Verify Endpoints:**
   ```bash
   curl http://localhost:5000/debug/traces
   ```

3. **Check Dependencies:**
   - `langgraph` installed
   - `workflows` folder exists
   - `draw_mermaid_png()` supported

---

**🔧 Happy Debugging!**





