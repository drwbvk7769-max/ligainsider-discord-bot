import os, requests
from bs4 import BeautifulSoup

URL = "https://www.ligainsider.de/"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "last_link.txt"

def get_all_recent_news():
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Holt alle News-Links von der Startseite
        news_items = soup.select('a[href*="/news/"]') or soup.select('a[href*="/"]')
        
        articles = []
        seen_urls = set()
        
        for item in news_items:
            link, title = item.get('href'), item.text.strip()
            if link and len(title) > 10 and not link.startswith('#'):
                full_url = "https://www.ligainsider.de" + link if not link.startswith('http') else link
                # Keine Duplikate auf der Seite doppelt erfassen
                if full_url not in seen_urls:
                    seen_urls.add(full_url)
                    articles.append({"title": title, "url": full_url})
        return articles
    except:
        return []

def main():
    if not WEBHOOK_URL: return
    
    articles = get_all_recent_news()
    if not articles: return
    
    # Lade den zuletzt gesendeten Link
    last_link = open(STATE_FILE, "r").read().strip() if os.path.exists(STATE_FILE) else ""
    
    # Sammle ALLE Artikel, die neuer sind als der zuletzt gespeicherte Link
    new_articles = []
    for article in articles:
        if article["url"] == last_link:
            break  # Stopper: Wir sind beim letzten bekannten Artikel angekommen!
        new_articles.append(article)
        
    # Wenn der Bot das allererste Mal läuft, schickt er nur die aktuellste Meldung
    if not last_link and new_articles:
        new_articles = [new_articles[0]]
        
    # Sende alle neuen Artikel chronologisch (von alt nach neu) an Discord
    for article in reversed(new_articles):
        payload = {
            "content": f"🚨 **NEUE MELDUNG** 🚨\n**{article['title']}**\n{article['url']}",
            "username": "LigaInsider Bot"
        }
        requests.post(WEBHOOK_URL, json=payload)
        
    # Speichere den absolut neuesten Link für den nächsten Durchlauf
    if new_articles:
        open(STATE_FILE, "w").write(new_articles[0]["url"])

if __name__ == "__main__":
    main()

