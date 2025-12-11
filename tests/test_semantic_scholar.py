"""
Test script for Semantic Scholar API integration.
Verifies that the paper search functionality works correctly.
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.paper_search import PaperSearchTool, paper_search
import asyncio


def test_sync_search():
    """Test the synchronous paper search function"""
    print("="*80)
    print("TEST 1: Synchronous Paper Search")
    print("="*80)
    
    query = "human computer interaction"
    print(f"\nSearching for: '{query}'")
    print(f"Max results: 3")
    print(f"Year filter: 2020 onwards\n")
    
    result = paper_search(query, max_results=3, year_from=2020)
    print(result)
    
    return "PASSED" if result and "Found" in result else "FAILED"


async def test_async_search():
    """Test the async paper search"""
    print("\n" + "="*80)
    print("TEST 2: Async Paper Search with Filters")
    print("="*80)
    
    tool = PaperSearchTool(max_results=5)
    
    query = "accessibility user interfaces"
    print(f"\nSearching for: '{query}'")
    print("Filters:")
    print("  - Year: 2019-2023")
    print("  - Min citations: 10")
    print("  - Max results: 5\n")
    
    results = await tool.search(
        query=query,
        year_from=2019,
        year_to=2023,
        min_citations=10
    )
    
    if results:
        print(f"✓ Found {len(results)} papers\n")
        for i, paper in enumerate(results, 1):
            print(f"{i}. {paper['title']}")
            print(f"   Year: {paper['year']} | Citations: {paper['citation_count']}")
            print(f"   URL: {paper['url']}\n")
        return "PASSED"
    else:
        print("✗ No results found")
        return "FAILED"


async def test_paper_details():
    """Test getting paper details"""
    print("="*80)
    print("TEST 3: Get Paper Details")
    print("="*80)
    
    tool = PaperSearchTool()
    
    # First search for a paper
    results = await tool.search("Construction of the Literature Graph", max_results=1)
    
    if not results:
        print("✗ No papers found to test details")
        return "SKIPPED"
    
    paper_id = results[0]['paper_id']
    print(f"\nFetching details for paper ID: {paper_id}")
    
    details = await tool.get_paper_details(paper_id)
    
    if details and details.get('title'):
        print(f"\n✓ Successfully retrieved paper details")
        print(f"  Title: {details['title']}")
        print(f"  Authors: {len(details.get('authors', []))} authors")
        print(f"  Year: {details.get('year')}")
        print(f"  Citations: {details.get('citation_count')}")
        print(f"  Venue: {details.get('venue')}")
        if details.get('pdf_url'):
            print(f"  PDF: {details['pdf_url']}")
        return "PASSED"
    else:
        print("✗ Failed to retrieve details")
        return "FAILED"


async def test_citations():
    """Test getting paper citations"""
    print("\n" + "="*80)
    print("TEST 4: Get Paper Citations")
    print("="*80)
    
    tool = PaperSearchTool()
    
    # Search for a well-cited paper
    results = await tool.search("attention is all you need", max_results=1)
    
    if not results:
        print("✗ No papers found to test citations")
        return "SKIPPED"
    
    paper_id = results[0]['paper_id']
    print(f"\nFetching citations for: {results[0]['title']}")
    
    citations = await tool.get_citations(paper_id, limit=3)
    
    if citations:
        print(f"\n✓ Found {len(citations)} citing papers (showing first 3):")
        for i, cite in enumerate(citations, 1):
            print(f"  {i}. {cite['title']} ({cite.get('year', 'N/A')})")
        return "PASSED"
    else:
        print("✗ No citations found")
        return "FAILED"


def check_environment():
    """Check if environment is properly set up"""
    print("="*80)
    print("ENVIRONMENT CHECK")
    print("="*80)
    
    issues = []
    
    # Check Python version
    import sys
    print(f"\n✓ Python version: {sys.version.split()[0]}")
    
    # Check if semanticscholar is installed
    try:
        import semanticscholar
        print(f"✓ semanticscholarpackage installed")
    except ImportError:
        print("✗ semanticscholar package NOT installed")
        issues.append("Run: pip install semanticscholar")
    
    # Check for API key
    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        print(f"✓ API key found (length: {len(api_key)})")
    else:
        print("⚠ No API key found (using anonymous access - lower rate limits)")
        print("  To add key: edit .env and set SEMANTIC_SCHOLAR_API_KEY=your_key")
    
    # Check if .env exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✓ .env file exists")
    else:
        print("⚠ .env file not found")
        issues.append("Create .env file from .env.example")
    
    if issues:
        print("\n⚠ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✓ Environment setup looks good!")
        return True


async def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪 SEMANTIC SCHOLAR API TEST SUITE")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check environment first
    env_ok = check_environment()
    
    if not env_ok:
        print("\n⚠ Please fix environment issues before running tests")
        return
    
    print("\n" + "="*80)
    print("RUNNING TESTS")
    print("="*80)
    
    results = {}
    
    # Test 1: Sync search
    try:
        results['sync_search'] = test_sync_search()
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results['sync_search'] = "FAILED"
    
    # Test 2: Async searchtest_async_search
    try:
        results['async_search'] = await test_async_search()
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results['async_search'] = "FAILED"
    
    # Test 3: Paper details
    try:
        results['paper_details'] = await test_paper_details()
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results['paper_details'] = "FAILED"
    
    # Test 4: Citations
    try:
        results['citations'] = await test_citations()
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        results['citations'] = "FAILED"
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r == "PASSED")
    failed = sum(1 for r in results.values() if r == "FAILED")
    skipped = sum(1 for r in results.values() if r == "SKIPPED")
    
    print(f"\nTotal Tests: {total}")
    print(f"  ✓ Passed: {passed}")
    print(f"  ✗ Failed: {failed}")
    print(f"  ⊘ Skipped: {skipped}")
    
    print("\nDetailed Results:")
    for test_name, status in results.items():
        icon = "✓" if status == "PASSED" else "✗" if status == "FAILED" else "⊘"
        print(f"  {icon} {test_name}: {status}")
    
    # Save results
    report = {
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'python_version': sys.version.split()[0],
            'has_api_key': bool(os.getenv("SEMANTIC_SCHOLAR_API_KEY"))
        },
        'summary': {
            'total': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped
        },
        'results': results
    }
    
    os.makedirs('logs', exist_ok=True)
    report_file = 'logs/semantic_scholar_test_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Detailed report saved to: {report_file}")
    print("="*80)
    
    return passed == total


if __name__ == '__main__':
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
