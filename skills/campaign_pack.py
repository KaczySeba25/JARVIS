"""Create a reviewable promotion and product-listing content pack.

It drafts copy only. Publishing requires a separate approved connector action.
"""
from __future__ import annotations

import json

RISK_LEVEL = "medium"


def _payload(argument):
    if isinstance(argument, dict):
        return argument
    try:
        return json.loads(str(argument or "{}"))
    except (TypeError, ValueError):
        return {"product": str(argument or "")}


def run(argument=None):
    data = _payload(argument)
    product = str(data.get("product") or "Produkt").strip()[:180]
    audience = str(data.get("audience") or "osoby szukające praktycznego rozwiązania").strip()[:240]
    price = str(data.get("price") or "").strip()[:40]
    currency = str(data.get("currency") or "").strip()[:8]
    benefits = [str(item).strip()[:180] for item in (data.get("benefits") or [])[:8] if str(item).strip()]
    proof = [str(item).strip()[:180] for item in (data.get("proof") or [])[:5] if str(item).strip()]
    benefit_text = ", ".join(benefits) if benefits else "praktyczne zastosowanie i wygodę"
    proof_text = "; ".join(proof) if proof else "Do uzupełnienia po weryfikacji specyfikacji i dostawcy."
    price_text = f"{price} {currency}".strip() if price else "Cena do ustalenia po analizie marży."
    return {
        "ok": True,
        "product": product,
        "review_required": True,
        "publishing_performed": False,
        "listing": {
            "title": product,
            "short_description": f"{product} dla {audience}: {benefit_text}.",
            "description": f"Poznaj {product}. Najważniejsze korzyści: {benefit_text}. Cena robocza: {price_text}. Dowody/specyfikacja: {proof_text}",
            "price": price_text,
            "claims_to_verify": benefits,
        },
        "channels": {
            "instagram": f"{product}\n\n{benefit_text}.\n\n{price_text}\n\nSprawdź szczegóły i wybierz świadomie.\n\n#promocja #zakupy #technologia",
            "facebook": f"PROMOCJA: {product}\n\nDla kogo: {audience}.\nKorzyści: {benefit_text}.\nCena robocza: {price_text}.\n\nSpecyfikacja i dowody: {proof_text}",
            "tiktok": f"Czy szukasz: {product}?\n\n3 rzeczy: {benefit_text}.\nCena: {price_text}.\nSprawdź pełną specyfikację przed zakupem.",
        },
        "next": "Zweryfikuj twierdzenia, obrazy, cenę i zgodność z regulaminem kanału. Dopiero potem użyj zatwierdzonego konektora publikacji.",
    }
