import statistics
from typing import List, Dict, Any

def extract_prices(item_summary_response: Dict[str, Any]) -> List[float]:
    items = item_summary_response.get("itemSummaries", []) or []
    prices = []
    for it in items:
        price = it.get("price") or {}
        val = price.get("value")
        cur = price.get("currency")
        if val is None:
            continue
        try:
            fv = float(val)
            if cur == "EUR":
                prices.append(fv)
        except:
            pass
    return prices

def summarize(prices: List[float]) -> Dict[str, float]:
    if not prices:
        return {"count": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "count": len(prices),
        "min": min(prices),
        "median": statistics.median(prices),
        "mean": round(sum(prices)/len(prices), 2),
        "max": max(prices),
    }
