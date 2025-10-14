# ChromaDB RAG Pipeline

This is an alternative implementation of the RAG pipeline using ChromaDB instead of Haystack to avoid version conflicts.

## 🎯 **Why This Exists**

- **Version Conflicts**: Haystack has complex dependency conflicts with pydantic/langchain
- **Same Architecture**: Maintains identical interface and functionality
- **Easy Migration**: Can switch back to Haystack when versions stabilize
- **Working System**: Get a functional RAG pipeline immediately

## 📁 **Structure**

```
RAG_pipeline_chromadb/
├── __init__.py              # Module exports
├── rag_pipeline.py          # Main orchestrator (ChromaDBRAGPipeline)
├── chunking.py              # Document chunking (ChromaDBChunker)
├── indexing.py              # Document indexing (ChromaDBIndexer)
├── retrieval.py             # Document retrieval (ChromaDBRetriever)
├── test_chromadb_pipeline.py # Test script
└── README.md                # This file
```

## 🔄 **Component Mapping**

| Haystack Component | ChromaDB Equivalent | Functionality |
|-------------------|-------------------|---------------|
| `FAISSDocumentStore` | `ChromaDB Collection` | Vector storage |
| `EmbeddingRetriever` | `SentenceTransformer + ChromaDB.query()` | Embedding retrieval |
| `SentenceTransformersRanker` | `CrossEncoder` | Document reranking |
| `PreProcessor` | `ChromaDBChunker` | Document chunking |
| `Document` | `Dict[str, Any]` | Document representation |

## 🚀 **Usage**

```python
from RAG_pipeline_chromadb import ChromaDBRAGPipeline

# Initialize (same interface as Haystack version)
pipeline = ChromaDBRAGPipeline()

# Index documents (same interface)
pipeline.index_scraped_data(pydantic_results, structured_results)

# Retrieve and rerank (same interface)
results = pipeline.rerank_document_store(query, top_k_retrieval=20, top_k_final=5)

# Run pipeline (same interface)
results = pipeline.run({"query": "machine learning", "documents": docs})
```

## 📦 **Dependencies**

```bash
pip install chromadb sentence-transformers
```

**No Haystack dependencies required!**

## ✅ **Benefits**

1. **No Version Conflicts**: ChromaDB has minimal dependencies
2. **Same Interface**: Drop-in replacement for Haystack version
3. **Better Performance**: ChromaDB is optimized for vector operations
4. **Easy Maintenance**: Simpler codebase, fewer dependencies
5. **Future-Proof**: Easy to migrate back to Haystack when ready

## 🔧 **Migration Path**

When Haystack version conflicts are resolved:

1. **Keep both implementations** during transition
2. **Run A/B tests** to compare performance
3. **Gradually migrate** components one by one
4. **Remove ChromaDB version** when fully migrated

## 🧪 **Testing**

```bash
cd RAG_pipeline_chromadb
python test_chromadb_pipeline.py
```

## 📊 **Performance Comparison**

| Metric | Haystack | ChromaDB |
|--------|----------|----------|
| **Setup Time** | Slow (dependencies) | Fast (minimal deps) |
| **Memory Usage** | High | Moderate |
| **Query Speed** | Good | Excellent |
| **Indexing Speed** | Good | Excellent |
| **Maintenance** | Complex | Simple |

## 🔮 **Future Enhancements**

- [ ] Add persistence options (ChromaDB supports multiple backends)
- [ ] Implement advanced filtering
- [ ] Add batch processing optimizations
- [ ] Integrate with existing logging system
- [ ] Add performance monitoring
