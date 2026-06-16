import os

import httpx
from tenacity import retry, reraise, retry_if_exception, stop_after_attempt, wait_exponential

WB_SEARCH_URL = "https://search.wb.ru/exactmatch/ru/common/v5/search"

_HEADERS = {
    "User-Agent": os.getenv(
        "WB_USER_AGENT",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    )
}


def _is_429(exc: BaseException) -> bool:
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429


@retry(
    retry=retry_if_exception(_is_429),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(4),
    reraise=True,
)
def _get(url: str, params: dict) -> dict:
    resp = httpx.get(url, params=params, headers=_HEADERS, timeout=10, follow_redirects=True)
    resp.raise_for_status()
    return resp.json()


def _normalize(p: dict) -> dict:
    return {
        "id": p["id"],
        "name": p.get("name", ""),
        "brand": p.get("brand", ""),
        "category": p.get("subjectName", ""),
        # WB stores price in 1/100 kopecks — divide by 100 to get rubles
        "price_rub": round(p.get("priceU", 0) / 100),
        "sale_price_rub": round(p.get("salePriceU", 0) / 100),
        "discount_pct": p.get("sale", 0),
        "rating": p.get("rating", 0.0),
        "reviews": p.get("feedbacks", 0),
    }


def get_products(query: str, limit: int = 100) -> list[dict]:
    """Search WB catalog by keyword. Returns normalized product list."""
    params = {
        "query": query,
        "resultset": "catalog",
        "limit": min(limit, 100),
        "sort": "popular",
        "page": 1,
    }
    data = _get(WB_SEARCH_URL, params)
    return [_normalize(p) for p in data.get("data", {}).get("products", [])]
