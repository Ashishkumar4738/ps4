from ddgs import DDGS
from logger_config import logger

def web_search(query, max_results=5):
    """
    Search the web using DuckDuckGo.

    Returns:
        list[dict]: Search results.
    """
    logger.info(f"Performing web search for query: {query} with max results: {max_results}")
    try:
        results = DDGS().text(
            query,
            max_results=max_results
        )

        return results

    except Exception as e:
        logger.error(f"[WEB SEARCH ERROR] {e}")
        return []


def news_search(query, max_results=5):
    """
    Search recent news using DuckDuckGo.

    Returns:
        list[dict]: News results.
    """
    logger.info(f"Performing news search for query: {query} with max results: {max_results}")
    try:
        results = DDGS().news(
            query,
            max_results=max_results
        )
        return results

    except Exception as e:
        logger.error(f"[NEWS SEARCH ERROR] {e}")
        return []


if __name__ == "__main__":

    print("\n=== WEB SEARCH TEST ===")

    results = web_search("current weather of pune city", 5)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title')}")
        print(f"   {result.get('href')}")
        print(f"   {result.get('body')}")

    print("\n=== NEWS SEARCH TEST ===")

    results = news_search("latest technology news", 5)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title')}")
        print(f"   {result.get('url')}")
        print(f"   {result.get('body')}")