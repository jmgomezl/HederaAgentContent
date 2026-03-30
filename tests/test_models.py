"""Tests for Pydantic models."""

import pytest
from src.models import (
    VideoInfo,
    TweetInfo,
    WebArticle,
    ResearchResult,
    ContentPlan,
    TwitterContent,
    MediumArticle,
    DiscordMessage,
    PlatformResult,
    PublishResult,
)


class TestVideoInfo:
    def test_create_with_required_fields(self):
        v = VideoInfo(video_id="abc12345678", title="Test Video")
        assert v.video_id == "abc12345678"
        assert v.title == "Test Video"
        assert v.description == ""

    def test_create_with_all_fields(self):
        v = VideoInfo(
            video_id="abc12345678",
            title="Test",
            description="A test video",
            published_at="2026-03-15T18:00:00Z",
            url="https://youtube.com/watch?v=abc12345678",
        )
        assert v.url.startswith("https://")


class TestTweetInfo:
    def test_create(self):
        t = TweetInfo(tweet_id="123", text="Hello #Hedera")
        assert t.tweet_id == "123"
        assert t.metrics is None

    def test_with_metrics(self):
        t = TweetInfo(
            tweet_id="123",
            text="Hello",
            metrics={"retweet_count": 10, "like_count": 50},
        )
        assert t.metrics["like_count"] == 50


class TestWebArticle:
    def test_create(self):
        a = WebArticle(title="Hedera Update", url="https://hedera.com/blog/update")
        assert a.title == "Hedera Update"
        assert a.summary == ""


class TestResearchResult:
    def test_empty_defaults(self):
        r = ResearchResult()
        assert r.youtube_videos == []
        assert r.tweets == []
        assert r.key_topics == []
        assert r.summary == ""

    def test_with_data(self):
        r = ResearchResult(
            youtube_videos=[VideoInfo(video_id="abc", title="Test")],
            key_topics=["DeFi", "Token Service"],
            summary="Latest Hedera developments",
        )
        assert len(r.youtube_videos) == 1
        assert len(r.key_topics) == 2


class TestContentPlan:
    def test_create(self):
        p = ContentPlan(
            topic="Hedera 50B Transactions",
            angle="Enterprise adoption milestone",
            key_points=["50B txns", "Low carbon", "Growing ecosystem"],
        )
        assert len(p.key_points) == 3
        assert p.target_audience.startswith("Web3")
        assert "twitter" in p.content_types
        assert p.language == "en"

    def test_spanish_language(self):
        p = ContentPlan(
            topic="Hedera alcanza 50 mil millones de transacciones",
            angle="Hito de adopcion empresarial",
            key_points=["50B txns", "Baja huella de carbono"],
            language="es",
        )
        assert p.language == "es"


class TestTwitterContent:
    def test_create(self):
        tc = TwitterContent(
            tweets=["First tweet", "Second tweet"],
            hashtags=["#Hedera"],
        )
        assert len(tc.tweets) == 2
        assert tc.language == "en"

    def test_tweet_length_validation(self):
        tc = TwitterContent(tweets=["A" * 280])
        assert len(tc.tweets[0]) == 280

    def test_spanish_tweets(self):
        tc = TwitterContent(
            tweets=["Hedera alcanza un hito increible!", "Mas detalles pronto."],
            hashtags=["#Hedera", "#HBAR"],
            language="es",
        )
        assert tc.language == "es"
        assert len(tc.tweets) == 2


class TestMediumArticle:
    def test_create(self):
        a = MediumArticle(
            title="Hedera Update",
            body="## Introduction\n\nContent here.",
            tags=["hedera", "blockchain"],
        )
        assert a.subtitle == ""
        assert "##" in a.body

    def test_default_tags(self):
        a = MediumArticle(title="Test", body="Body")
        assert "hedera" in a.tags
        assert a.language == "en"

    def test_spanish_article(self):
        a = MediumArticle(
            title="Actualizacion de Hedera Q1 2026",
            body="## Introduccion\n\nContenido aqui.",
            language="es",
        )
        assert a.language == "es"


class TestDiscordMessage:
    def test_create(self):
        d = DiscordMessage(
            title="Announcement",
            description="Big news from Hedera!",
        )
        assert d.color == 0x8259EF  # Hedera purple
        assert d.url is None
        assert d.fields == []


class TestPublishResult:
    def test_create(self):
        pr = PublishResult(
            results=[
                PlatformResult(platform="twitter", success=True, url="https://twitter.com/..."),
                PlatformResult(platform="medium", success=True, url="https://medium.com/..."),
                PlatformResult(platform="discord", success=False, error="Webhook failed"),
            ],
            summary="2/3 platforms published successfully",
        )
        assert len(pr.results) == 3
        assert pr.results[2].success is False
