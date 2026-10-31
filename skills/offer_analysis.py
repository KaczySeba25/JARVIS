"""Deterministic offer and margin analysis for agent decisions."""
from __future__ import annotations

import json

RISK_LEVEL = "low"


def _payload(argument):
    if isinstance(argument, dict):
        return argument
    try:
        return json.loads(str(argument or "{}"))
    except (TypeError, ValueError):
        return {}


def _number(value, default=0.0):
    try:
        return float(str(value).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        return default


def run(argument=None):
    data = _payload(argument)
    offers = data.get("offers") or []
    currency = str(data.get("currency") or "USD")[:8]
    default_fee = _number(data.get("platform_fee_percent"), 0.0)
    results = []
    for index, offer in enumerate(offers[:200]):
        if not isinstance(offer, dict):
            continue
        cost = _number(offer.get("cost"))
        shipping = _number(offer.get("shipping"))
        other = _number(offer.get("other_costs"))
        sell = _number(offer.get("sell_price"))
        fee_percent = _number(offer.get("platform_fee_percent"), default_fee)
        fee = sell * fee_percent / 100.0
        landed = cost + shipping + other
        profit = sell - landed - fee
        margin = (profit / sell * 100.0) if sell else 0.0
        results.append({
            "index": index,
            "name": str(offer.get("name") or offer.get("title") or f"Oferta {index + 1}")[:240],
            "source": str(offer.get("source") or "")[:240],
            "url": str(offer.get("url") or "")[:800],
            "currency": currency,
            "cost": round(cost, 2),
            "shipping": round(shipping, 2),
            "other_costs": round(other, 2),
            "sell_price": round(sell, 2),
            "platform_fee": round(fee, 2),
            "landed_cost": round(landed, 2),
            "profit": round(profit, 2),
            "margin_percent": round(margin, 2),
            "complete_cost_data": bool(offer.get("cost") is not None and offer.get("sell_price") is not None),
        })
    ranked = sorted(results, key=lambda item: (item["profit"], item["margin_percent"]), reverse=True)
    minimum_margin = _number(data.get("minimum_margin_percent"), 0.0)
    eligible = [item for item in ranked if item["complete_cost_data"] and item["margin_percent"] >= minimum_margin]
    return {
        "ok": True,
        "currency": currency,
        "minimum_margin_percent": minimum_margin,
        "offers_analyzed": len(results),
        "ranked_offers": ranked,
        "recommended": eligible[0] if eligible else None,
        "warnings": [] if eligible else ["Brak kompletnej oferty spełniającej wymagany próg marży."],
        "decision_note": "Nie uwzględniono podatków, zwrotów, reklam, kursów walut ani ryzyka dostawcy, jeśli nie podano ich w danych.",
    }
