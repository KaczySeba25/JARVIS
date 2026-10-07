# Opis Sklepu i Systemu

Stan na: 2026-06-14  
Zakres dokumentu: tylko elementy potwierdzone jako podłączone, obecne w sklepie lub działające w systemie.

## 1. Czym jest SebsMegaStore

SebsMegaStore to sklep Shopify zbudowany pod rynek UK i walutę GBP. Jego obecna tożsamość nie opiera się na modelu „wrzuć jak najwięcej produktów”, tylko na modelu:

- praktyczne produkty,
- AI-kuracyjny wybór,
- zakupy prowadzone przez intencję klienta,
- nacisk na wartość, użyteczność i prostą nawigację.

Sklep działa w domenie storefrontowej:

- `https://sebsmegastore-2.myshopify.com`

Nazwa sklepu w panelu Shopify:

- `SebsMegaStore`

Potwierdzone parametry sklepu:

- plan: `basic`
- waluta: `GBP`
- kraj: `United Kingdom`
- strefa czasu: `Europe/London`
- e-mail obsługi klienta: `megastoreai@protonmail.com`

## 2. Aktywny storefront

Aktualny aktywny theme Shopify:

- `AI Magnet Theme - Codex 2026-05-09`
- theme ID: `188500181316`
- role: `main`

Theme jest niestandardowym storefrontem skupionym na:

- dziale produktowym,
- szybkim wyszukiwaniu,
- AI Finder,
- sekcji „Checked Deals”,
- czytelnym układzie kategorii,
- krótkim i użytecznym przepływie klienta od intencji do produktu.

## 3. Architektura doświadczenia klienta na storefrontcie

Strona główna korzysta z pięciu głównych sekcji:

- `hero`
- `marketplace-categories`
- `problem-paths`
- `shopping-paths`
- `live-hot-pick`

To daje trzy główne ścieżki wejścia do katalogu:

1. Wejście przez dział.
2. Wejście przez problem do rozwiązania.
3. Wejście przez wyszukiwarkę lub AI Finder.

## 4. Co klient widzi na stronie głównej

### Hero

Hero komunikuje:

- „AI checked UK deals”,
- praktyczne produkty sprawdzone przed publikacją,
- ofertę skupioną na działach: car, tech, tools, camping, home, garden, pet,
- przycisk prowadzący do `Deals Under GBP 30`,
- przycisk prowadzący do `AI Finder`.

Hero dodatkowo pokazuje mini-półkę z produktami z:

- `deals-under-30`,
- fallbackowo `live-hot`,
- ostatecznie całego katalogu.

### Marketplace Categories

Sekcja działów prowadzi bezpośrednio do głównych departmentów:

- `Car & Motoring`
- `Electronics & Tech`
- `Tools & Hardware`
- `Camping & Outdoors`
- `Home & Kitchen`
- `Garden & DIY`
- `Pet Supplies`

Każdy dział ma własne opisy, wejścia podrzędne i kierunki wyszukiwania.

### Problem Paths

Sekcja „Shop by problem” prowadzi klienta nie po taxonomy backendowej, tylko po realnej potrzebie:

- dla zwierzaka,
- na gorące dni,
- do auta,
- do kuchni,
- poniżej `GBP 30`,
- przez AI Finder.

### Shopping Paths

Sekcja „Choose your route” łączy:

- smart search z sugestiami,
- browse by category,
- przejście do AI Finder.

### Checked Deals / Live Pick

Sekcja `live-hot-pick` obraca produkt w rytmie półgodzinnym z kolekcji:

- `live-hot`

Na storefrontcie ta kolekcja jest opisana jako:

- `Checked Deals`

## 5. Header, nawigacja i wyszukiwanie

Header jest mocno funkcjonalny i zorientowany na marketplace UX.

### Utility bar

W utility barze klient dostaje:

- e-mail wsparcia,
- skróty do `Order Help`,
- `Shipping`,
- `Returns`,
- `FAQ`.

### Search bar

Centralny search bar obsługuje:

- wybór działu,
- wpisywanie frazy produktowej,
- szybkie sugestie z `search/suggest.json`,
- przejście do pełnych wyników wyszukiwania.

### Quick actions

Nagłówek ma szybkie akcje do:

- `AI Finder`,
- `Checked Deals`,
- `AI Guide`,
- koszyka.

### Mega menu

Mega menu rozwija główne działy z podpowiedziami typu:

- accessories,
- chargers,
- organizers,
- projectors,
- tool kits,
- repair,
- camping gear,
- kitchen tools,
- plant watering,
- solar utility.

## 6. Główne strony informacyjne sklepu

W Shopify potwierdzone są następujące strony:

- `About Us`
- `AI Personal Shopper: Checked Deals Under GBP 30`
- `AI Shopping Guide`
- `Useful Car Accessories UK`
- `Camping and Outdoor Essentials UK`
- `Useful Deals Under GBP 30 UK`
- `Useful Home and Kitchen Finds UK`
- `Useful Tech Gadgets UK`
- `Contact SebsMegaStore Support`
- `FAQ - SebsMegaStore Customer Support`
- `Order Help & Tracking`
- `Shipping Policy`
- `Returns & Refunds`
- `Privacy Policy`
- `Terms of Service`
- `Refund Policy`
- `Return Policy`
- `Review Submission`

Łącznie sklep ma obecnie:

- `19` stron CMS.

## 7. AI Finder i strony prowadzące do konwersji

AI Finder jest realnym elementem storefrontu, a nie tylko koncepcją w kodzie.

Potwierdzone elementy:

- strona `ai-personal-shopper`,
- linki do niej z hero, headera i sekcji shopping paths,
- dedykowany template `page.ai-personal-shopper.json`,
- sekcja `ai-personal-shopper.liquid`.

AI Finder prowadzi użytkownika do działów:

- `Car & Motoring`
- `Electronics & Tech`
- `Tools & Hardware`
- `Camping Essentials`

W warstwie komunikacji pełni funkcję „AI-guided start page” dla użytkownika, który nie chce przeszukiwać całego katalogu ręcznie.

## 8. Katalog produktów

Potwierdzony stan katalogu:

- wszystkich produktów: `1176`,
- aktywnych produktów w Shopify: `404`,
- produktów opublikowanych do storefrontu web: `376`,
- draftów: `36`,
- archiwalnych: `736`.

Najwięksi aktywni vendorzy w katalogu:

- `SebsMegaStore`: `154`
- `SebsMegaStore AI`: `104`
- `AW Dropship UK`: `63`
- `CJ Dropshipping`: `53`
- `MegaStore`: `14`
- `AliExpress`: `9`
- `AW Dropship`: `5`
- `AliExpress Trend`: `2`

To pokazuje, że katalog jest miksowany pomiędzy produktami markowanymi własną warstwą sklepu i produktami zidentyfikowanymi po dostawcy.

## 9. Główne działy i kolekcje

Potwierdzone główne departmenty storefrontowe:

- `car-motoring`
- `electronics-tech`
- `tools-hardware`
- `camping-outdoors`
- `home-kitchen`
- `garden-diy`
- `pet-supplies`
- `deals-under-30`
- `live-hot`

Potwierdzone wielkości najważniejszych kolekcji:

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

Sklep ma również rozbudowaną warstwę kolekcji wtórnych i kuracyjnych. W Shopify potwierdzone są między innymi:

- `AI Curated 120`
- `AI Product Hits`
- `AI-Curated Camping Gear UK | Practical Outdoor Finds`
- `AI Gift Ideas for UK Homes | Useful Giftable Finds`
- `AW Dropship Curated Practical Picks`
- `CJ Curated Practical Picks`
- `Smart Mini Projectors`
- `High-Margin Picks`
- `Smart Home Finds UK`
- `Garden & Outdoor Finds`
- `Pet Picks`

Łącznie sklep ma:

- `130` custom collections,
- `2` smart collections.

## 10. Jak działa produkt na storefrontcie

Karta produktu i strona produktu są już ustandaryzowane przez theme.

### Product card

Na liście produktów klient dostaje:

- zdjęcie produktu,
- badge `AI Pick`,
- skrócony opis,
- cenę,
- sygnał `checked`,
- badge dostawcy typu `UK supplier` albo `supplier verified`,
- przycisk `Details`,
- quick add do koszyka.

### Product page

Strona produktu zawiera:

- główne zdjęcie i miniatury,
- tytuł,
- lead opisowy,
- cenę i compare-at price jeśli istnieje,
- warianty,
- formularz dodania do koszyka,
- bloki usługowe:
  - shipping shown at checkout,
  - returns help,
  - order support,
- panel wartości:
  - AI-curated fit,
  - price sanity,
  - supplier signal,
- trust strip:
  - AI demand signals,
  - value checked,
  - secure checkout,
  - shipping shown before payment,
- pełny opis produktu,
- JSON danych produktu wykorzystywany także przez tracking i frontend JS.

## 11. Koszyk, wyszukiwanie i checkout

Potwierdzone możliwości storefrontowe w ramach obecnego theme:

- wyszukiwanie po produktach,
- sugestie wyszukiwania w locie przez Shopify suggest endpoint,
- paginacja wyników,
- quick add do koszyka z kart produktowych,
- pełna strona produktu z wyborem wariantu i ilości,
- przejście do checkoutu Shopify,
- w footerze pasek `Secure checkout` z aktywnymi metodami płatności Shopify.

## 12. Zasady merchandisingu, które już działają w systemie

System nie traktuje katalogu jako czystego dumpu. Aktualna warstwa sklepu i backendu wspiera:

- przypisywanie produktów do właściwych kolekcji,
- tagowanie kategorii i subkategorii,
- oznaczanie produktów jako `merchant-audited`,
- oznaczanie produktów jako `seo-reviewed`,
- dodawanie tagów kosztowych i shippingowych,
- oznaczanie produktów dostawcy,
- wyróżnianie produktów promowalnych i AI-curated.

Przykładowe tagi widoczne na realnych aktywnych produktach:

- `cost_gbp:*`
- `shipping_cost_gbp:*`
- `merchant-audited`
- `seo-reviewed`
- `quality-guard-passed`
- `smart-pick`
- `customer-magnet`
- `selected-live:*`
- `category:*`
- `subcategory:*`
- `cj_pid:*`

## 13. Shopify i aktualne kanały / integracje produktowe

### DSers / AliExpress

Repo i dokumentacja potwierdzają aktywny workflow:

- import przez DSers / AliExpress do Shopify,
- dalsza obróbka po stronie Imperium już na produkcie obecnym w Shopify.

To oznacza, że Shopify jest nie tylko storefrontem, ale także centralnym punktem, do którego trafia import zewnętrzny przed kuracją.

### AW Dropship UK

AW jest już widoczne w realnym katalogu sklepu:

- aktywne produkty vendor `AW Dropship UK`,
- kolekcje AW-curated,
- badge `UK supplier` na kartach produktowych dla produktów oznaczonych tagami AW.

### CJ Dropshipping

CJ jest obecne zarówno w warstwie danych, jak i w aktywnym katalogu:

- aktywne produkty vendor `CJ Dropshipping`,
- tagi `cj_pid`,
- sygnały `supplier verified` na kartach produktowych.

## 14. Shopify Admin jako silnik operacyjny systemu

Imperium używa Shopify Admin API do:

- pobierania produktów,
- tworzenia produktów,
- aktualizowania produktów,
- usuwania produktów tam, gdzie polityka systemu to dopuszcza,
- pobierania kolekcji,
- przypisywania do kolekcji,
- pobierania zamówień,
- budowania raportów sprzedażowych,
- pobierania theme i assetów,
- operacji na stronach i warstwie treści.

Dodatkowo repo zawiera skrypty do:

- uploadu assetów theme,
- wdrażania żywego theme,
- dbania o policy pages,
- aktualizacji SEO kolekcji,
- pracy z konfiguracją checkout shipping.

## 15. SEO i warstwa treści

Sklep ma gotową warstwę do pracy z treścią produktową i kolekcyjną.

Potwierdzone moduły:

- `content_generator.py`
- `update_collection_seo.py`
- `shopify_seo_optimizer.py`

Potwierdzone możliwości:

- generowanie SEO title,
- generowanie meta description,
- generowanie HTML description,
- generowanie tagów,
- generowanie słów kluczowych,
- generowanie hashtagów,
- aktualizacja wybranych kolekcji SEO.

## 16. Analityka sprzedaży i wydajności katalogu

System już działa jako warstwa raportująca dla Shopify.

### Orders analytics

Moduł:

- `imperium_engine\modules\shopify_orders_analytics.py`

Potwierdzone funkcje:

- pobieranie zamówień z Shopify,
- liczenie sprzedaży na produkt,
- szacowanie kosztu i zysku,
- raportowanie wyników w `data\orders_analytics.*`.

### Performance tracker

Moduł:

- `imperium_engine\modules\performance_tracker.py`

Potwierdzone funkcje:

- oznaczanie winnerów,
- oznaczanie produktów do review,
- wykrywanie produktów bez wyników w danym oknie analitycznym.

### Profit dashboard

Raport:

- `data\profit_dashboard.md`

Dashboard daje bieżący przegląd:

- liczby aktywnych produktów,
- cen,
- ryzyk,
- sweet spotu cenowego,
- produktów do merchandisig advisory.

## 17. Analityka storefrontu i sygnały zachowania

System ma własną warstwę eventową storefrontu.

Składniki:

- `analytics_collector.py`
- `shopify_storefront_tracker.js`
- `storefront_events.db`
- `storefront_events.jsonl`
- `storefront_analytics.py`

Obsługiwane eventy:

- `page_view`
- `product_view`
- `product_click`
- `image_click`
- `add_to_cart`
- `search`
- `collection_click`

W danych 30-dniowych zapisane są:

- `676` eventów,
- ranking zainteresowania produktami,
- osobny summary wyszukiwań.

## 18. Customer Magnet i warstwa promocyjna

Repo zawiera aktywną warstwę wokół promowania produktów.

Moduły i raporty:

- `customer_magnet_engine.py`
- `organic_asset_pack_generator.py`
- `automation_roi_report.py`
- `automation_competitor_gap_report.py`

Potwierdzone możliwości:

- wybór produktów do promowania,
- tworzenie lub aktualizacja collection/page kampanijnej,
- tagowanie wybranych produktów,
- budowanie paczek copy do Google, social i e-mail,
- liczenie ROI operacyjnego automatyzacji.

Najnowszy command center pokazuje:

- `305` promotable products,
- `112` wygenerowanych social posts.

## 19. Obsługa klienta i warstwa post-purchase

Repo ma także działającą warstwę supportowo-operacyjną:

- `customer_support_kb_generator.py`
- `order_fulfillment_exception_queue.py`

Potwierdzone artefakty:

- `data\customer_support_kb.md`
- `data\FULFILLMENT_EXCEPTION_REPORT.md`

To oznacza, że system nie kończy się na publikacji produktu. Obejmuje też:

- odpowiedzi supportowe,
- klasyfikację dostawcy,
- prywatny handling wyjątków fulfillment,
- raportowanie operacji po zamówieniu.

## 20. Co faktycznie robi Imperium w obrębie Shopify

W obecnej postaci system:

- czyta sklep przez Shopify Admin API,
- utrzymuje własny niestandardowy theme,
- porządkuje kolekcje i działy,
- przypisuje i koryguje tagi produktowe,
- utrzymuje strukturę stron pomocniczych,
- generuje i aktualizuje treść SEO,
- liczy sprzedaż i zysk,
- utrzymuje raporty ryzyka,
- wspiera produkty promowalne,
- zbiera sygnały zachowania klientów,
- utrzymuje AI Finder jako wejście do katalogu.

## 21. Najkrótszy opis sklepu

SebsMegaStore to Shopify storefront z własnym theme i warstwą AI-operacyjną, który działa jak kurator praktycznych produktów dla UK. Shopify jest tu nie tylko witryną sprzedażową, ale główną platformą, na której Imperium:

- zarządza katalogiem,
- ocenia produkt,
- poprawia treść,
- przypisuje merchandising,
- śledzi sprzedaż,
- utrzymuje raporty,
- i buduje promowalny, bardziej uporządkowany sklep.
