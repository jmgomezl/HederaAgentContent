"""Pydantic models for structured agent outputs."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Research models
# ---------------------------------------------------------------------------

class VideoInfo(BaseModel):
    """Metadata about a single YouTube video."""
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    description: str = Field(default="", description="Video description snippet")
    published_at: str = Field(default="", description="ISO-8601 publish date")
    url: str = Field(default="", description="Full YouTube URL")


class TweetInfo(BaseModel):
    """Metadata about a single tweet."""
    tweet_id: str = Field(..., description="Tweet ID")
    text: str = Field(..., description="Tweet text")
    created_at: str = Field(default="", description="ISO-8601 creation date")
    metrics: Optional[dict] = Field(default=None, description="Engagement metrics")


class WebArticle(BaseModel):
    """Scraped article from Hedera blog or docs."""
    title: str = Field(..., description="Article title")
    url: str = Field(..., description="Article URL")
    summary: str = Field(default="", description="Brief summary or first paragraph")
    published_at: str = Field(default="", description="Publication date if available")


class ResearchResult(BaseModel):
    """Aggregated research from all sources."""
    youtube_videos: List[VideoInfo] = Field(default_factory=list)
    youtube_transcripts: List[str] = Field(default_factory=list, description="Transcript summaries")
    tweets: List[TweetInfo] = Field(default_factory=list)
    web_articles: List[WebArticle] = Field(default_factory=list)
    key_topics: List[str] = Field(default_factory=list, description="Main topics identified")
    summary: str = Field(default="", description="Overall research summary")


# ---------------------------------------------------------------------------
# Content planning models
# ---------------------------------------------------------------------------

class ContentPlan(BaseModel):
    """Strategic plan for a content piece."""
    topic: str = Field(..., description="Main topic / headline idea")
    angle: str = Field(..., description="Unique angle or perspective")
    key_points: List[str] = Field(default_factory=list, description="3-5 key points to cover")
    target_audience: str = Field(default="Web3 developers and Hedera community members")
    sources: List[str] = Field(default_factory=list, description="Source URLs used")
    content_types: List[str] = Field(
        default_factory=lambda: ["twitter", "medium", "discord"],
        description="Platforms to publish on",
    )
    language: str = Field(default="en", description="Target language code (en or es)")


# ---------------------------------------------------------------------------
# Content output models
# ---------------------------------------------------------------------------

class TwitterContent(BaseModel):
    """Ready-to-publish Twitter/X content."""
    tweets: List[str] = Field(
        ...,
        description="List of tweets forming a thread (each max 280 chars)",
    )
    hashtags: List[str] = Field(default_factory=list, description="Suggested hashtags")
    language: str = Field(default="en", description="Content language code (en or es)")


class MediumArticle(BaseModel):
    """Ready-to-publish Medium article."""
    title: str = Field(..., description="Article title")
    subtitle: str = Field(default="", description="Optional subtitle")
    body: str = Field(..., description="Full article body in Markdown")
    tags: List[str] = Field(
        default_factory=lambda: ["hedera", "blockchain", "web3"],
        description="Medium tags (max 5)",
    )
    language: str = Field(default="en", description="Content language code (en or es)")


class DiscordMessage(BaseModel):
    """Ready-to-publish Discord message."""
    title: str = Field(..., description="Embed title")
    description: str = Field(..., description="Main message content (max 4096 chars)")
    url: Optional[str] = Field(default=None, description="Optional link")
    color: int = Field(default=0x8259EF, description="Embed color (Hedera purple)")
    fields: List[dict] = Field(
        default_factory=list,
        description="Embed fields [{name, value, inline}]",
    )


# ---------------------------------------------------------------------------
# Publishing result
# ---------------------------------------------------------------------------

class PlatformResult(BaseModel):
    """Result of publishing to a single platform."""
    platform: str = Field(..., description="twitter | medium | discord")
    success: bool = Field(default=False)
    url: Optional[str] = Field(default=None, description="Published content URL")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class PublishResult(BaseModel):
    """Aggregated results across all platforms."""
    results: List[PlatformResult] = Field(default_factory=list)
    summary: str = Field(default="", description="Human-readable summary")
