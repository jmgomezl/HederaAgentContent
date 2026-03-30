"""X/Twitter tools for Hedera content agent."""

from __future__ import annotations

import json
import os
from typing import List

import requests
from crewai.tools import tool


HEDERA_TWITTER_USERNAME = "Hedera"


def _bearer_headers() -> dict:
    """Build Authorization header for Twitter API v2 Bearer token auth."""
    token = os.getenv("TWITTER_BEARER_TOKEN", "")
    return {"Authorization": f"Bearer {token}"}


def _oauth1_session():
    """Build a requests-oauthlib OAuth1Session for write operations."""
    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        raise ImportError("pip install requests-oauthlib for Twitter posting")

    return OAuth1(
        os.getenv("TWITTER_API_KEY", ""),
        os.getenv("TWITTER_API_SECRET", ""),
        os.getenv("TWITTER_ACCESS_TOKEN", ""),
        os.getenv("TWITTER_ACCESS_SECRET", ""),
    )


@tool("Search Hedera Tweets")
def search_hedera_tweets(query: str = "from:Hedera", max_results: int = 10) -> str:
    """Search recent tweets from or about Hedera on X/Twitter.

    Args:
        query: Twitter search query (default: 'from:Hedera').
        max_results: Number of tweets to return (10-100, default: 10).
    """
    bearer = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer:
        return json.dumps({"error": "TWITTER_BEARER_TOKEN not set in environment"})

    max_results = min(max(10, max_results), 100)
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics,author_id",
    }

    try:
        resp = requests.get(url, headers=_bearer_headers(), params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"Twitter API request failed: {exc}"})

    tweets = []
    for t in data.get("data", []):
        tweets.append({
            "tweet_id": t.get("id", ""),
            "text": t.get("text", ""),
            "created_at": t.get("created_at", ""),
            "metrics": t.get("public_metrics"),
        })

    return json.dumps({"tweets": tweets, "count": len(tweets)})


@tool("Post Tweet")
def post_tweet(tweets: str) -> str:
    """Post a tweet or tweet thread to X/Twitter.

    Args:
        tweets: JSON string of a list of tweet texts to post as a thread.
               Example: '["First tweet", "Second tweet in thread"]'
    """
    required = ["TWITTER_API_KEY", "TWITTER_API_SECRET",
                 "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_SECRET"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        return json.dumps({"error": f"Missing env vars: {', '.join(missing)}"})

    try:
        tweet_list: List[str] = json.loads(tweets)
    except (json.JSONDecodeError, TypeError):
        tweet_list = [str(tweets)]

    auth = _oauth1_session()
    url = "https://api.twitter.com/2/tweets"
    posted = []
    reply_to = None

    for text in tweet_list:
        if len(text) > 280:
            text = text[:277] + "..."

        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}

        try:
            resp = requests.post(url, json=payload, auth=auth, timeout=15)
            resp.raise_for_status()
            result = resp.json()
            tweet_id = result.get("data", {}).get("id", "")
            reply_to = tweet_id
            posted.append({
                "tweet_id": tweet_id,
                "text": text,
                "url": f"https://twitter.com/i/status/{tweet_id}",
            })
        except requests.RequestException as exc:
            posted.append({"text": text, "error": str(exc)})
            break

    return json.dumps({"posted": posted, "count": len(posted)})
