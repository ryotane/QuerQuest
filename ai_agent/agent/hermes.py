from ai_agent.tools.scraper import scrape_url
from ai_agent.tools.db import search
from ai_agent.tools.pdf_loader import load_pdf

import requests
import re
import urllib.parse

LM_API = "http://localhost:1234/v1/chat/completions"


def ask_llm(prompt: str):
    try:
        res = requests.post(LM_API, json={
            "model": "local-model",
            "messages": [{"role": "user", "content": prompt}]
        })
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM_ERROR: {e}"


def route_query(question: str):
    q = question.lower()

    if re.search(r"https?://", q):
        return "web"

    if q.endswith(".pdf") or "pdf" in q:
        return "pdf"

    if any(w in q for w in ["調べて", "検索", "ニュース", "とは"]):
        return "search"

    return "rag"


def search_web(query):
    url = f"http://localhost:8080/search?q={urllib.parse.quote(query)}&format=json"
    res = requests.get(url)
    return res.json()


def run(question: str):
    mode = route_query(question)

    context = ""

    if mode == "web":
        if not question.startswith("http"):
            return "URLではありません"
        text = scrape_url(question)
        context = text[:3000]

    elif mode == "pdf":
        context = load_pdf(question)

    elif mode == "search":
        results = search_web(question)
        context = str(results)[:3000]

    else:
        results = search(question)
        docs = results.get("documents", [[]])
        context = "\n".join(docs[0]) if docs and docs[0] else ""

    prompt = f"""
あなたはリサーチAIです。

以下の情報を統合して回答してください：

{context}

質問：
{question}
"""

    return ask_llm(prompt)