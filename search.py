import asyncio

from duckduckgo_search import DDGS


def _search_sync(query: str, max_results: int) -> list:
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


async def web_search(query: str, max_results: int = 5) -> str:
    """Ищет query в интернете и возвращает краткую сводку результатов."""
    if not query:
        return ""

    results = await asyncio.to_thread(_search_sync, query, max_results)
    if not results:
        return ""

    lines = []
    for r in results:
        title = r.get("title", "")
        body = r.get("body", "")
        href = r.get("href", "")
        lines.append(f"- {title}: {body} ({href})")

    return "\n".join(lines)
