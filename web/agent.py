from search import web_search, news_search


class WebAgent:
    """
    Handles online information requests.

    Uses DuckDuckGo for web and news searches.
    """

    def search(self, query, max_results=5):
        print(f"[WEB AGENT] Searching web: {query}")

        results = web_search(
            query,
            max_results=max_results
        )

        return results

    def news(self, query, max_results=5):
        print(f"[WEB AGENT] Searching news: {query}")

        results = news_search(
            query,
            max_results=max_results
        )

        return results

    def format_results(self, results):
        """
        Convert raw search results into clean text
        for the LLM.
        """
    
        if not results:
            return "No search results found."
    
        formatted = []
        result_number = 1
    
        for result in results:
        
            title = result.get("title", "").strip()
            url = (result.get("href") or result.get("url") or "").strip()
            body = (
                result.get("body")
                or result.get("snippet")
                or ""
            ).strip()
    
            # Ignore incomplete results
            if not title or not url:
                continue
            
            # Ignore obvious advertising/redirect results
            if "aclick?" in url:
                continue
            
            formatted.append(
                f"{result_number}. {title}\n"
                f"URL: {url}\n"
                f"Summary: {body}"
            )
    
            result_number += 1
    
        if not formatted:
            return "No useful search results found."
    
        return "\n\n".join(formatted)


if __name__ == "__main__":

    agent = WebAgent()

    print("\n=== WEB AGENT TEST ===")

    results = agent.search(
        "current weather of Pune city",
        5
    )

    print("\n" + agent.format_results(results))