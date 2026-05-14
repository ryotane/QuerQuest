from ai_agent.tools.scraper import scrape_url
from ai_agent.tools.db import save_document


def research_url(url: str):
    text = scrape_url(url)
    save_document(text, url)
    return {"status": "saved", "url": url}