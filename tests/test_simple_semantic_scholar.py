"""
Simple Semantic Scholar API test - verifies connection works with anonymous access.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*80)
print("SEMANTIC SCHOLAR API - SIMPLE CONNECTION TEST")
print("="*80)

# Load environment
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
print(f"\n1. API Key Status: {'Found' if api_key else 'Not found (using anonymous access)'}")

# Test library import
try:
    from semanticscholar import SemanticScholar
    print("2. ✓ semanticscholar library imported successfully")
except ImportError as e:
    print(f"2. ✗ Failed to import: {e}")
    sys.exit(1)

# Initialize client
try:
    sch = SemanticScholar(api_key=api_key, timeout=10)
    print("3. ✓ Semantic Scholar client initialized")
except Exception as e:
    print(f"3. ✗ Failed to initialize client: {e}")
    sys.exit(1)

# Try a simple search
print("\n4. Testing paper search...")
print("   Query: 'human computer interaction'")
print("   Limit: 2 papers")
print("   Timeout: 10 seconds")

try:
    results = sch.search_paper(
        "human computer interaction", 
        limit=2,
        fields=["paperId", "title", "year", "citationCount"]
    )
    
    papers = list(results)
    
    if papers:
        print(f"\n   ✓ SUCCESS! Found {len(papers)} papers:")
        for i, paper in enumerate(papers, 1):
            print(f"\n   Paper {i}:")
            print(f"     Title: {paper.title}")
            print(f"     Year: {paper.year}")
            print(f"     Citations: {paper.citationCount}")
            print(f"     ID: {paper.paperId}")
    else:
        print("   ⚠ Search returned no results")
        
except Exception as e:
    print(f"\n   ✗ Search failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - Semantic Scholar API is working!")
print("="*80)
print("\nYou can now use the paper_search tool in your multi-agent system.")
print("Note: Anonymous access has rate limits (1 req/sec).")
print("For higher limits, add a real API key to your .env file.")
print("="*80)
