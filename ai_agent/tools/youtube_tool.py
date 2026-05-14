import requests

YOUTUBE_API_KEY = "YOUR_API_KEY"

def search_youtube_live(query):

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "eventType": "live",
        "maxResults": 5,
        "key": YOUTUBE_API_KEY
    }

    try:
        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        results = []

        for item in data.get("items", []):
            results.append({
                "title": item["snippet"]["title"],
                "content": item["snippet"]["description"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            })

        return results

    except Exception as e:
        print("YouTube error:", e)
        return []