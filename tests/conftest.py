"""Shared test fixtures for HederaAgentContent."""

import json
import pytest


@pytest.fixture
def sample_youtube_response():
    return {
        "items": [
            {
                "id": {"videoId": "abc12345678"},
                "snippet": {
                    "title": "Hedera Town Hall - March 2026",
                    "description": "Monthly update on Hedera ecosystem development.",
                    "publishedAt": "2026-03-15T18:00:00Z",
                },
            },
            {
                "id": {"videoId": "def90123456"},
                "snippet": {
                    "title": "Building with Hedera Token Service",
                    "description": "Deep dive into HTS for developers.",
                    "publishedAt": "2026-03-10T14:00:00Z",
                },
            },
        ]
    }


@pytest.fixture
def sample_twitter_response():
    return {
        "data": [
            {
                "id": "1234567890",
                "text": "Exciting news! Hedera reaches 50B transactions. #Hedera #HBAR",
                "created_at": "2026-03-20T12:00:00Z",
                "public_metrics": {
                    "retweet_count": 150,
                    "like_count": 500,
                },
            },
        ]
    }


@pytest.fixture
def sample_medium_response():
    return {
        "data": {
            "id": "medium-post-123",
            "title": "Hedera Q1 2026 Update",
            "url": "https://medium.com/@hedera/hedera-q1-2026-update",
            "publishStatus": "draft",
        }
    }


@pytest.fixture
def sample_content_plan():
    return {
        "topic": "Hedera Reaches 50 Billion Transactions",
        "angle": "Milestone achievement demonstrates enterprise adoption",
        "key_points": [
            "50B total transactions processed",
            "Lowest carbon footprint of any public DLT",
            "Growing enterprise partnerships",
        ],
        "target_audience": "Web3 developers and Hedera community",
        "sources": [
            "https://twitter.com/Hedera/status/1234567890",
            "https://hedera.com/blog/50b-transactions",
        ],
        "content_types": ["twitter", "medium", "discord"],
    }


@pytest.fixture
def sample_tweet_content():
    return {
        "tweets": [
            "Hedera just hit 50 BILLION transactions! A major milestone for the network. #Hedera #HBAR",
            "What makes this impressive? Enterprise-grade throughput at the lowest carbon footprint of any public DLT.",
            "Learn more about what's next for the Hedera ecosystem. The future of Web3 is being built now. #Web3",
        ],
        "hashtags": ["#Hedera", "#HBAR", "#Web3"],
    }
