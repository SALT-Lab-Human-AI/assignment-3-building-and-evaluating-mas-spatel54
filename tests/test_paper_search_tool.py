"""
Quick test of the updated paper_search.py
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from tools.paper_search import PaperSearchTool

load_dotenv()

async def test_search():
    print("="*80)
    print("Testing Updated PaperSearchTool")
    print("="*80)
    
    tool = PaperSearchTool(max_results=5)
    
    print("\nSearching for: 'accessibility user interfaces'")
    print("Max results: 5")
    print("Min citations: 10")
    print("Year: 2020 onwards\n")
    
    results = await tool.search(
        query="accessibility user interfaces",
        year_from=2020,
        min_citations=10
    )
    
    if results:
        print(f"✅ SUCCESS! Found {len(results)} papers:\n")
        for i, paper in enumerate(results, 1):
            print(f"{i}. {paper['title']}")
            print(f"   Year: {paper['year']} | Citations: {paper['citation_count']}")
            authors = ", ".join([a['name'] for a in paper['authors'][:3]])
            if len(paper['authors']) > 3:
                authors += " et al."
            print(f"   Authors: {authors}")
            print(f"   URL: {paper['url']}")
            if paper.get('pdf_url'):
                print(f"   PDF: {paper['pdf_url']}")
            print()
    else:
        print("✗ No results found (check logs for errors)")
        return False
   
    print("="*80)
    print("✅ Paper search tool working correctly!")
    print("="*80)
    return True

if __name__ == "__main__":
    success = asyncio.run(test_search())
    sys.exit(0 if success else 1)
