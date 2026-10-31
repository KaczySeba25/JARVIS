"""Research suppliers and competitors for a user-described product.

This skill is read-only: it searches public sources, fetches public pages and
returns evidence for the model. It never buys, publishes or logs in.
"""
from __future__ import annotations

import json
import re
from urllib.parse import urlparse

try:
    from research_engine import fetch, search
except ImportError:
    from agent.research_engine import fetch, search

RISK_LEVEL = "medium"
_PRICE_RE = re.compile(r"(?i)(?:[$€£]\s?\d+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?\s?(?:USD|EUR|GBP|zł|PLN))")


def _payload(argument):
    if isinstance(argument, dict):
        return argument
    text = str(argument or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return {"product": text}


def _query(product: str, group: str, capacity: str = "") -> str:
    suffix = f" {capacity}" if capacity else ""
    if group == "supplier":
        return f"{product}{suffix} wholesale supplier price official product page"
    return f"{product}{suffix} price competitors Amazon eBay official product listing"


def _item(result, group, product, capacity):
    url = result.get("url", "")
    title = result.get("title", "")
    text = result.get("snippet", "")
    fetched = False
    if url:
        try:
            page = fetch(url)
            text = page.get("text", "")[:4000]
            title = page.get("title") or title
            fetched = True
        except Exception:
            pass
    prices = _PRICE_RE.findall(text)
    return {
        "group": group,
        "product": product,
        "capacity": capacity,
        "title": title[:240],
        "url": url[:800],
        "domain": urlparse(url).netloc,
        "prices_found": prices[:8],
        "excerpt": text[:1200],
        "fetched": fetched,
        "source_score": result.get("score", 0),
    }


def run(argument=None):
    data = _payload(argument)
    product = str(data.get("product") or "").strip()[:200]
    if not product:
        return {"ok": False, "error": "product_required", "message": "Podaj produkt do researchu."}
    capacities = data.get("capacities") or [""]
    capacities = [str(item).strip()[:60] for item in capacities[:10] if str(item).strip()] or [""]
    max_results = max(1, min(int(data.get("max_results", 4) or 4), 6))
    output = {"ok": True, "product": product, "capacities": capacities, "read_only": True, "supplier_sources": [], "competitor_sources": [], "warnings": []}
    for capacity in capacities:
        for group, key in (("supplier", "supplier_sources"), ("competitor", "competitor_sources")):
            query = _query(product, group, capacity)
            results = search(query, max_results)
            for result in results[:max_results]:
                output[key].append(_item(result, group, product, capacity))
    if not output["supplier_sources"]:
        output["warnings"].append("Nie znaleziono wiarygodnych źródeł dostawców.")
    if not output["competitor_sources"]:
        output["warnings"].append("Nie znaleziono źródeł konkurencji.")
    output["next"] = "Przekaż wynik do offer_analysis po uzupełnieniu rzeczywistego kosztu dostawy, opłat i ceny sprzedaży."
    return output
