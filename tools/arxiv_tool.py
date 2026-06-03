"""
arXiv API Tool for Research Agent Framework
Provides arXiv paper search capabilities using the free arXiv API
"""

import requests
import xml.etree.ElementTree as ET
from langchain_core.tools import tool

@tool
def arxiv_search(query: str) -> str:
    """
    Search arXiv for academic papers, research publications, and scientific literature.
    Use this tool for academic questions, research topics, scientific studies, technical papers,
    recent research findings, and scholarly information in fields like physics, mathematics,
    computer science, biology, and other academic disciplines.

    Args:
        query: The search term to look up on arXiv (e.g., "machine learning", "quantum computing")

    Returns:
        str: Formatted search results from arXiv with paper titles, authors, and abstracts
    """
    try:
        # arXiv API endpoint
        base_url = "http://export.arxiv.org/api/query"

        # Prepare search parameters
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": 5,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        headers = {
            "User-Agent": "Research-Agent/1.0 (https://github.com/research-agent)"
        }

        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse XML response
        root = ET.fromstring(response.content)

        # Define namespaces
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        # Extract entries
        entries = root.findall('.//atom:entry', namespaces)

        if not entries:
            return f"No arXiv papers found for query: '{query}'"

        # Format results
        results = []
        for entry in entries[:5]:
            try:
                title = entry.find('atom:title', namespaces)
                title = title.text.strip() if title is not None else "No title"

                authors = entry.findall('atom:author/atom:name', namespaces)
                author_names = [author.text for author in authors if author.text]
                author_str = ", ".join(author_names[:3])  # Limit to first 3 authors
                if len(author_names) > 3:
                    author_str += " et al."

                summary = entry.find('atom:summary', namespaces)
                summary = summary.text.strip()[:200] + "..." if summary is not None else "No summary"

                published = entry.find('atom:published', namespaces)
                pub_date = published.text[:10] if published is not None else "Unknown date"

                arxiv_id = entry.find('atom:id', namespaces)
                paper_url = arxiv_id.text if arxiv_id is not None else ""

                results.append(f"**{title}**\nAuthors: {author_str}\nPublished: {pub_date}\nSummary: {summary}\nURL: {paper_url}")

            except Exception as e:
                continue  # Skip malformed entries

        if results:
            return f"arXiv search results for '{query}':\n\n" + "\n\n".join(results)
        else:
            return f"Found entries but could not parse results for query: '{query}'"

    except requests.RequestException as e:
        return f"Error searching arXiv: {str(e)}"
    except ET.ParseError as e:
        return f"Error parsing arXiv response: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def test_arxiv_search(query):
    """Test function for the arXiv tool"""
    return arxiv_search.invoke({"query": query})