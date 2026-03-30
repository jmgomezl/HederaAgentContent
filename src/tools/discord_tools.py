"""Discord webhook tool for Hedera content agent."""

from __future__ import annotations

import json
import os

import requests
from crewai.tools import tool


@tool("Post to Discord")
def post_to_discord(
    title: str,
    description: str,
    url: str = "",
    color: int = 0x8259EF,
) -> str:
    """Post a rich embed message to a Discord channel via webhook.

    Args:
        title: Embed title.
        description: Main message content (max 4096 chars).
        url: Optional URL to link in the embed.
        color: Embed sidebar color as integer (default: Hedera purple 0x8259EF).
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return json.dumps({"error": "DISCORD_WEBHOOK_URL not set in environment"})

    if len(description) > 4096:
        description = description[:4093] + "..."

    embed = {
        "title": title,
        "description": description,
        "color": color,
    }
    if url:
        embed["url"] = url

    embed["footer"] = {"text": "Hedera Content Agent"}

    payload = {"embeds": [embed]}

    try:
        resp = requests.post(webhook_url, json=payload, timeout=15)
        resp.raise_for_status()
        return json.dumps({
            "success": True,
            "status_code": resp.status_code,
            "message": "Discord message posted successfully",
        })
    except requests.RequestException as exc:
        return json.dumps({"error": f"Discord webhook failed: {exc}"})
