import os
import httpx
from fastmcp import FastMCP


mcp = FastMCP("Apex AI Research")


@mcp.tool()
def search_web(
    query: str,
    max_results: int = 5,
) -> dict:
    """Search the web and return relevant results."""
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY is not configured")

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    max_results = max(1, min(max_results, 10))

    response = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        },
        timeout=30,
    )
    response.raise_for_status()
    search_results = response.json()

    results = [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
        }
        for item in search_results.get("results", [])
    ]

    return {
        "query": query,
        "results": results,
    }


if __name__ == "__main__":
    mcp.run()