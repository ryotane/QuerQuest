from scrapling.fetchers import Fetcher
from bs4 import BeautifulSoup


def scrape_url(url: str) -> str:
    f = Fetcher()
    res = f.get(url, timeout=15)

    soup = BeautifulSoup(res.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    return "\n".join(lines[:3000])