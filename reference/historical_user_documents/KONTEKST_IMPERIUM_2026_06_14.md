# Kontekst Imperium

Stan na: 2026-06-14  
Projekt: `C:\sebsmegastoreai`  
Sklep: `https://sebsmegastore-2.myshopify.com`  
Nazwa sklepu w Shopify: `SebsMegaStore`  
Waluta: `GBP`  
Rynek bazowy: `United Kingdom`  
Strefa czasu sklepu: `Europe/London`

## 1. Czym jest Imperium

Imperium to warstwa operacyjna i decyzyjna dla sklepu SebsMegaStore. Nie jest pojedynczym skryptem do importowania produktów. Jest to lokalny system zarządzania ecommerce, którego zadaniem jest:

- znajdować kandydatów produktowych,
- sprawdzać koszt, marżę, jakość i sens biznesowy,
- publikować tylko bezpieczniejsze i mocniejsze pozycje,
- porządkować sklep po imporcie,
- mierzyć sprzedaż i sygnały zainteresowania,
- przygotowywać raporty,
- korygować ustawienia na podstawie danych operacyjnych.

Założenie biznesowe repo pozostaje spójne we wszystkich głównych plikach i raportach: lepszy jest mniejszy, czystszy, bardziej dochodowy katalog niż masowy, chaotyczny import.

## 2. Tożsamość sklepu

SebsMegaStore jest pozycjonowany jako sklep z praktycznymi, AI-kuracyjnymi produktami dla klienta z UK. Warstwa komunikacyjna sklepu akcentuje:

- użyteczne zakupy zamiast przypadkowego scrollowania,
- oferty sprawdzane pod kątem wartości i jakości,
- szybkie wejście przez działy, wyszukiwanie albo AI Finder,
- katalog skupiony na codziennym zastosowaniu.

W live theme sklepu ustawione są:

- e-mail wsparcia: `megastoreai@protonmail.com`,
- kolor główny: `#14213D`,
- kolor akcentu: `#FFB703`,
- kolor tła pomocniczego: `#F8F3E8`.

## 3. Najważniejsza zasada operacyjna

Cały system jest zbudowany wokół bramek jakości i zysku. W praktyce Imperium nie powinno traktować draftów jak śmietnika i nie powinno publikować produktu bez przejścia przez kontrolę:

- kosztu,
- ceny końcowej,
- zysku netto,
- marży netto,
- jakości zdjęć,
- duplikatu,
- sensowności tytułu,
- zgodności kategorii,
- wiarygodności dostawcy,
- sygnału rynkowego albo przynajmniej benchmarku cenowego.

## 4. Aktualny obraz sklepu na 2026-06-14

Na podstawie bieżących raportów i bezpośredniego odczytu Shopify:

- wszystkie produkty: `1176`,
- produkty aktywne w Shopify: `404`,
- produkty w draft: `36`,
- produkty zarchiwizowane: `736`,
- produkty opublikowane do storefrontu web: `376`,
- produkty z realnym tagiem kosztowym: `1147`,
- produkty bez tagu kosztowego: `29`,
- aktywne produkty bez kosztu według najnowszego repair report: `0`,
- aktywne produkty bez obrazów według command center: `0`,
- aktywne hard-risk items: `54`,
- aktywne produkty w sweet spot: `276`,
- średnia cena aktywnego produktu: `GBP 24.28`,
- promowalne produkty: `305`,
- wygenerowane posty social: `112`,
- zdarzenia storefront z ostatnich 30 dni: `676`,
- zamówienia z ostatnich 30 dni: `1`.

Najwyżej wycenione produkty w katalogu pokazują, że sklep ma mieszany profil: od niskiego i średniego koszyka po pojedyncze pozycje high-ticket.

## 5. Warstwa sterowania

Najważniejsze entrypointy i procesy sterujące:

- `master_system.py`  
  Historyczny punkt wejścia dla całości.

- `imperium_engine\imperium_controller.py`  
  Kontroler 24/7 odpowiedzialny za monitoring sklepu, self-heal, dashboardy, pamięć systemu i wybrane korekty operacyjne.

- `imperium_engine\autonomous_growth_controller.py`  
  Główny Growth Brain. Łączy sourcing, scoring, market research, pricing, finalizację w Shopify, analitykę, dzienne podsumowanie, alerty, self-heal i safety gate.

- `imperium_autopilot_15m.py` oraz Task Scheduler  
  Z dokumentacji repo wynika, że autopilot działa cyklicznie jako zaplanowany worker.

## 6. Aktualny tryb autopilota

Z najnowszego `data\IMPERIUM_AUTOPILOT_STATUS.md`:

- tryb: `every 20 minutes`,
- target total: `1 (derived=2)`,
- auto publish: `True`,
- create status: `active`,
- Hermes mode: `safe_live`,
- Hermes campaign: `trust_value_2026_social`,
- market limit: `6`,
- no product writes: `False`.

W bieżącym cyklu:

- dostępni dostawcy: `AW Dropship UK`, `CJ Dropshipping`,
- utworzone produkty: `0`,
- odrzucone / pominięte po analizie: `2`,
- self-healed / archived: `0`,
- błędy: `0`.

Główne sygnały kontekstowe w tym samym statusie:

- aktywne produkty: `404`,
- ostatnie sygnały odrzucenia: `no_candidate_passed_all_gates:1`,
- przykładowe phrase trendowe: `under sink organizer`, `drawer organizer`, `cable organizer box`, `portable tyre inflator`, `precision screwdriver set`, `socket wrench set`.

## 7. Warstwa decyzyjna produktu

Trzon decyzji produktowych tworzą:

- `imperium_engine\modules\product_scorer.py`
- `imperium_engine\modules\quality_guard.py`
- `imperium_engine\modules\market_research.py`
- `imperium_engine\modules\pricing_intelligence.py`
- `imperium_engine\modules\hit_scorer.py`
- `imperium_engine\modules\content_generator.py`
- `imperium_engine\modules\shopify_finalizer.py`

Rola modułów:

- `ProductScorer` ocenia niszę, cenę, marżę, konkurencję, trend, dostawcę i logistykę.
- `ProductQualityGuard` filtruje tytuły-śmieci, artefakty marketplace, ryzyka brandowe, kategorie niskiej jakości i problemy obrazowe.
- `MarketResearcher` buduje benchmark cenowy i confidence rynkowy z wielu źródeł oraz fallbacków.
- `PricingIntelligence` liczy ekonomię produktu, psych pricing, profit floor i sufit wartości percepcyjnej.
- `HitScorer` zamienia wynik biznesowy i rynkowy na końcową decyzję `publish`, `draft` albo `reject`.
- `ContentGenerator` generuje SEO title, meta description, opis HTML, tagi, słowa kluczowe i hashtagi.
- `ShopifyFinalizer` tworzy i aktualizuje produkty w Shopify, przypisuje kolekcje i pracuje z retry/backoff.

## 8. Główne progi i parametry biznesowe

Z konfiguracji i nadpisów systemowych:

- sweet spot cenowy: `GBP 9.99 - GBP 29.99`,
- bazowy markup: `2.5x`,
- VAT UK: `20%`,
- minimalna marża netto: `28%`,
- minimalny zysk absolutny w głównej konfiguracji: `GBP 5.00`,
- w aktywnych override dla części procesu: `GBP 3.00`,
- minimalna liczba zdjęć dla growth: `3`,
- maksymalny budżet czasu cyklu Growth Brain: `900 s`,
- maksymalna liczba publikacji na cykl: `1`,
- maksymalna liczba draftów na cykl: `3`,
- kill switch max drafts per cycle: `3`.

## 9. Module Brain i auto-tuning

`imperium_engine\modules\module_brain.py` to pamięć i warstwa sterowania parametrami modułów. Utrzymuje:

- `data\imperium\brain\module_tuning_overrides.json`
- `data\imperium\brain\module_events.jsonl`

Aktualne aktywne override zapisane w `data\IMPERIUM_MODULE_BRAIN_STATUS.md` obejmują między innymi:

- `autonomous_growth_controller`
- `hit_scorer`
- `market_research`
- `pricing_intelligence`
- `product_scorer`
- `quality_guard`

Najważniejszy sens tej warstwy:

- system nie jest twardo zaszyty raz na zawsze,
- próg publikacji i draftu może być regulowany,
- timeouty i limity zapytań mogą być dostosowane,
- preferowane nisze i blocked keywords są utrzymywane jako sterowalna polityka.

## 10. Dostawcy i kanały produktowe

### 10.1 AW Dropship UK

AW jest obecne w repo na kilku poziomach:

- `imperium_engine\modules\aw_dropship_connector.py`
- raporty połączenia dostawcy,
- aktywne produkty z vendorami `AW Dropship UK` i `AW Dropship`,
- tagi i badging na storefront.

Z bieżących danych:

- aktywne produkty vendor `AW Dropship UK`: `63`,
- aktywne produkty vendor `AW Dropship`: `5`,
- produkty powiązane z markerami AW w Shopify: `50`.

W command center AW jest traktowany jako dostawca zaufany warunkowo, w trybie `restricted_quality_only`.

### 10.2 CJ Dropshipping

CJ jest zintegrowane jako bezpośredni connector:

- `imperium_engine\modules\cj_connector.py`
- vendor `CJ Dropshipping` występuje aktywnie w katalogu,
- produkty mają tagi typu `cj_pid`,
- command center widzi CJ jako dostawcę bezpośredniego.

Z bieżących danych:

- aktywne produkty vendor `CJ Dropshipping`: `53`.

### 10.3 DSers / AliExpress

W repo i dokumentacji DSers / AliExpress jest opisane jako działający kanał importowy po stronie Shopify:

- produkty trafiają do Shopify przez workflow DSers / AliExpress,
- Imperium pracuje na nich już po pojawieniu się w Shopify,
- aktywni vendorzy `AliExpress` i `AliExpress Trend` występują w sklepie,
- command center opisuje DSers/AliExpress jako `manual_push_required`,
- w statusie autopilota AliExpress jest opisane jako `automated via bridge (3x daily via Task Scheduler)`.

Z bieżących danych:

- aktywne produkty vendor `AliExpress`: `9`,
- aktywne produkty vendor `AliExpress Trend`: `2`.

### 10.4 Avasam, Eprolo, Syncee

Repo i historyczna dokumentacja pokazują, że te źródła były rozpoznawane i diagnozowane, ale ich rola jest wtórna wobec AW, CJ i kanału AliExpress/DSers.

## 11. Struktura katalogu sklepu

Potwierdzony stan Shopify:

- stron CMS: `19`,
- smart collections: `2`,
- custom collections: `130`,
- aktywny theme: `AI Magnet Theme - Codex 2026-05-09`,
- theme ID: `188500181316`,
- role theme: `main`.

## 12. Główne strony sklepu

Na żywo potwierdzone są między innymi następujące page handles:

- `about-us`
- `ai-personal-shopper`
- `ai-shopping-guide`
- `car-accessories-uk`
- `camping-outdoor-essentials-uk`
- `deals-under-30-uk`
- `home-kitchen-useful-finds-uk`
- `useful-tech-gadgets-uk`
- `contact`
- `faq`
- `order-help`
- `shipping-policy`
- `returns-refunds`
- `privacy-policy`
- `terms-of-service`
- `refund-policy`
- `return-policy`
- `review-submission`

To pokazuje, że sklep nie jest tylko katalogiem produktów. Ma również warstwę informacyjną i obsługową.

## 13. Główne kolekcje i merchandising

Najważniejsze kolekcje potwierdzone w Shopify:

- `car-motoring`
- `electronics-tech`
- `tools-hardware`
- `camping-outdoors`
- `home-kitchen`
- `garden-diy`
- `pet-supplies`
- `deals-under-30`
- `live-hot` jako `Checked Deals`
- `smart-finds-under-30`
- `ai-product-hits`
- `ai-personal-shopper`
- `high-ticket-picks`
- `ai-camping-gear`
- `ai-giftable-home-finds`
- `ai-outdoor-essentials`
- `aw-dropship-curated-home-wellness`
- `smart-mini-projectors`

Potwierdzone liczby produktów w kluczowych kolekcjach:

- `Car & Motoring`: `96`
- `Electronics & Tech`: `197`
- `Tools & Hardware`: `34`
- `Camping & Outdoors`: `130`
- `Home & Kitchen`: `467`
- `Garden & DIY`: `78`
- `Pet Supplies`: `47`
- `Deals Under GBP 30`: `707`
- `Checked Deals`: `1029`
- `Smart Finds Under GBP 30`: `715`
- `AI Product Hits`: `486`
- `AI Personal Shopper`: `60`

## 14. Aktualna logika storefrontu

Theme w `shopify_theme_ai_magnet\` buduje doświadczenie zakupowe wokół trzech wejść:

- działów,
- wyszukiwania,
- AI Finder.

Strona główna w `templates\index.json` renderuje:

- `hero`,
- `marketplace-categories`,
- `problem-paths`,
- `shopping-paths`,
- `live-hot-pick`.

To oznacza, że storefront ma być problem-led i intent-led, a nie losowym feedem produktów.

## 15. Co storefront komunikuje klientowi

Z plików theme wynika wyraźna obietnica sklepu:

- AI-curated shelves,
- cost and image checked,
- practical UK-focused finds,
- checked deals under GBP 30,
- szybkie przejście do działów i wyszukiwania,
- pomoc posprzedażowa przez `order-help`, `faq`, `shipping`, `returns`.

## 16. Tracking, analityka i pamięć klienta

System posiada osobną warstwę zbierania sygnałów storefront:

- `analytics_collector.py`
- `shopify_storefront_tracker.js`
- `imperium_engine\modules\storefront_analytics.py`

Dane zapisywane są do:

- `data\storefront_events.db`
- `data\storefront_events.jsonl`

Dozwolone eventy:

- `page_view`
- `product_view`
- `product_click`
- `image_click`
- `add_to_cart`
- `search`
- `collection_click`

Najnowszy raport storefront analytics pokazuje:

- `676` eventów w oknie 30 dni,
- jeden produkt z wykrytym zainteresowaniem,
- osobny ranking sygnałów na poziomie produktu.

## 17. Orders analytics i performance

Warstwa po sprzedaży opiera się na:

- `imperium_engine\modules\shopify_orders_analytics.py`
- `imperium_engine\modules\performance_tracker.py`

Najnowszy raport zamówień:

- okno: `30 days`,
- zamówienia: `1`,
- sprzedane produkty: `1`,
- gross sales: `GBP 1.0`,
- estimated profit: `GBP 0.85`.

Najnowszy performance report:

- winners: `1`,
- dead products: `0`,
- review needed: `239`.

## 18. Self-heal, raporty i kontrola ryzyka

Najważniejsze bieżące raporty operacyjne:

- `data\IMPERIUM_AUTOPILOT_STATUS.md`
- `data\IMPERIUM_COMMAND_CENTER_LATEST.md`
- `data\growth_brain_report.md`
- `data\growth_safety_gate_report.md`
- `data\growth_brain_self_heal_report.md`
- `data\profit_dashboard.md`
- `data\performance_report.md`
- `data\orders_analytics.md`
- `data\storefront_analytics.md`
- `data\system_alerts.md`
- `data\cost_tag_repair_report.md`
- `data\supplier_connection_report.md`
- `data\daily_summaries\YYYY-MM-DD.md`

To repo jest bardzo mocno raportocentryczne. Prawie każda większa operacja ma odpowiadający jej ślad w `data\`.

## 19. System marketingowo-operacyjny wokół sklepu

Poza samym sourcingiem i storefrontem, repo zawiera też gotowe warstwy wspierające skalowanie:

- `customer_magnet_engine.py`
- `organic_asset_pack_generator.py`
- `automation_roi_report.py`
- `automation_competitor_gap_report.py`
- `supplier_monitoring_watchdog.py`
- `order_fulfillment_exception_queue.py`
- `customer_support_kb_generator.py`
- `shopify_flow_playbook.py`

Ich rola:

- wybierać produkty promowalne,
- tworzyć kolekcje i strony kampanijne,
- generować assety organiczne i copy,
- liczyć zwrot operacyjny z automatyzacji,
- pilnować ryzyk dostawców,
- budować kolejkę wyjątków fulfillment,
- utrzymywać bazę wiedzy supportu,
- przygotowywać playbook dla workflow w Shopify Flow.

## 20. Co system już realnie zrobił historycznie

Z aktualnych raportów można potwierdzić między innymi:

- `89` repricingów w pełnym incremental competitor audit,
- `354` archiwizacji w tym samym procesie audytu katalogu,
- `74` historycznych publikacji w learning totals,
- `594` historycznych odrzuceń w learning totals,
- `305` produktów promowalnych,
- `112` wygenerowanych postów social.

## 21. Główne ryzyka i napięcia strategiczne na dziś

Najważniejsze rzeczy, które kontekstowo definiują obecną fazę projektu:

- sklep jest już duży katalogowo, ale nadal wymaga ostrzejszej kuracji,
- aktywnych hard-risk produktów jest nadal `54`,
- storefront i merchandising są już rozbudowane, ale nadal są obszary underfilled według command center,
- system jest dojrzały raportowo, ale nadal przechodzi etap stabilizacji decyzyjnej,
- priorytetem nie jest masowy wzrost liczby live produktów, tylko jakość, zysk i spójność.

## 22. Priorytety zapisane w repo

Aktualne priorytety z instrukcji projektowych:

1. Naprawić `daily_summary.py` `NameError: traffic`.
2. Udostępnić `analytics_collector.py` przez publiczny endpoint HTTPS.
3. Podłączyć tracking Shopify do publicznego endpointu.
4. Potwierdzić AW Dropship fulfillment / order API.
5. Dodać lub naprawić brakujące tagi kosztowe dla live produktów.
6. Poprawić scoring, logging, timeout handling i self-heal Growth Brain.

## 23. Ważna nota o spójności źródeł

W repo są zarówno opisy historyczne, jak i bieżące raporty generowane automatycznie. Gdy źródła różnią się między sobą, największy ciężar należy dawać:

- bezpośredniemu odczytowi Shopify Admin,
- najnowszym raportom w `data\`,
- aktualnym plikom theme i konfiguracji,
- bieżącym statusom autopilota i command center.

## 24. Najkrótsza definicja Imperium

Imperium to lokalny, raportowany, Shopify-first system AI, który ma działać jak ostrożny manager sklepu:

- kurator katalogu,
- strażnik marży,
- operator storefrontu,
- notariusz zmian w `data\`,
- i warstwa samoregulacji dla procesu sourcingu, publikacji oraz czyszczenia sklepu.
