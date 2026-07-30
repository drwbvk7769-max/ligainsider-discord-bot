   import os, requests, re
from bs4 import BeautifulSoup

URL = "https://www.ligainsider.de/"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "last_link.txt"

def get_all_recent_news():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Der smarte Filter: Wir suchen NUR nach Links, die mit einer Nummer enden!
        # Das blockiert alle Sidebar-Links wie "Torschützenkönig"
        news_links = soup.find_all('a', href=re.compile(r'/news/.*-\d+/?$'))
        
        articles = []
        seen_urls = set()
        
        for item in news_links:
            link = item.get('href')
            # Text aus dem Link holen
            title = item.get('title') or item.get_text(strip=True)
            
            # Bilder-Links (ohne Text) und zu kurze Texte ignorieren wir
            if not title or len(title) < 10:
                continue
                
            full_url = "https://www.ligainsider.de" + link if not link.startswith('http') else link
            
            if full_url not in seen_urls:
                seen_urls.add(full_url)
                articles.append({"title": title, "url": full_url})
                
        # Wir übergeben nur die obersten 5 echten Artikel zur Kontrolle
        return articles[:5]
    except Exception as e:
        print("Fehler:", e)
        return []

def main():
    if not WEBHOOK_URL: return
    
    articles = get_all_recent_news()
    if not articles: return
    
    last_link = open(STATE_FILE, "r").read().strip() if os.path.exists(STATE_FILE) else ""
    
    new_articles = []
    for article in articles:
        if article["url"] == last_link:
            break
        new_articles.append(article)
        
    # Beim ersten Start nach dem Update nur die EINE absolut neuste Meldung schicken
    if not last_link and new_articles:
        new_articles = [new_articles[0]]
        
    for article in reversed(new_articles):
        payload = {
            "content": f"🚨 **NEUE MELDUNG** 🚨\n**{article['title']}**\n{article['url']}",
            "username": "LigaInsider Bot"
        }
        requests.post(WEBHOOK_URL, json=payload)
        
    if new_articles:
        open(STATE_FILE, "w").write(new_articles[-1]["url"])

if __name__ == "__main__":
    main()
