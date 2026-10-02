import os
from dotenv import load_dotenv

load_dotenv()

# Keep web search optional so the core agent can still start when the
# Tavily package/key is unavailable. The tool returns a normal failure
# object instead of crashing the entire backend at import time.
try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

api_key = os.getenv("TAVILY_API_KEY")
client = TavilyClient(api_key=api_key) if TavilyClient and api_key else None


def search_web(query):
    if not query or not query.strip():
        return {
            "success": False,
            "query": query,
            "answer": "",
            "sources": [],
            "error": "Search query cannot be empty."
        }

    if client is None:
        return {
            "success": False,
            "query": query,
            "answer": "",
            "sources": [],
            "error": "Web search is unavailable. Install tavily-python and configure TAVILY_API_KEY."
        }

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5
        )

        results = response.get("results", [])
        sources = [
            {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", "")
            }
            for result in results
        ]

        answer_parts = []
        for result in results[:5]:
            title = result.get("title", "")
            content = result.get("content", "")
            if content:
                answer_parts.append(f"{title}: {content}")

        return {
            "success": True,
            "query": query,
            "answer": "\n\n".join(answer_parts),
            "sources": sources
        }

    except Exception as e:
        return {
            "success": False,
            "query": query,
            "answer": "",
            "sources": [],
            "error": str(e)
        }


if __name__ == "__main__":
    query = input("Enter a search query: ")
    print("\nSearch Result:")
    print(search_web(query))
