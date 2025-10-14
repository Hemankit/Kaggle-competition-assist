# Component Testing Suite

This directory contains comprehensive test scripts for all major components of the Kaggle Competition Assist system.

## Test Files

### Individual Component Tests
- **`test_kaggle_fetcher.py`** - Tests Kaggle API client and fetcher components
- **`test_scrapers.py`** - Tests all scraper components (overview, notebook, model, discussion)
- **`test_hybrid_scraping_routing.py`** - Tests routing and decision-making components
- **`test_query_processing.py`** - Tests query preprocessing and classification
- **`test_rag_pipeline.py`** - Tests RAG pipeline components (chunking, indexing, retrieval)
- **`test_orchestrators.py`** - Tests orchestration components
- **`test_agents.py`** - Tests all agent components (excluded from master test for now)

### Master Test
- **`test_all_components.py`** - Runs all component tests in sequence

## Usage

### Run Individual Component Tests
```bash
# Test specific component
python component_tests/test_kaggle_fetcher.py
python component_tests/test_scrapers.py
python component_tests/test_hybrid_scraping_routing.py
python component_tests/test_query_processing.py
python component_tests/test_rag_pipeline.py
python component_tests/test_orchestrators.py
python component_tests/test_agents.py  # (excluded from master test for now)
```

### Run All Tests
```bash
# Run comprehensive test suite
python component_tests/test_all_components.py
```

## What Each Test Checks

### Import Tests
- ✅ Successful import of all modules
- ✅ No import errors or missing dependencies

### Initialization Tests  
- ✅ Components can be instantiated with default parameters
- ✅ Components can be instantiated with custom parameters
- ✅ No constructor errors

### Method Existence Tests
- ✅ Required methods are present on classes
- ✅ Methods are callable

### Basic Functionality Tests
- ✅ Components respond to basic method calls
- ✅ No immediate runtime errors

## Expected Results

### ✅ Success Indicators
- All imports successful
- All initializations successful  
- All required methods present
- No runtime errors during basic operations

### ❌ Failure Indicators
- Import errors (missing dependencies)
- Constructor errors (parameter mismatches)
- Missing methods
- Runtime errors during initialization

## Next Steps

After running these tests:

1. **If all tests pass**: Proceed to integration testing
2. **If some tests fail**: Fix the identified issues before integration testing
3. **If many tests fail**: Check environment setup and dependencies

## Dependencies

Make sure you have:
- All required Python packages installed (`pip install -r requirements.txt`)
- Environment variables set up (`.env` file)
- Required API keys configured
- Redis server running (if using Redis caching)

## Notes

- These tests focus on **initialization and basic functionality**
- They do **not** test actual API calls or external service connections
- They do **not** test complex business logic
- They are designed to catch **structural and import issues** early

This testing approach helps identify issues before attempting to run the full application, making debugging much more efficient.
