# Semantic Scholar API - Quick Start Guide

## ⚠️ Important: API Key Issue Detected

Your tests show a **403 Forbidden** error, which means:
1. The API key in `.env` might be a placeholder (not a real key)
2. OR the API key has expired/been revoked
3. OR you might need to use anonymous access

## 🔧 Two Options to Fix

### Option 1: Get a Real API Key (Recommended)

1. **Visit**: https://www.semanticscholar.org/product/api  
2. Click **"Sign in"** (top right)
3. After signing in, go to your **API dashboard**
4. Copy your **personal API key**
5. Edit `.env` and replace the placeholder with your real key:
   ```bash
   SEMANTIC_SCHOLAR_API_KEY=your_real_key_here
   ```

### Option 2: Use Anonymous Access (No Key Needed)

Edit `.env` and comment out or remove the Semantic Scholar line:
```bash
# SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key_here
```

**Note:** Anonymous access has lower rate limits (1 request/second instead of 100/second).

---

## 📍 Test Log Locations

### Guardrails Test Logs
```
/Users/shivpat/assignment-3-building-and-evaluating-mas-spatel54/logs/
├── guardrails_test_report.json    (4.3 KB) - ✅ Complete test results
└── semantic_scholar_test_report.json - Will be created after successful test
```

### To View Logs:
```bash
# Guardrails test results
cat logs/guardrails_test_report.json | python3 -m json.tool

# Semantic Scholar test results (after running tests)
cat logs/semantic_scholar_test_report.json | python3 -m json.tool
```

---

## 🧪 Run Tests After Fixing API Key

```bash
# Activate virtual environment
source venv/bin/activate

# Run Semantic Scholar tests
python3 test_semantic_scholar.py
```

---

## 📚 What's Already Set Up

✅ **`semanticscholar` library** (v0.11.0) - Installed in venv  
✅ **Implementation** - `src/tools/paper_search.py` is complete  
✅ **API Spec** - `swagger.json` has full API documentation  
✅ **Test Suite** - `test_semantic_scholar.py` ready to run  

---

## 🔍 Available Features

Your `PaperSearchTool` supports:

### Search Papers
```python
from src.tools.paper_search import paper_search

# Simple search
result = paper_search("accessibility user interfaces", max_results=5)
print(result)
```

### Advanced Search with Filters
```python
from src.tools.paper_search import PaperSearchTool
import asyncio

async def search():
    tool = PaperSearchTool(max_results=10)
    results = await tool.search(
        query="human computer interaction",
        year_from=2020,
        year_to=2023,
        min_citations=50
    )
    return results

results = asyncio.run(search())
```

### Get Paper Details
```python
tool = PaperSearchTool()
details = await tool.get_paper_details("paper_id_here")
```

### Get Citations & References
```python
citations = await tool.get_citations("paper_id_here", limit=10)
references = await tool.get_references("paper_id_here", limit=10)
```

---

## 🚀 Quick Fix & Test

1. **Edit `.env`** - Add real API key OR comment out the line
2. **Run tests**:
   ```bash
   source venv/bin/activate
   python3 test_semantic_scholar.py
   ```
3. **Check results** in `logs/semantic_scholar_test_report.json`

---

## 📖 Full Documentation

See **`SEMANTIC_SCHOLAR_SETUP.md`** for complete setup guide including:
- All available API endpoints from swagger.json
- Detailed filter options
- Field customization
- Troubleshooting guide
- Integration examples
