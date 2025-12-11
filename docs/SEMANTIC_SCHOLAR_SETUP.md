# Semantic Scholar API Setup Guide

## 📍 Test Logs Location

Your guardra ils test logs are located in:
```
/Users/shivpat/assignment-3-building-and-evaluating-mas-spatel54/logs/
```

Files:
- **`guardrails_test_report.json`** (4.3 KB) - Complete test results in JSON format
- **`safety_events.log`** - Can be generated on-demand when safety violations occur

---

## 🔧 Semantic Scholar Setup

### Overview
Semantic Scholar is already integrated in your project! The implementation is in:
- **File**: `src/tools/paper_search.py`
- **API Spec**: `swagger.json` (Semantic Scholar Academic Graph API v1)

### Current Implementation Status: ✅ COMPLETE

Your `paper_search.py` uses the `semanticscholar` Python library which is already listed in your `requirements.txt`.

### Configuration Steps

#### 1. Check if Library is Installed
```bash
source venv/bin/activate
pip show semanticscholar
```

#### 2. Get Your API Key (Optional but Recommended)

The API works without a key, but having one gives you:
- **Higher rate limits**: 100 requests/second (vs 1 req/sec anonymous)
- **Better reliability**

**To get your API key:**
1. Visit: https://www.semanticscholar.org/product/api
2. Click "Get API Key" or sign in
3. Navigate to your API dashboard
4. Copy your API key

#### 3. Add API Key to .env File

Edit your `.env` file and add:
```bash
# Semantic Scholar API (optional, has free tier)
SEMANTIC_SCHOLAR_API_KEY=your_actual_api_key_here
```

If you already have it set, verify the key is correct.

#### 4. Test the Integration

Run the test script (see below) to verify everything works.

---

## 🔍 API Capabilities (from swagger.json)

### Available Endpoints

Based on your `swagger.json`, the Semantic Scholar API supports:

### **Paper Search**
- `/paper/search` - Search papers by query
- `/paper/search/match` - Find exact title matches
- `/paper/search/bulk` - Bulk paper retrieval
- `/paper/{paper_id}` - Paper details
- `/paper/batch` - Multiple papers at once

### **Citations & References**
- `/paper/{paper_id}/citations` - Get citing papers
- `/paper/{paper_id}/references` - Get referenced papers

### **Author Search**
- `/author/search` - Search for authors
- `/author/{author_id}` - Author details
- `/author/{author_id}/papers` - Author's papers

### **Filters Available**
- Publication year range
-Minimum citation count
- Open access PDF only
- Venue (conference/journal)
- Fields of study
- Publication types

### **Fields You Can Request**
- `title`, `abstract`, `authors`, `year`
- `citationCount`, `referenceCount`
- `url`, `venue`, `openAccessPdf`
- `fieldsOfStudy`, `publicationTypes`
- `embedding` (Specter v1 or v2)
- `tldr` (AI-generated summary)

---

## 🧪 Testing

### Quick Test

Run this Python code to test:

```python
from src.tools.paper_search import paper_search

# Test search
result = paper_search("human computer interaction", max_results=3, year_from=2020)
print(result)
```

Or use the comprehensive test script provided below.

---

## 📊 Your Current Implementation

### Methods Available in `PaperSearchTool`:

1. **`search(query, year_from, year_to, min_citations)`**
   - Search for papers with filters
   - Returns list of paper dictionaries

2. **`get_paper_details(paper_id)`**
   - Get full details of a specific paper
   - Includes authors, abstract, citations, etc.

3. **`get_citations(paper_id, limit)`**
   - Get papers that cite this paper

4. **`get_references(paper_id, limit)`**
   - Get papers referenced by this paper

5. **`paper_search(query, max_results, year_from)`** *(synchronous wrapper)*
   - For use with AutoGen tools
   - Returns formatted string output

---

## 🚨 Troubleshooting

### Issue: Library not installed
```bash
source venv/bin/activate
pip install semanticscholar
```

### Issue: API rate limiting
- Add your API key to `.env`
- Reduce request frequency
- Add delays between requests

### Issue: Import errors
```python
# Test if library is importable
python3 -c "from semanticscholar import SemanticScholar; print('OK')"
```

### Issue: Connection errors
- Check internet connection
- Verify API key is valid
- Check Semantic Scholar API status

---

## 📚 Useful Resources

- **API Documentation**: https://api.semanticscholar.org/api-docs/
- **Python Library**: https://github.com/danielnsilva/semanticscholar
- **API Product Page**: https://www.semanticscholar.org/product/api
- **Your swagger.json**: Complete API specification in your project root

---

## ✅ Next Steps

1. ✅ Verify `semanticscholar` is installed in venv
2. ✅ Add your API key to `.env` (or use anonymous access)
3. ✅ Run the test script below
4. ✅ Integrate with your multi-agent system
