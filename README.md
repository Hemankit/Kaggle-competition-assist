# New Architecture - Scraper Router (Stage 1)

## 🎯 **What We Built**

A **two-stage architecture** that separates data collection from data processing:

```
Query → Scraper Router → Data Sources → Combined Data
```

## 📁 **File Structure**

```
improvements/
├── scraper_router/
│   ├── data_source_decider.py    # LLM-powered data source selection
│   └── scraper_router.py         # Main orchestrator for data collection
├── core_utils/
│   ├── simple_cache.py           # Simplified caching (no Redis dependency)
│   └── data_combiner.py          # Combines data from multiple sources
├── tests/
│   └── test_scraper_router.py    # Test suite for scraper router
├── main_orchestrator.py          # Main entry point
└── README.md                     # This file
```

## 🚀 **Key Components**

### **1. Data Source Decider**
- **Purpose**: LLM-powered decision making about what data sources to use
- **Input**: User query, context, cached data info
- **Output**: List of data sources (KAGGLE_API, SHALLOW_SCRAPING, PERPLEXITY_SEARCH, CACHED_DATA)
- **Intelligence**: Understands query urgency and data freshness requirements

### **2. Scraper Router**
- **Purpose**: Orchestrates data collection from chosen sources
- **Features**:
  - Integrates with existing scrapers (overview, notebook, model, discussion)
  - Uses Kaggle API for official data
  - Supports Perplexity API for real-time search
  - Implements intelligent caching

### **3. Data Combiner**
- **Purpose**: Combines and structures data from multiple sources
- **Features**:
  - Deduplicates content using hashing
  - Prioritizes items based on relevance
  - Generates metadata about data quality and freshness

### **4. Simple Cache**
- **Purpose**: Lightweight caching without Redis dependency
- **Features**:
  - In-memory storage with TTL
  - LRU eviction policy
  - Easy to replace with Redis later

## 🔧 **How It Works**

### **Step 1: Data Source Decision**
```python
# LLM analyzes query and decides data sources
decision = data_source_decider.decide_data_sources(
    query="What is the latest leaderboard?",
    context={"section": "leaderboard"},
    cached_data_info="No cached data",
    data_freshness="unknown"
)
# Returns: {"sources": ["KAGGLE_API", "PERPLEXITY_SEARCH"], "priority": "high"}
```

### **Step 2: Data Collection**
```python
# Router collects data from chosen sources
collected_data = scraper_router.route_and_collect_data(query, context)
# Returns: {"data": {...}, "sources_used": [...], "freshness": "fresh"}
```

### **Step 3: Data Combination**
```python
# Combiner structures and deduplicates data
combined_data = data_combiner.combine_data(collected_data, query)
# Returns: {"data": {...}, "metadata": {...}}
```

## ✅ **What's Working**

- ✅ **LLM-powered data source selection**
- ✅ **Intelligent caching with TTL**
- ✅ **Data combination and deduplication**
- ✅ **Integration points for existing scrapers**
- ✅ **Perplexity API integration ready**
- ✅ **Comprehensive test suite**

## ⚠️ **What Needs Integration**

- ⚠️ **Existing scrapers** (overview_scraper, notebook_scraper, etc.)
- ⚠️ **Kaggle API** (kaggle_fetcher)
- ⚠️ **Perplexity API** (needs API key)
- ⚠️ **Stage 2: Agent Router** (for data processing)

## 🧪 **Testing**

Run the test suite:
```bash
cd improvements
python tests/test_scraper_router.py
```

## 🎯 **Next Steps**

1. **Integrate with existing scrapers** - Connect to your current scraping infrastructure
2. **Add Perplexity API** - For real-time search capabilities
3. **Implement Stage 2** - Agent Router for data processing
4. **Replace with existing system** - Gradually migrate from old architecture

## 💡 **Key Benefits**

1. **Separation of Concerns** - Data collection vs processing
2. **LLM Intelligence** - Smart decisions about data sources
3. **No Deep Scraping Dependencies** - Eliminates ScrapeGraphAI complexity
4. **Easy to Test** - Modular components with clear interfaces
5. **Easy to Deploy** - No complex dependencies or Redis requirements

## 🔄 **Migration Path**

1. **Phase 1**: Use scraper router alongside existing system
2. **Phase 2**: Gradually replace old routing logic
3. **Phase 3**: Add Stage 2 (Agent Router) for complete architecture
4. **Phase 4**: Remove old hybrid scraping routing

This architecture directly addresses the issues identified by your Amazon friend:
- ✅ **No more strict keyword detection** - LLM-powered decisions
- ✅ **Better resource management** - Intelligent source selection
- ✅ **More natural flow** - Data-first approach
- ✅ **Easier to debug** - Clear separation of concerns