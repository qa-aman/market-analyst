from ddgs import DDGS

from src.config import FINANCIAL_DOMAINS


def search_stock_news(company_name: str, max_results: int = 8) -> list[dict]:
    """Search for recent stock news, filtering to financial domains post-search."""
    query = f"{company_name} stock news India"

    all_results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results * 2):
            all_results.append({
                "title": r.get("title", ""),
                "body": r.get("body", ""),
                "href": r.get("href", ""),
            })

    # Prioritize results from financial domains
    financial = []
    other = []
    for r in all_results:
        href = r.get("href", "")
        if any(domain in href for domain in FINANCIAL_DOMAINS):
            financial.append(r)
        else:
            other.append(r)

    # Return financial sources first, fill with others if needed
    results = (financial + other)[:max_results]
    return results
