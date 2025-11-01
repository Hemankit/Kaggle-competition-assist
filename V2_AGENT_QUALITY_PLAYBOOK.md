# V2.0 Agent Quality Playbook 🎯

## Why This Matters
**V2.0 architecture is NOT plug-and-play with V1 agents!** Simply copying agents from V1 will result in poor responses. This playbook documents the issues we encountered and how to fix them for **ALL** agents.

---

## 🔥 The CompetitionSummaryAgent Journey: Lessons Learned

### ❌ What Went Wrong Initially

1. **Response Repetition (4x "Hello there!")**
   - **Problem**: Agent was calling `explain_sections()` which generates separate response per chunk
   - **Fix**: Changed to `summarize_sections()` to combine chunks FIRST, then generate ONE response
   - **File**: `agents/base_rag_retrieval_agent.py` line 90

2. **Mixed Competition Data (Titanic + ARC-AGI)**
   - **Problem**: ChromaDB was returning documents from ALL competitions
   - **V1 Had This**: `minimal_backend.py` line 397: `where_filter = {"competition_slug": competition_slug}`
   - **V2 Missed It**: DynamicOrchestrator wasn't passing `competition_slug` to retrieval
   - **Fix**: 
     - Updated `rag_pipeline.py` to accept `competition_slug` parameter
     - Updated `base_rag_retrieval_agent.py` to extract and pass `competition_slug` from metadata

3. **Wrong Slug in Session ("tita" vs "titanic")**
   - **Problem**: Frontend autocomplete set correct slug, but was overwritten by user input
   - **File**: `streamlit_frontend/app.py` line 469
   - **Fix**: `competition_slug = session_state.get('competition_slug', competition_input)`

4. **Generic Overview Instead of Evaluation Breakdown**
   - **Problem**: Agent always used `overview_prompt`, never `evaluation_prompt`
   - **Fix**: Dynamic detection of evaluation keywords in query
   - **File**: `agents/competition_summary_agent.py` line 176

5. **Missing Metric Name ("Metric Name" and "Details" are blank)**
   - **Problem**: Evaluation prompt expected `{metric}` and `{details}` in metadata, but they were empty
   - **Fix**: Extract metric name from retrieved content using keyword matching
   - **File**: `agents/competition_summary_agent.py` line 211 (`_extract_metric_name()`)

---

## ✅ The Fix Checklist for ANY V2.0 Agent

### 1. **Response Consolidation**
```python
# ❌ BAD (V1 way):
final_response = self.explain_sections(relevant_chunks, metadata)

# ✅ GOOD (V2 way):
final_response = self.summarize_sections(chunks, metadata)
```
**Why**: `explain_sections()` generates separate LLM calls per chunk → repetitive responses. `summarize_sections()` combines chunks → ONE clean response.

### 2. **Competition Filtering**
```python
# In your agent's fetch_sections or run method:
metadata = structured_query.get("metadata", {})
competition_slug = metadata.get("competition_slug") or metadata.get("competition")

# Pass to retriever:
docs = self.retriever.rerank_document_store(
    query=cleaned_query,
    competition_slug=competition_slug  # CRITICAL!
)
```
**Why**: ChromaDB has data from multiple competitions. Without filtering, you get mixed results.

### 3. **Dynamic Prompt Selection**
```python
# Detect query intent (e.g., evaluation vs overview)
query_lower = query.get("cleaned_query", "").lower()
is_specific_intent = any(keyword in query_lower for keyword in intent_keywords)

if is_specific_intent:
    # Use specialized prompt
    self.chain = LLMChain(llm=self.llm, prompt=specialized_prompt)
else:
    # Use general prompt
    self.chain = LLMChain(llm=self.llm, prompt=general_prompt)
```
**Why**: Different query types need different prompt templates for high-quality responses.

### 4. **Metadata Extraction from Content**
```python
# Don't assume metadata is provided - extract from content!
combined_content = "\n".join([chunk.get("content", "") for chunk in chunks])

# Extract key information
key_info = self._extract_key_info(combined_content)

# Pass to prompt
metadata["extracted_info"] = key_info
```
**Why**: V2 orchestrator may not pass all metadata. Agents must be self-sufficient.

### 5. **Frontend/Backend Contract**
```python
# Backend must return:
{
    "response": final_response,
    "final_response": final_response,  # Frontend expects this!
    "metadata": {...}
}
```
**Why**: Frontend looks for `final_response` key. Missing this = "No response received".

---

## 🎯 Agent-Specific Considerations

### **CompetitionSummaryAgent** ✅ (DONE)
- ✅ Dynamic prompt switching (overview vs evaluation)
- ✅ Metric extraction from content
- ✅ Competition filtering
- ✅ Response consolidation

### **NotebookExplainerAgent** (TODO)
- **Likely Issues**:
  - Multiple notebook chunks → repetitive explanations
  - Need to extract: notebook name, key techniques, performance metrics
- **Prompt Needs**: Code explanation + technique breakdown
- **Metadata to Extract**: 
  - Notebook title
  - Libraries used (pandas, sklearn, xgboost, etc.)
  - Model types mentioned

### **DiscussionHelperAgent** (TODO)
- **Likely Issues**:
  - Multiple discussion posts → repetitive summaries
  - Need to identify: main topics, best answers, community consensus
- **Prompt Needs**: Discussion synthesis + actionable insights
- **Metadata to Extract**:
  - Discussion topic
  - Top-voted answers
  - Recurring themes

### **DataSectionAgent** (TODO)
- **Likely Issues**:
  - Data dictionary entries → need structured presentation
  - Feature descriptions need to be organized
- **Prompt Needs**: Feature explanation + usage recommendations
- **Metadata to Extract**:
  - Feature names
  - Data types
  - Missing value patterns

### **ErrorDiagnosisAgent** (Non-RAG, TODO)
- **Likely Issues**:
  - May not need ChromaDB filtering (focuses on code)
  - Needs error context from user query
- **Prompt Needs**: Error interpretation + fix suggestions

### **CodeFeedbackAgent** (Non-RAG, TODO)
- **Likely Issues**:
  - Code snippets need syntax highlighting in response
  - Multiple improvement suggestions → prioritize by impact
- **Prompt Needs**: Code review + improvement recommendations

---

## 🚨 Common Failure Patterns to Watch For

### Pattern 1: "No response received"
**Symptoms**: Frontend shows error, backend logs show successful execution
**Root Cause**: Frontend expects `final_response` key, backend returns `response` key
**Fix**: Return BOTH keys in backend response

### Pattern 2: Repetitive responses
**Symptoms**: "Hello there!..." repeated 3-4 times
**Root Cause**: Using `explain_sections()` instead of `summarize_sections()`
**Fix**: Change to `summarize_sections()` in agent's `run()` method

### Pattern 3: Mixed competition data
**Symptoms**: Response contains info from wrong competition (e.g., ARC-AGI in Titanic query)
**Root Cause**: ChromaDB retrieval not filtered by `competition_slug`
**Fix**: Pass `competition_slug` to `retriever.rerank_document_store()`

### Pattern 4: Generic responses
**Symptoms**: Agent gives overview when user asks for specific info (e.g., evaluation metric)
**Root Cause**: Agent using wrong prompt template (not detecting query intent)
**Fix**: Implement dynamic prompt selection based on query keywords

### Pattern 5: Asking user for info we should know
**Symptoms**: "Please tell me the metric name..."
**Root Cause**: Prompt expects metadata that's not provided
**Fix**: Extract information from retrieved content, don't rely on metadata

---

## 📊 Quality Comparison: V1 vs V2

### V1 Architecture
- ✅ **Simple**: Direct endpoint calls, no orchestration overhead
- ✅ **Explicit filtering**: Backend directly passed `competition_slug` to every retrieval
- ❌ **Limited**: Keyword routing only, no intelligent agent selection
- ❌ **Brittle**: Hard to add new agents or orchestration modes

### V2 Architecture
- ✅ **Intelligent**: Dynamic agent selection, cross-framework orchestration
- ✅ **Scalable**: Easy to add new agents and modes
- ✅ **Flexible**: Category-based routing (RAG, CODE, STRATEGY)
- ⚠️ **Complex**: Requires careful metadata passing through orchestration layers
- ⚠️ **Debugging**: More layers = more potential failure points

---

## 🎯 V2 Quality = V1 Quality + V2 Intelligence

**The Goal**: 
- Responses should be **AS GOOD OR BETTER** than V1
- With the **ADDED BENEFIT** of intelligent routing and multi-agent orchestration

**The Reality**:
- V1 agents won't "just work" in V2
- Each agent needs V2-specific adaptations (this playbook!)
- But once adapted, V2 responses are **significantly better**

---

## 🔧 Step-by-Step Agent Migration

### Phase 1: Base Integration
1. ✅ Copy agent from V1
2. ✅ Test in V2 environment
3. ✅ Document issues (use this playbook!)

### Phase 2: Fix Response Quality
1. ✅ Change to `summarize_sections()`
2. ✅ Add competition filtering
3. ✅ Extract metadata from content
4. ✅ Test: Compare response to V1 quality

### Phase 3: Add V2 Intelligence
1. ✅ Implement dynamic prompt selection
2. ✅ Add query intent detection
3. ✅ Optimize for category-based routing
4. ✅ Test: Verify responses are BETTER than V1

### Phase 4: Edge Cases & Robustness
1. ⏳ Test with empty ChromaDB
2. ⏳ Test with wrong competition slug
3. ⏳ Test with multi-part queries
4. ⏳ Test follow-up questions (context retention)

---

## 📝 Testing Protocol

### Baseline Query (V1 Comparison)
```
Query: "What is the evaluation metric for this competition?"
Expected: Detailed 3-section breakdown (GOAL, OPTIMIZATION, PREPROCESSING)
V1 Result: [Paste V1 response for comparison]
V2 Result: [Should match or exceed V1 quality]
```

### Edge Case Queries
```
Query: "Can you explain me the evaluation metric?"  # Missing "for this competition"
Expected: Should still work with context from session

Query: "metric"  # Single word
Expected: Should detect intent and provide evaluation breakdown

Query: "How is performance measured?"  # Indirect phrasing
Expected: Should detect this is about evaluation metric
```

---

## 🚀 Success Criteria

An agent is **V2-ready** when:
1. ✅ No repetitive responses
2. ✅ Competition-specific data only
3. ✅ Correct prompt for query intent
4. ✅ Self-sufficient (extracts needed info from content)
5. ✅ Response quality ≥ V1
6. ✅ Handles edge cases gracefully

---

## 💡 Key Takeaways

1. **V2 ≠ V1 with fancier routing**
   - V2 requires structural changes to agents
   - Metadata flow is different
   - Response consolidation is critical

2. **Competition filtering is MANDATORY**
   - Every RAG agent MUST filter by `competition_slug`
   - V1 had this, V2 must too

3. **Don't trust metadata - extract from content**
   - Orchestrator may not pass everything
   - Agents should be self-sufficient

4. **Dynamic prompts = Better responses**
   - One-size-fits-all prompts don't work
   - Detect intent, switch prompts accordingly

5. **Frontend/Backend contract matters**
   - Response key names must match
   - Test end-to-end, not just backend

---

## 📚 Reference Files

### Critical Files for Agent Quality
1. `agents/base_rag_retrieval_agent.py` - Base class, response consolidation
2. `agents/competition_summary_agent.py` - Reference implementation ✅
3. `RAG_pipeline_chromadb/rag_pipeline.py` - Competition filtering
4. `routing/dynamic_orchestrator.py` - Agent execution, metadata passing
5. `backend_v2.py` - Response format, frontend contract

### V1 Reference (for comparison)
1. `minimal_backend.py` - V1 competition filtering (line 397)
2. Agent implementations in V1 (if available)

---

**Last Updated**: 2025-11-01  
**Status**: CompetitionSummaryAgent ✅ COMPLETE | Others ⏳ PENDING

