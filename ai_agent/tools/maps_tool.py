import requests

def get_place_busy(query):

    try:
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": "YOUR_API_KEY"
        }

        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        results = []

        for place in data.get("results", [])[:5]:
            results.append({
                "title": place.get("name"),
                "content": f"rating:{place.get('rating')} user_ratings:{place.get('user_ratings_total')}",
                "url": "https://maps.google.com/?q=" + place.get("name")
            })

        return results

    except Exception as e:
        print("Maps error:", e)
        return []