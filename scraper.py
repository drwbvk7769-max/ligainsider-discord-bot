import os, requests, time
from bs4 import BeautifulSoup

URL = "https://www.ligainsider.de/"
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK")
STATE_FILE = "last_link.txt"

def get_latest_news():
    headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select('a[href*="/news/"]') or soup.select('a[href*="/"]')
        for item in news_items:
            link, title = item.get('href'), item.text.strip()
            if link and len(title) > 10 and not link.startswith('#'):
                return {"title": title, "url": "https://www.ligainsider.de" + link if not link.startswith('http') else link}
    except: pass
    return None

def main():
    if not WEBHOOK_URL: return
    latest = get_latest_news()
    if not latest: return
    
    last_link = open(STATE_FILE, "r").read().strip() if os.path.exists(STATE_FILE) else ""
    
    if latest["url"] != last_link:
        payload = {"content": f"🚨 **NEUE MELDUNG** 🚨\n**{latest['title']}**\n{latest['url']}", "username": "LigaInsider Bot"}
        if requests.post(WEBHOOK_URL, json=payload).status_code == 204:
            open(STATE_FILE, "w").write(latest["url"])

if __name__ == "__main__":
    main()
