# Phase 2: Multi-Mode Orchestration Testing

## 🎯 Goal
Verify all 3 orchestration modes work without 500 errors

---

## 🧪 Test Queries

### Test 1: LangGraph Mode (RAG/Retrieval)
**Query:** "What is the evaluation metric for this competition?"

**Expected:**
- Category: `RAG` or `GENERAL`
- Mode: `LANGGRAPH`
- Agents: 1-2 (CompetitionSummaryAgent, DiscussionHelperAgent)
- Result: ✅ No 500 error (empty response OK for now)

---

### Test 2: CrewAI Mode (Reasoning)
**Query:** "Give me ideas to improve my model performance"

**Expected:**
- Category: `REASONING`
- Mode: `CREWAI`
- Agents: 1-2 (IdeaInitiatorAgent, MultiHopReasoningAgent)
- Result: ✅ No 500 error (empty response OK for now)

---

### Test 3: AutoGen Mode (Multi-Agent/Hybrid)
**Query:** "How can I combine feature engineering, ensemble methods, and hyperparameter tuning to optimize my submission?"

**Expected:**
- Category: `HYBRID`
- Mode: `AUTOGEN`
- Agents: 3+ (IdeaInitiatorAgent, MultiHopReasoningAgent, CodeFeedbackAgent)
- Result: ✅ No 500 error (empty response OK for now)

---

## ✅ Success Criteria
- [ ] No 500 errors for all 3 queries
- [ ] Correct mode selection (LangGraph, CrewAI, AutoGen)
- [ ] Backend logs show proper routing
- [ ] Frontend receives response (even if empty)

---

## 🐛 If Errors Occur
1. Check backend terminal for stack traces
2. Identify which orchestrator is failing
3. Fix compatibility issues (like the CrewAI Task context error we fixed earlier)
4. Retest

---

## 📝 Notes
- Empty responses are OK at this stage (ChromaDB is empty)
- We're testing **orchestration**, not **content quality**
- Phase 3 will test retrieval with real data
- Phase 4 will test complex reasoning

