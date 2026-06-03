"""
FRED API Tool for Research Agent Framework
Provides access to Federal Reserve Economic Data (FRED) for economic indicators and time series data
"""

import os
import requests
import json
from langchain_core.tools import tool

@tool
def fred_search(query: str) -> str:
    """
    Search FRED for economic data series including GDP, interest rates, unemployment, inflation,
    and other economic indicators. Use this tool for questions about economic data, financial metrics,
    macroeconomic indicators, monetary policy, labor statistics, and economic trends.

    Args:
        query: The search term for economic data (e.g., "GDP", "unemployment rate", "inflation")

    Returns:
        str: Formatted search results from FRED with economic data series information
    """
    try:
        # Get API key from environment
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            return "Error: FRED_API_KEY environment variable not set. Please obtain a free API key from https://fred.stlouisfed.org/docs/api/fred/"

        # FRED API endpoint for series search
        base_url = "https://api.stlouisfed.org/fred/series/search"

        # Search parameters
        params = {
            "search_text": query,
            "api_key": api_key,
            "file_type": "json",
            "limit": 5,
            "order_by": "popularity",
            "sort_order": "desc"
        }

        headers = {
            "User-Agent": "Research-Agent/1.0 (https://github.com/research-agent)"
        }

        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Check for API errors
        if "error_code" in data:
            return f"FRED API Error: {data.get('error_message', 'Unknown error')}"

        # Extract series data
        series_list = data.get("seriess", [])

        if not series_list:
            return f"No economic data series found for query: '{query}'"

        # Format results
        results = []
        for series in series_list[:5]:
            try:
                series_id = series.get("id", "N/A")
                title = series.get("title", "No title")
                units = series.get("units", "N/A")
                frequency = series.get("frequency", "N/A")
                last_updated = series.get("last_updated", "N/A")
                notes = series.get("notes", "")[:150] + "..." if series.get("notes") else "No description"

                results.append(f"**{title}** (ID: {series_id})\nUnits: {units} | Frequency: {frequency}\nLast Updated: {last_updated}\nDescription: {notes}")

            except Exception as e:
                continue  # Skip malformed entries

        if results:
            return f"FRED economic data search results for '{query}':\n\n" + "\n\n".join(results)
        else:
            return f"Found entries but could not parse results for query: '{query}'"

    except requests.RequestException as e:
        return f"Error accessing FRED API: {str(e)}"
    except json.JSONDecodeError as e:
        return f"Error parsing FRED response: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def test_fred_search(query):
    """Test function for the FRED tool"""
    return fred_search.invoke({"query": query})