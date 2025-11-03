# 🔗 Context Retention Issue - Followup Query Handling

## 🎯 **PROBLEM:**

**Test Case that Failed:**
```
Query 1: "What are people discussing about feature engineering?"
✅ Response: MAGICAL synthesis with consensus, debates, patterns

Query 2: "Tell me more about consensus on family-based features"
❌ Response: "No relevant information found"
```

**Root Cause:** Backend treats each query independently, without conversation context.

---

## 📊 **CURRENT BEHAVIOR:**

### **What Works:**
- ✅ Single queries with full context ("What features do notebooks use?")
- ✅ Agent selection based on query content
- ✅ ChromaDB retrieval with competition filtering

### **What Fails:**
- ❌ Followup queries referring to previous response ("Tell me more about X")
- ❌ Queries with pronouns ("What about it?", "Explain that further")
- ❌ Conversational context ("You mentioned Y earlier...")

---

## 🔍 **TECHNICAL ANALYSIS:**

### **Current Flow:**
```
Frontend → Backend → Agent
    ↓         ↓         ↓
  Query    Context    Fresh State
            ↓
    competition_slug
    kaggle_username
    session_id
            ↓
    [NO CONVERSATION HISTORY]
```

### **Missing Components:**
1. **Conversation History Storage**
   - Not currently stored in `user_context`
   - Not passed to agents
   - Not used in query analysis

2. **Context Window Management**
   - No mechanism to append previous Q&A
   - No pruning of old context

3. **Reference Resolution**
   - "Tell me more about X" requires knowing what X refers to
   - Requires parsing previous response to extract X

---

## 🏗️ **PROPOSED ARCHITECTURE:**

### **Option 1: Frontend-Managed Context (RECOMMENDED)**

**Why:** Stateless backend, simpler deployment, client controls context

```python
# Frontend sends:
{
    "query": "Tell me more about consensus on family-based features",
    "user_context": {
        "competition_slug": "titanic",
        "conversation_history": [
            {
                "role": "user",
                "content": "What are people discussing about feature engineering?"
            },
            {
                "role": "assistant", 
                "content": "[Previous MAGICAL response...]"
            }
        ]
    }
}

# Backend receives and uses:
full_context = "\n".join([
    f"{msg['role']}: {msg['content']}" 
    for msg in user_context.get('conversation_history', [])
])

enriched_query = f"""
Conversation History:
{full_context}

Current Query: {query}

Task: Answer the current query using context from conversation history.
"""
```

**Benefits:**
- ✅ Stateless backend (easier to scale)
- ✅ Frontend controls what context to send
- ✅ No backend storage needed
- ✅ User can clear context anytime

**Drawbacks:**
- ⚠️ Larger request payloads (minimal impact)
- ⚠️ Frontend must manage history

---

### **Option 2: Backend Session Storage**

**Why:** Backend manages state, frontend stays simple

```python
# Backend stores sessions in memory/Redis
sessions = {
    "session_abc123": {
        "competition_slug": "titanic",
        "conversation_history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "last_updated": datetime.now()
    }
}

# On query:
session_id = user_context.get("session_id")
session = sessions.get(session_id, {})
conversation_history = session.get("conversation_history", [])

# After response:
session["conversation_history"].append({"role": "user", "content": query})
session["conversation_history"].append({"role": "assistant", "content": response})
```

**Benefits:**
- ✅ Frontend stays simple
- ✅ Backend fully controls context

**Drawbacks:**
- ❌ Stateful backend (harder to scale)
- ❌ Requires session cleanup (memory leaks)
- ❌ Lost on backend restart

---

### **Option 3: Hybrid (Session Storage + Frontend Override)**

**Why:** Best of both worlds

```python
# Backend stores sessions, but frontend can override
session_history = get_session_history(session_id)
frontend_history = user_context.get("conversation_history", [])

# Prioritize frontend if provided (for manual context control)
conversation_history = frontend_history if frontend_history else session_history
```

**Benefits:**
- ✅ Automatic context for most cases
- ✅ Frontend can inject/modify context
- ✅ Fallback to frontend if session lost

**Drawbacks:**
- ⚠️ More complex implementation
- ⚠️ Potential conflicts (frontend vs backend state)

---

## 🎯 **RECOMMENDATION:**

**Start with Option 1 (Frontend-Managed Context)**

**Why:**
1. V2.0 backend is already complex - keep it stateless
2. Streamlit frontend already has session state (`st.session_state`)
3. Easier to test and debug (context is explicit in requests)
4. No backend storage/cleanup needed
5. Production deployment simpler (no session persistence)

**Implementation Priority:**
1. ✅ Document the issue (this file)
2. ⏳ Modify frontend to include `conversation_history` in `user_context`
3. ⏳ Modify backend to prepend conversation history to query
4. ⏳ Test with followup queries

---

## 🧪 **TEST CASES:**

### **Test 1: Simple Followup**
```
Q1: "What are people discussing about feature engineering?"
Q2: "Tell me more about consensus on family-based features"

Expected: Response synthesizes family-based features from previous response
```

### **Test 2: Pronoun Resolution**
```
Q1: "What evaluation metric is used?"
Q2: "How do I optimize for it?"

Expected: "it" resolves to the evaluation metric (e.g., "accuracy")
```

### **Test 3: Cross-Agent Followup**
```
Q1: "What features do top notebooks use?" (NotebookExplainerAgent)
Q2: "Are people discussing these features?" (DiscussionHelperAgent)

Expected: "these features" resolves to features from Q1 response
```

### **Test 4: Context Window Limit**
```
Q1-Q10: Long conversation
Q11: "What did you say first?"

Expected: If context pruned, explain that early messages are no longer in context
```

---

## 📏 **CONTEXT WINDOW LIMITS:**

### **Gemini 2.5 Flash:**
- **Input:** 1M tokens
- **Practical limit:** ~500K tokens (safety margin)
- **Typical conversation:** ~100-200 tokens per Q&A pair
- **Max conversation length:** ~1000 exchanges (way more than needed!)

### **Context Pruning Strategy:**
```python
# Keep last N exchanges (N=10 recommended)
MAX_HISTORY = 10

if len(conversation_history) > MAX_HISTORY * 2:
    # Keep first message (system/intro) + last N exchanges
    conversation_history = [
        conversation_history[0],  # System message
        *conversation_history[-(MAX_HISTORY * 2):]  # Last 10 Q&A pairs
    ]
```

---

## 🏆 **EXPECTED IMPROVEMENTS:**

### **Before (Current):**
```
Q1: "What are people discussing about feature engineering?"
A1: [MAGICAL synthesis] ✅

Q2: "Tell me more about consensus"
A2: "No relevant information found" ❌
```

### **After (With Context):**
```
Q1: "What are people discussing about feature engineering?"
A1: [MAGICAL synthesis including: "Consensus: FamilySize + IsAlone are must-have"] ✅

Q2: "Tell me more about consensus"
A2: [Expands on FamilySize + IsAlone from A1, with code examples] ✅
```

---

## 🚦 **STATUS:**

- ✅ **Issue documented**
- ⏳ **Frontend implementation pending**
- ⏳ **Backend implementation pending**
- ⏳ **Testing pending**

**Priority:** Medium (doesn't block single queries, but critical for V1 edge case goal)

---

## 📝 **NOTES:**

- This issue was discovered during DiscussionHelperAgent testing
- Agent architecture is sound - this is purely a context management issue
- Fixing this will address the V1 "followup failure" edge case
- Should work with all agents (NotebookExplainer, DiscussionHelper, etc.)

---

## 🎯 **NEXT SESSION TODO:**

1. [ ] Implement frontend conversation history management
2. [ ] Modify backend to accept and use conversation history
3. [ ] Test with followup queries (Test Cases above)
4. [ ] Update V2_AGENT_QUALITY_PLAYBOOK.md with context retention best practices

