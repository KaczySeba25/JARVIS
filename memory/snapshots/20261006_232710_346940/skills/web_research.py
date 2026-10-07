import requests
from bs4 import BeautifulSoup

def run(query: str):
    """Wyszukuje informacje w sieci i streszcza zawartość strony."""
    try:
        # Proste wyszukiwanie przez DuckDuckGo (darmowe, bez klucza API)
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for link in soup.find_all('a', class_='result__a'):
            results.append(link.get('href'))
            
        if not results:
            return "Nie znalazłem konkretnych linków, ale polecam sprawdzić trendy na ProductHunt lub IndieHackers."
            
        return f"Znalazłem potencjalne źródła dla Twojego SaaS/MVP: {results[:5]}"
    except Exception as e:
        return f"Błąd researchu: {str(e)}"
