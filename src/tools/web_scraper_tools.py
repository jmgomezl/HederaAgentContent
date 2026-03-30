"""Web scraping tools for Hedera official sources."""

from __future__ import annotations

import json

import requests
from bs4 import BeautifulSoup
from crewai.tools import tool


HEDERA_BLOG_URL = "https://hedera.com/blog"
HEDERA_LEARNING_URL = "https://hedera.com/learning"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


@tool("Scrape Hedera Blog")
def scrape_hedera_blog(max_articles: int = 5) -> str:
    """Scrape recent articles from the official Hedera blog at hedera.com/blog.

    Args:
        max_articles: Number of articles to fetch (1-10, default: 5).
    """
    max_articles = min(max(1, max_articles), 10)

    try:
        resp = requests.get(HEDERA_BLOG_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return json.dumps({"error": f"Failed to fetch Hedera blog: {exc}"})

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []

    # Try common blog card patterns
    cards = (
        soup.select("article")
        or soup.select("[class*='blog-card']")
        or soup.select("[class*='post-card']")
        or soup.select("a[href*='/blog/']")
    )

    for card in cards[:max_articles]:
        title_el = card.find(["h2", "h3", "h4"]) or card
        title = title_el.get_text(strip=True) if title_el else ""

        link_el = card.find("a", href=True) if card.name != "a" else card
        href = link_el["href"] if link_el else ""
        if href and not href.startswith("http"):
            href = f"https://hedera.com{href}"

        summary_el = card.find("p")
        summary = summary_el.get_text(strip=True)[:300] if summary_el else ""

        time_el = card.find("time")
        published = time_el.get("datetime", time_el.get_text(strip=True)) if time_el else ""

        if title:
            articles.append({
                "title": title,
                "url": href,
                "summary": summary,
                "published_at": published,
            })

    # If structured parsing failed, try simpler link extraction
    if not articles:
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/blog/" in href and href != "/blog/":
                text = link.get_text(strip=True)
                if text and len(text) > 10:
                    if not href.startswith("http"):
                        href = f"https://hedera.com{href}"
                    articles.append({
                        "title": text[:200],
                        "url": href,
                        "summary": "",
                        "published_at": "",
                    })
                    if len(articles) >= max_articles:
                        break

    return json.dumps({"articles": articles, "count": len(articles)})
