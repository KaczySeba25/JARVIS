import requests
from bs4 import BeautifulSoup
import urllib.parse

def run(query: str):
    """Zaawansowany research: przeszukuje sieÄ‡ i wyciÄ…ga treÅ›ci."""
    if not query or len(query.strip()) < 3:
        return "BÅÄ„D: Podaj konkretne zapytanie do researchu."
    try:
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_='result__a')]
        if not links: return "Nie znaleziono linkÃ³w."
        first_link = links[0]
        page_res = requests.get(first_link, headers=headers, timeout=10)
        page_soup = BeautifulSoup(page_res.text, 'html.parser')
        paragraphs = page_soup.find_all('p')
        text_content = "\n".join([p.get_text() for p in paragraphs[:5]])
        return f"Å¹RÃ“DÅO: {first_link}\n\nTREÅšÄ†:\n{text_content[:2000]}..."
    except Exception as e:
        return f"BÅ‚Ä…d researchu: {str(e)}"
