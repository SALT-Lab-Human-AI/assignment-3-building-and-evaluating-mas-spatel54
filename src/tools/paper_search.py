"""
Paper Search Tool
Integrates with Semantic Scholar API for academic paper search.

This tool provides academic paper search functionality using the
Semantic Scholar API, which offers free access to a large corpus
of academic papers.
"""

from typing import List, Dict, Any, Optional
import os
import logging
import asyncio


class PaperSearchTool:
    """
    Tool for searching academic papers via Semantic Scholar API.
    
    Semantic Scholar provides free access to academic papers with
    rich metadata including citations, abstracts, and author information.
    API key is optional but recommended for higher rate limits.
    """

    def __init__(self, max_results: int = 10):
        """
        Initialize paper search tool.

        Args:
            max_results: Maximum number of papers to return
        """
        self.max_results = max_results
        self.logger = logging.getLogger("tools.paper_search")

        # API key is optional for Semantic Scholar
        self.api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        
        if not self.api_key:
            self.logger.info("No Semantic Scholar API key found. Using anonymous access (lower rate limits)")

    async def search(
        self,
        query: str,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        min_citations: int = 0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search for academic papers using Semantic Scholar API.
        
        Uses the official API with proper authentication headers.
        Based on: https://www.semanticscholar.org/product/api/tutorial

        Args:
            query: Search query
            year_from: Filter papers from this year onwards
            year_to: Filter papers up to this year
            min_citations: Minimum citation count
            **kwargs: Additional search parameters
                - fields: List of fields to retrieve

        Returns:
            List of papers with metadata format:
            {
                "paper_id": str,
                "title": str,
                "authors": List[{"name": str}],
                "year": int,
                "abstract": str,
                "citation_count": int,
                "url": str,
                "venue": str,
                "pdf_url": Optional[str],
            }
        """
        self.logger.info(f"Searching papers: {query}")

        try:
            import requests
            
            # Use bulk search endpoint (recommended in tutorial)
            url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
            
            # Build year filter if provided
            year_filter = None
            if year_from and year_to:
                year_filter = f"{year_from}-{year_to}"
            elif year_from:
                year_filter = f"{year_from}-"
            elif year_to:
                year_filter = f"-{year_to}"
            
            # Query parameters
            params = {
                "query": query,
                "fields": "paperId,title,authors,year,abstract,citationCount,url,venue,openAccessPdf",
                "limit": min(self.max_results, 100)  # API max is 100 per request
            }
            
            if year_filter:
                params["year"] = year_filter
            
            # Headers with API key (CRITICAL: must use x-api-key header!)
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            
            # Make request
            self.logger.debug(f"Requesting: {url} with params: {params}")
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                papers_data = data.get('data', [])
                
                # Parse results
                papers = []
                for paper in papers_data:
                    # Apply citation filter
                    citation_count = paper.get('citationCount', 0) or 0
                    if citation_count < min_citations:
                        continue
                    
                    # Parse authors
                    authors = []
                    for author in paper.get('authors', []):
                        authors.append({"name": author.get('name', 'Unknown')})
                    
                    # Parse PDF URL
                    pdf_url = None
                    if paper.get('openAccessPdf'):
                        pdf_url = paper['openAccessPdf'].get('url')
                    
                    papers.append({
                        "paper_id": paper.get('paperId'),
                        "title": paper.get('title', 'Unknown'),
                        "authors": authors,
                        "year": paper.get('year'),
                        "abstract": paper.get('abstract', ''),
                        "citation_count": citation_count,
                        "url": paper.get('url', ''),
                        "venue": paper.get('venue', ''),
                        "pdf_url": pdf_url
                    })
                
                self.logger.info(f"Found {len(papers)} papers")
                return papers
                
            elif response.status_code == 429:
                self.logger.warning("Rate limited by Semantic Scholar API. Try again later.")
                return []
            else:
                self.logger.error(f"API error {response.status_code}: {response.text}")
                return []
            
        except ImportError:
            self.logger.error("requests library not installed. Run: pip install requests")
            return []
        except Exception as e:
            self.logger.error(f"Error searching papers: {e}")
            return []

    async def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific paper.

        Args:
            paper_id: Semantic Scholar paper ID

        Returns:
            Detailed paper information
        """
        try:
            from semanticscholar import SemanticScholar
            
            sch = SemanticScholar(api_key=self.api_key)
            paper = sch.get_paper(paper_id)
            
            return {
                "paper_id": paper.paperId,
                "title": paper.title,
                "authors": [{"name": a.name} for a in paper.authors] if paper.authors else [],
                "year": paper.year,
                "abstract": paper.abstract,
                "citation_count": paper.citationCount,
                "url": paper.url,
                "venue": paper.venue,
                "pdf_url": paper.openAccessPdf.get("url") if paper.openAccessPdf else None,
            }
        except Exception as e:
            self.logger.error(f"Error getting paper details: {e}")
            return {}

    async def get_citations(self, paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get papers that cite this paper.

        Args:
            paper_id: Semantic Scholar paper ID
            limit: Maximum number of citations to retrieve

        Returns:
            List of citing papers
        """
        try:
            from semanticscholar import SemanticScholar
            
            sch = SemanticScholar(api_key=self.api_key)
            paper = sch.get_paper(paper_id)
            citations = paper.citations[:limit] if paper.citations else []
            
            return [
                {
                    "paper_id": c.paperId,
                    "title": c.title,
                    "year": c.year,
                }
                for c in citations
            ]
        except Exception as e:
            self.logger.error(f"Error getting citations: {e}")
            return []

    async def get_references(self, paper_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get papers referenced by this paper.

        Args:
            paper_id: Semantic Scholar paper ID
            limit: Maximum number of references to retrieve

        Returns:
            List of referenced papers
        """
        try:
            from semanticscholar import SemanticScholar
            
            sch = SemanticScholar(api_key=self.api_key)
            paper = sch.get_paper(paper_id)
            references = paper.references[:limit] if paper.references else []
            
            return [
                {
                    "paper_id": r.paperId,
                    "title": r.title,
                    "year": r.year,
                }
                for r in references
            ]
        except Exception as e:
            self.logger.error(f"Error getting references: {e}")
            return []

    def _parse_results(
        self,
        results: Any,
        year_from: Optional[int],
        year_to: Optional[int],
        min_citations: int
    ) -> List[Dict[str, Any]]:
        """
        Parse and filter search results from Semantic Scholar.
        
        Args:
            results: Raw results from Semantic Scholar API
            year_from: Minimum year filter
            year_to: Maximum year filter
            min_citations: Minimum citation count filter
            
        Returns:
            Filtered and formatted list of papers
        """
        papers = []
        
        for paper in results:
            # Skip papers without basic metadata
            if not paper or not hasattr(paper, 'title'):
                continue
                
            paper_dict = {
                "paper_id": paper.paperId if hasattr(paper, 'paperId') else None,
                "title": paper.title if hasattr(paper, 'title') else "Unknown",
                "authors": [{"name": a.name} for a in paper.authors] if hasattr(paper, 'authors') and paper.authors else [],
                "year": paper.year if hasattr(paper, 'year') else None,
                "abstract": paper.abstract if hasattr(paper, 'abstract') else "",
                "citation_count": paper.citationCount if hasattr(paper, 'citationCount') else 0,
                "url": paper.url if hasattr(paper, 'url') else "",
                "venue": paper.venue if hasattr(paper, 'venue') else "",
                "pdf_url": paper.openAccessPdf.get("url") if hasattr(paper, 'openAccessPdf') and paper.openAccessPdf else None,
            }
            
            papers.append(paper_dict)
        
        # Apply filters
        papers = self._filter_by_year(papers, year_from, year_to)
        papers = self._filter_by_citations(papers, min_citations)
        
        return papers

    def _filter_by_year(
        self,
        papers: List[Dict[str, Any]],
        year_from: Optional[int],
        year_to: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Filter papers by publication year."""
        filtered = papers
        if year_from:
            filtered = [p for p in filtered if p.get("year") and p.get("year") >= year_from]
        if year_to:
            filtered = [p for p in filtered if p.get("year") and p.get("year") <= year_to]
        return filtered

    def _filter_by_citations(
        self,
        papers: List[Dict[str, Any]],
        min_citations: int
    ) -> List[Dict[str, Any]]:
        """Filter papers by citation count."""
        return [p for p in papers if p.get("citation_count", 0) >= min_citations]


# Synchronous wrapper for use with AutoGen tools
def paper_search(query: str, max_results: int = 10, year_from: Optional[int] = None) -> str:
    """
    Synchronous wrapper for paper search (for AutoGen tool integration).
    
    Args:
        query: Search query
        max_results: Maximum results to return
        year_from: Only return papers from this year onwards
        
    Returns:
        Formatted string with paper results
    """
    tool = PaperSearchTool(max_results=max_results)
    results = asyncio.run(tool.search(query, year_from=year_from))
    
    if not results:
        return "No academic papers found."
    
    # Format results as readable text
    output = f"Found {len(results)} academic papers for '{query}':\n\n"
    
    for i, paper in enumerate(results, 1):
        authors = ", ".join([a["name"] for a in paper["authors"][:3]])
        if len(paper["authors"]) > 3:
            authors += " et al."
            
        output += f"{i}. {paper['title']}\n"
        output += f"   Authors: {authors}\n"
        output += f"   Year: {paper['year']} | Citations: {paper['citation_count']}"
        if paper.get('venue'):
            output += f" | Venue: {paper['venue']}"
        output += "\n"
        
        if paper.get('abstract'):
            abstract = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
            output += f"   Abstract: {abstract}\n"
            
        output += f"   URL: {paper['url']}\n"
        output += "\n"
    
    return output
