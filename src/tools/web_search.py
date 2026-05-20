from agents import function_tool


@function_tool
def web_search(query: str) -> str:
    """Search the web for programming documentation, library references, or error explanations.

    Args:
        query: The search query, e.g. 'Python asyncio gather example'.
    """
    # Stub — replace with Tavily or SerpAPI in production
    return (
        f"Search results for '{query}':\n"
        f"1. Official docs: Comprehensive reference with examples.\n"
        f"2. Stack Overflow: Multiple answers with community votes.\n"
        f"3. Real Python: Beginner-friendly tutorial with code samples."
    )
