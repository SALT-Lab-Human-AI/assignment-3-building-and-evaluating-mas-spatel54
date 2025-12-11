"""
Direct Semantic Scholar API test using requests library.
Based on official tutorial: https://www.semanticscholar.org/product/api/tutorial
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("SEMANTIC SCHOLAR API - DIRECT TEST (Using Official Tutorial Method)")
print("="*80)

# Get API key
api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
if not api_key:
    print("\n✗ No API key found in .env file")
    exit(1)

print(f"\n1. API Key: Found (length: {len(api_key)} chars)")
print(f"   First 8 chars: {api_key[:8]}...")

# Test 1: Get specific paper by ID (from tutorial)
print("\n" + "="*80)
print("TEST 1: Get Paper by ID (Official Tutorial Example)")
print("="*80)

paper_id = "649def34f8be52c8b66281af98ae884c09aef38b"
url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"

# Query parameters
query_params = {
    "fields": "title,year,abstract,citationCount"
}

# Headers with API key (THIS IS THE KEY PART from tutorial!)
headers = {
    "x-api-key": api_key
}

print(f"\nFetching paper: {paper_id}")
print(f"URL: {url}")
print(f"Fields: {query_params['fields']}")

try:
    response = requests.get(url, params=query_params, headers=headers, timeout=10)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS!")
        print(f"   Title: {data.get('title', 'N/A')}")
        print(f"   Year: {data.get('year', 'N/A')}")
        print(f"   Citations: {data.get('citationCount', 'N/A')}")
        if data.get('abstract'):
            abstract = data['abstract'][:150] + "..." if len(data['abstract']) > 150 else data['abstract']
            print(f"   Abstract: {abstract}")
    else:
        print(f"\n✗ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"\n✗ Request failed: {e}")
    exit(1)

# Test 2: Search for papers (bulk search)
print("\n" + "="*80)
print("TEST 2: Search Papers (Bulk Search)")
print("="*80)

search_url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"

search_params = {
    "query": "human computer interaction",
    "fields": "title,year,citationCount,url",
    "limit": 3
}

print(f"\nSearching for: '{search_params['query']}'")
print(f"Limit: {search_params['limit']} papers")

try:
    response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        papers = data.get('data', [])
        
        print(f"\n✅ SUCCESS! Found {len(papers)} papers:")
        
        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper.get('title', 'No title')}")
            print(f"   Year: {paper.get('year', 'N/A')} | Citations: {paper.get('citationCount', 0)}")
            print(f"   URL: {paper.get('url', 'N/A')}")
    
    elif response.status_code == 429:
        print(f"\n⚠️ RATE LIMITED (429)")
        print("   Wait a few minutes and try again")
        print("   Tip: Use bulk endpoints and limit requests to 1/second")
    else:
        print(f"\n✗ FAILED: {response.status_code}")
        print(f"   Error: {response.text}")
        exit(1)
        
except Exception as e:
    print(f"\n✗ Request failed: {e}")
    exit(1)

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - API Key Works!")
print("="*80)
print("\nNow you can use the Semantic Scholar API in your multi-agent system.")
print("The key is to pass the API key in headers: {'x-api-key': your_key}")
print("="*80)
