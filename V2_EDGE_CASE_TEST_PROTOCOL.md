# 🧪 V2.0 Edge-Case Testing Protocol

## 🎯 **GOAL**: Validate V2.0 solves V1's followup query failures

---

## 📋 **TEST SCENARIOS**

### **SCENARIO 1: Initial Notebook Query**

**Query:** "Show me top notebooks for Titanic"

**Expected Agent:** `notebook_explainer`

**Expected Response Format:**
- ✅ Categorized (Pinned vs Unpinned)
- ✅ Comparative analysis (scores, techniques)
- ✅ Actionable insights (START/BOOST/OPTIMIZE/AVOID)
- ✅ Meta-game trends
- ✅ KEY TAKEAWAY section

**Success Criteria:**
- [ ] Correct agent selected (notebook_explainer)
- [ ] Response is MAGICAL (not just factual listing)
- [ ] Contains competitive intelligence (deltas, comparisons)
- [ ] Provides actionable roadmap

---

### **SCENARIO 2: Followup - Specific Notebook Deep Dive**

**Previous Context:** User saw list of notebooks

**Query:** "Tell me more about the feature engineering in the second notebook"

**Expected Agent:** `notebook_explainer` (maintains context)

**Expected Response:**
- ✅ Identifies which notebook is "second" from previous context
- ✅ Deep dive into specific feature engineering techniques
- ✅ Compares to baseline/other notebooks
- ✅ Explains WHY the features work

**V1 Failure Mode:**
- ❌ Lost context, asked "which notebook?"
- ❌ Routed to wrong agent (data_section or competition_summary)
- ❌ Generic feature engineering advice instead of notebook-specific

**Success Criteria:**
- [ ] Maintains context from previous query
- [ ] Provides notebook-specific details
- [ ] No "which notebook?" confusion

---

### **SCENARIO 3: Followup - Comparative Analysis**

**Previous Context:** User saw list of notebooks

**Query:** "What's the difference between the pinned baseline and the top community notebook?"

**Expected Agent:** `notebook_explainer`

**Expected Response:**
- ✅ Side-by-side comparison
- ✅ Highlights key differences (techniques, features, scores)
- ✅ Shows deltas (+X% accuracy)
- ✅ Trade-offs (speed vs accuracy, complexity vs simplicity)

**V1 Failure Mode:**
- ❌ Re-listed notebooks instead of comparing
- ❌ Generic comparison without specifics

**Success Criteria:**
- [ ] Direct comparison with specific details
- [ ] Quantified differences (deltas)
- [ ] Actionable insights on which to use

---

### **SCENARIO 4: Followup - Filtered Search**

**Previous Context:** User knows notebooks exist

**Query:** "Show me notebooks that use XGBoost"

**Expected Agent:** `notebook_explainer`

**Expected Response:**
- ✅ Filtered list of XGBoost notebooks
- ✅ Compares different XGBoost implementations
- ✅ Highlights unique aspects (hyperparameters, custom objectives)

**V1 Failure Mode:**
- ❌ Showed all notebooks again
- ❌ No filtering capability

**Success Criteria:**
- [ ] Only XGBoost notebooks returned
- [ ] Comparative analysis of implementations
- [ ] Actionable insights on best XGBoost approach

---

### **SCENARIO 5: Followup - Learning from Failures**

**Previous Context:** User saw notebook list

**Query:** "What did the failed experiments teach us?"

**Expected Agent:** `notebook_explainer`

**Expected Response:**
- ✅ Highlights notebooks with lower scores
- ✅ Explains WHY they failed
- ✅ Extracts lessons (avoid X, watch out for Y)
- ✅ Turns failures into actionable "don'ts"

**V1 Failure Mode:**
- ❌ Only showed successful notebooks
- ❌ No failure analysis

**Success Criteria:**
- [ ] Identifies failed approaches
- [ ] Explains failure reasons
- [ ] Converts to actionable avoidance advice

---

### **SCENARIO 6: Cross-Agent Followup (CRITICAL)**

**Initial Query:** "Show me top notebooks for Titanic"
**Agent:** `notebook_explainer`

**Followup Query:** "Now compare that to what people are discussing about feature engineering"
**Expected Agent:** `discussion_helper` (intelligent switch!)

**Expected Response:**
- ✅ Synthesizes discussion posts about feature engineering
- ✅ Compares notebook techniques to discussion insights
- ✅ Identifies consensus vs. experimentation

**V1 Failure Mode:**
- ❌ Stuck on notebook agent
- ❌ Couldn't switch context
- ❌ Lost discussion context entirely

**Success Criteria:**
- [ ] Correctly switches to discussion_helper
- [ ] Maintains feature engineering context
- [ ] Synthesizes notebook + discussion insights

---

### **SCENARIO 7: Followup - Specific Notebook by Name**

**Previous Context:** User saw notebook titles

**Query:** "Tell me about the 'Titanic Data Science Solutions' notebook"

**Expected Agent:** `notebook_explainer`

**Expected Response:**
- ✅ Retrieves specific notebook by title
- ✅ Deep dive into that notebook's approach
- ✅ Compares to other notebooks

**V1 Failure Mode:**
- ❌ Couldn't find by name
- ❌ Re-listed all notebooks

**Success Criteria:**
- [ ] Finds notebook by exact title
- [ ] Provides detailed analysis
- [ ] Contextual comparison

---

## 📊 **TESTING CHECKLIST**

### **Phase 1: Basic Functionality**
- [ ] Backend starts without errors
- [ ] Frontend connects to backend
- [ ] Initial notebook query returns response
- [ ] Response format is MAGICAL (not V1 factual)

### **Phase 2: Edge-Case Followups**
- [ ] Scenario 2: Specific notebook followup
- [ ] Scenario 3: Comparative analysis
- [ ] Scenario 4: Filtered search
- [ ] Scenario 5: Learning from failures

### **Phase 3: Advanced Intelligence**
- [ ] Scenario 6: Cross-agent followup
- [ ] Scenario 7: Notebook by name

### **Phase 4: Hybrid Routing Validation**
- [ ] LLM tie-breaker logs show when invoked
- [ ] Agent selection is correct 95%+ of queries
- [ ] No "stuck agent" issues

---

## 🎯 **SUCCESS METRICS**

| Metric | V1 Performance | V2 Target | V2 Actual |
|--------|---------------|-----------|-----------|
| Initial Query Success | 90% | 95% | TBD |
| Followup Query Success | 30% | 85% | TBD |
| Cross-Agent Followup | 10% | 70% | TBD |
| Response Quality (MAGICAL) | 40% | 90% | TBD |
| Context Retention | 20% | 80% | TBD |

---

## 📝 **TEST LOG**

### **Test 1: Initial Notebook Query**
**Date:** 2025-11-03  
**Query:** "Show me top notebooks for Titanic"  
**Result:** [PENDING]  
**Agent Selected:** [TBD]  
**Response Quality:** [TBD]  
**Notes:** [TBD]

---

### **Test 2: Followup - Specific Notebook**
**Date:** 2025-11-03  
**Previous Query:** [Test 1]  
**Query:** "Tell me more about the second notebook's feature engineering"  
**Result:** [PENDING]  
**Agent Selected:** [TBD]  
**Context Retained:** [TBD]  
**Notes:** [TBD]

---

**Status:** Testing in Progress  
**Last Updated:** 2025-11-03  
**Tester:** V2.0 Validation Team

