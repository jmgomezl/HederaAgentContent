"""Tests for tool functions (mocked API calls)."""

import json
from unittest.mock import patch, MagicMock

import pytest

from src.tools.youtube_tools import search_hedera_youtube, fetch_video_transcript, _extract_video_id
from src.tools.twitter_tools import search_hedera_tweets, post_tweet
from src.tools.medium_tools import publish_to_medium
from src.tools.discord_tools import post_to_discord
from src.tools.web_scraper_tools import scrape_hedera_blog


# ---------------------------------------------------------------------------
# YouTube Tools
# ---------------------------------------------------------------------------

class TestExtractVideoId:
    def test_raw_id(self):
        assert _extract_video_id("abc12345678") == "abc12345678"

    def test_watch_url(self):
        assert _extract_video_id("https://www.youtube.com/watch?v=abc12345678") == "abc12345678"

    def test_short_url(self):
        assert _extract_video_id("https://youtu.be/abc12345678") == "abc12345678"

    def test_live_url(self):
        assert _extract_video_id("https://youtube.com/live/abc12345678") == "abc12345678"

    def test_invalid(self):
        assert _extract_video_id("not-a-url") is None

    def test_empty(self):
        assert _extract_video_id("") is None


class TestSearchHederaYoutube:
    @patch("src.tools.youtube_tools.requests.get")
    @patch.dict("os.environ", {"YOUTUBE_API_KEY": "test-key"})
    def test_success(self, mock_get, sample_youtube_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_youtube_response
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = json.loads(search_hedera_youtube.run("Hedera"))
        assert result["count"] == 2
        assert result["videos"][0]["title"] == "Hedera Town Hall - March 2026"

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_api_key(self):
        result = json.loads(search_hedera_youtube.run("Hedera"))
        assert "error" in result


class TestFetchVideoTranscript:
    @patch("src.tools.youtube_tools.YouTubeTranscriptApi")
    def test_success(self, mock_api_cls):
        mock_entry_1 = MagicMock()
        mock_entry_1.text = "Hello everyone"
        mock_entry_2 = MagicMock()
        mock_entry_2.text = "Welcome to Hedera"
        mock_entry_3 = MagicMock()
        mock_entry_3.text = "[Music]"

        mock_instance = MagicMock()
        mock_instance.fetch.return_value = [mock_entry_1, mock_entry_2, mock_entry_3]
        mock_api_cls.return_value = mock_instance

        result = json.loads(fetch_video_transcript.run("abc12345678"))
        assert "transcript" in result
        assert "Hello" in result["transcript"]
        assert "[Music]" not in result["transcript"]

    def test_invalid_url(self):
        result = json.loads(fetch_video_transcript.run("invalid"))
        assert "error" in result


# ---------------------------------------------------------------------------
# Twitter Tools
# ---------------------------------------------------------------------------

class TestSearchHederaTweets:
    @patch("src.tools.twitter_tools.requests.get")
    @patch.dict("os.environ", {"TWITTER_BEARER_TOKEN": "test-bearer"})
    def test_success(self, mock_get, sample_twitter_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_twitter_response
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = json.loads(search_hedera_tweets.run("from:Hedera"))
        assert result["count"] == 1
        assert "50B" in result["tweets"][0]["text"]

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_bearer(self):
        result = json.loads(search_hedera_tweets.run("from:Hedera"))
        assert "error" in result


class TestPostTweet:
    @patch("src.tools.twitter_tools.requests.post")
    @patch("src.tools.twitter_tools._oauth1_session")
    @patch.dict("os.environ", {
        "TWITTER_API_KEY": "k",
        "TWITTER_API_SECRET": "s",
        "TWITTER_ACCESS_TOKEN": "t",
        "TWITTER_ACCESS_SECRET": "as",
    })
    def test_success(self, mock_oauth, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": {"id": "999"}}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp
        mock_oauth.return_value = MagicMock()

        result = json.loads(post_tweet.run('["Hello Hedera!"]'))
        assert result["count"] == 1
        assert result["posted"][0]["tweet_id"] == "999"


# ---------------------------------------------------------------------------
# Medium Tools
# ---------------------------------------------------------------------------

class TestPublishToMedium:
    @patch("src.tools.medium_tools.requests.post")
    @patch("src.tools.medium_tools._get_medium_user_id", return_value="user-123")
    @patch.dict("os.environ", {"MEDIUM_TOKEN": "test-token"})
    def test_success(self, mock_user_id, mock_post, sample_medium_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = sample_medium_response
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        result = json.loads(publish_to_medium.run(
            title="Test Article",
            body="## Hello\n\nWorld",
        ))
        assert result["success"] is True
        assert "medium.com" in result["url"]

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_token(self):
        result = json.loads(publish_to_medium.run(title="Test", body="Body"))
        assert "error" in result


# ---------------------------------------------------------------------------
# Discord Tools
# ---------------------------------------------------------------------------

class TestPostToDiscord:
    @patch("src.tools.discord_tools.requests.post")
    @patch.dict("os.environ", {"DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/test"})
    def test_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        result = json.loads(post_to_discord.run(
            title="Test Announcement",
            description="Hello Hedera community!",
        ))
        assert result["success"] is True

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_webhook(self):
        result = json.loads(post_to_discord.run(title="Test", description="Body"))
        assert "error" in result


# ---------------------------------------------------------------------------
# Web Scraper Tools
# ---------------------------------------------------------------------------

class TestScrapeHederaBlog:
    @patch("src.tools.web_scraper_tools.requests.get")
    def test_success(self, mock_get):
        html = """
        <html><body>
            <article>
                <h2><a href="/blog/hedera-update">Hedera Q1 Update</a></h2>
                <p>Latest developments in the Hedera ecosystem.</p>
                <time datetime="2026-03-01">March 1, 2026</time>
            </article>
            <article>
                <h3><a href="/blog/hts-guide">HTS Developer Guide</a></h3>
                <p>Complete guide to Hedera Token Service.</p>
            </article>
        </body></html>
        """
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = json.loads(scrape_hedera_blog.run())
        assert result["count"] >= 1
        assert "Hedera" in result["articles"][0]["title"]
