"""Medium publishing tool for Hedera content agent."""

from __future__ import annotations

import json
import os
from typing import List

import requests
from crewai.tools import tool


def _get_medium_user_id(token: str) -> str | None:
    """Fetch the authenticated Medium user's ID."""
    url = "https://api.medium.com/v1/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json().get("data", {}).get("id")
    except requests.RequestException as exc:
        print(f"[medium_tools] Failed to fetch user ID: {exc}")
        return None


@tool("Publish to Medium")
def publish_to_medium(
    title: str,
    body: str,
    tags: str = '["hedera", "blockchain", "web3"]',
    publish_status: str = "draft",
) -> str:
    """Publish an article to Medium.

    Args:
        title: Article title.
        body: Article body in Markdown format.
        tags: JSON string list of tags (max 5). Default: '["hedera","blockchain","web3"]'.
        publish_status: 'draft' (default), 'public', or 'unlisted'.
    """
    token = os.getenv("MEDIUM_TOKEN")
    if not token:
        return json.dumps({"error": "MEDIUM_TOKEN not set in environment"})

    user_id = _get_medium_user_id(token)
    if not user_id:
        return json.dumps({"error": "Could not fetch Medium user ID. Check your token."})

    try:
        tag_list: List[str] = json.loads(tags)
    except (json.JSONDecodeError, TypeError):
        tag_list = ["hedera", "blockchain", "web3"]
    tag_list = tag_list[:5]

    url = f"https://api.medium.com/v1/users/{user_id}/posts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {
        "title": title,
        "contentFormat": "markdown",
        "content": body,
        "tags": tag_list,
        "publishStatus": publish_status,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return json.dumps({
            "success": True,
            "url": data.get("url", ""),
            "id": data.get("id", ""),
            "publish_status": data.get("publishStatus", publish_status),
        })
    except requests.RequestException as exc:
        return json.dumps({"error": f"Medium API request failed: {exc}"})
