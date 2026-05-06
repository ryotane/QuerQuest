import requests
from bs4 import BeautifulSoup

def search_twitter(query):

    url = f"https://search.yahoo.co.jp/realtime/search?p={query}"

    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        tweets = []

        for item in soup.select("div")[:10]:
            text = item.get_text(strip=True)

            if len(text) > 20:
                tweets.append({
                    "title": "Twitter",
                    "content": text,
                    "url": url
                })

        return tweets[:5]

    except Exception as e:
        print("Twitter error:", e)
        return []