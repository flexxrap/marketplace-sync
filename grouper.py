from collections import defaultdict


def group_products(products: list[dict]) -> list[dict]:
    """Group products by (category, brand) and compute price/rating aggregates.

    Returns rows sorted by item count descending.
    """
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for p in products:
        key = (p.get("category", ""), p.get("brand", ""))
        buckets[key].append(p)

    result = []
    for (category, brand), items in buckets.items():
        prices = [p["sale_price_rub"] for p in items]
        ratings = [p["rating"] for p in items if p.get("rating")]
        result.append(
            {
                "category": category,
                "brand": brand,
                "count": len(items),
                "avg_price_rub": round(sum(prices) / len(prices), 2),
                "min_price_rub": min(prices),
                "max_price_rub": max(prices),
                "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
            }
        )

    return sorted(result, key=lambda x: x["count"], reverse=True)
