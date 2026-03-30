"""YouTube research tools for Hedera content agent."""

from __future__ import annotations

import json
import os
import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests
from crewai.tools import tool
from youtube_transcript_api import YouTubeTranscriptApi


HEDERA_CHANNEL_ID = os.getenv("HEDERA_YOUTUBE_CHANNEL_ID", "UCIhE4NYpaX9E6SZQFq6JE")
VIDEO_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")


def _extract_video_id(url: str) -> Optional[str]:
    """Extract a YouTube video ID from a URL or raw ID string."""
    candidate = url.strip()
    if VIDEO_ID_RE.match(candidate):
        return candidate
    try:
        parsed = urlparse(candidate)
        host = (parsed.hostname or "").lower().replace("www.", "")
        if host == "youtu.be":
            return parsed.path.lstrip("/")[:11]
        if host in ("youtube.com", "m.youtube.com"):
            if parsed.path.startswith(("/watch", "/live", "/embed", "/shorts")):
                qs = parse_qs(parsed.query)
                if "v" in qs:
                    return qs["v"][0]
                parts = parsed.path.split("/")
                if len(parts) >= 3:
                    return parts[2][:11]
    except (ValueError, AttributeError, KeyError):
        pass
    return None


@tool("Search Hedera YouTube Channel")
def search_hedera_youtube(query: str = "Hedera", max_results: int = 5) -> str:
    """Search the official Hedera YouTube channel for recent videos.

    Args:
        query: Search keywords (default: 'Hedera').
        max_results: Number of results to return (1-10, default: 5).
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return json.dumps({"error": "YOUTUBE_API_KEY not set in environment"})

    max_results = min(max(1, max_results), 10)
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": api_key,
        "channelId": HEDERA_CHANNEL_ID,
        "q": query,
        "part": "snippet",
        "type": "video",
        "order": "date",
        "maxResults": max_results,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        return json.dumps({"error": f"YouTube API request failed: {exc}"})

    videos = []
    for item in data.get("items", []):
        vid_id = item["id"].get("videoId", "")
        snippet = item.get("snippet", {})
        videos.append({
            "video_id": vid_id,
            "title": snippet.get("title", ""),
            "description": snippet.get("description", "")[:300],
            "published_at": snippet.get("publishedAt", ""),
            "url": f"https://www.youtube.com/watch?v={vid_id}",
        })

    return json.dumps({"videos": videos, "count": len(videos)})


@tool("Fetch YouTube Video Transcript")
def fetch_video_transcript(video_url: str) -> str:
    """Fetch the English transcript of a YouTube video.

    Args:
        video_url: A YouTube URL or video ID.
    """
    video_id = _extract_video_id(video_url)
    if not video_id:
        return json.dumps({"error": f"Could not extract video ID from: {video_url}"})

    try:
        # youtube-transcript-api v1.x uses .fetch() and .list()
        ytt = YouTubeTranscriptApi()
        transcript_entries = ytt.fetch(video_id, languages=["en"])

        lines = []
        for entry in transcript_entries:
            text = entry.text if hasattr(entry, "text") else str(entry)
            text = text.strip()
            if text.lower() in ("[music]", "[applause]", ""):
                continue
            lines.append(text)

        full_text = " ".join(lines)
        if len(full_text) > 15000:
            full_text = full_text[:15000] + "... [truncated]"

        return json.dumps({
            "video_id": video_id,
            "transcript": full_text,
            "word_count": len(full_text.split()),
        })

    except Exception as exc:
        return json.dumps({"error": f"Transcript fetch failed: {exc}"})
