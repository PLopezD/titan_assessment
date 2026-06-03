"""
Wikipedia API Tool for Research Agent Framework
Provides Wikipedia search and article retrieval capabilities using the free Wikipedia API
"""

import requests
from langchain_core.tools import tool

@tool
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for general knowledge, encyclopedic information, and background on topics.
    Use this tool for questions about history, science, geography, biographies, definitions,
    general concepts, and educational content.

    Args:
        query: The search term to look up on Wikipedia

    Returns:
        str: Formatted search results from Wikipedia
    """
    try:
        # Use Wikipedia's standard API for search
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": 3,
            "format": "json"
        }

        headers = {
            "User-Agent": "Research-Agent/1.0 (https://github.com/research-agent)"
        }

        response = requests.get(search_url, params=search_params, headers=headers, timeout=10)
        response.raise_for_status()

        search_results = response.json()

        if not search_results.get("query", {}).get("search"):
            return f"No Wikipedia articles found for query: {query}"

        # Format results
        results = []
        for page in search_results["query"]["search"][:3]:
            title = page.get("title", "")
            snippet = page.get("snippet", "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
            results.append(f"- **{title}**: {snippet}")

        return f"Wikipedia search results for '{query}':\n" + "\n".join(results)

    except requests.RequestException as e:
        return f"Error searching Wikipedia: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def test_wikipedia_search(query):
    """Test function for the Wikipedia tool"""
    return wikipedia_search.invoke({"query": query})


def wikipedia_get_page(page_title, summary_length=500):
    """Get content from a specific Wikipedia page"""
    try:
        # Get page summary
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title.replace(' ', '_')}"

        headers = {
            "User-Agent": "Research-Agent/1.0 (https://github.com/research-agent)"
        }

        response = requests.get(summary_url, headers=headers, timeout=10)
        response.raise_for_status()

        page_data = response.json()

        # Extract key information
        title = page_data.get("title", "")
        extract = page_data.get("extract", "")
        page_url = page_data.get("content_urls", {}).get("desktop", {}).get("page", "")

        # Truncate extract if too long
        if len(extract) > summary_length:
            extract = extract[:summary_length] + "..."

        result = f"**{title}**\n\n{extract}"
        if page_url:
            result += f"\n\nFull article: {page_url}"

        return result

    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response.status_code == 404:
            return f"Wikipedia page not found: {page_title}"
        return f"Error retrieving Wikipedia page: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

