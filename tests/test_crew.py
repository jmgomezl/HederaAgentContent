"""Integration tests for crew orchestration (mocked LLM and tools)."""

import pytest
from unittest.mock import patch, MagicMock

from src.crew import ResearchCrew, WritingCrew, PublishingCrew


class TestResearchCrew:
    def test_agents_are_created(self):
        """Verify all research agents can be instantiated."""
        crew = ResearchCrew()
        agents = [
            crew.youtube_researcher(),
            crew.twitter_researcher(),
            crew.web_researcher(),
            crew.content_strategist(),
        ]
        assert len(agents) == 4
        for agent in agents:
            assert agent.role is not None
            assert agent.goal is not None

    def test_tasks_are_created(self):
        """Verify all research tasks can be instantiated."""
        crew = ResearchCrew()
        tasks = [
            crew.youtube_research_task(),
            crew.twitter_research_task(),
            crew.web_research_task(),
            crew.content_strategy_task(),
        ]
        assert len(tasks) == 4
        for task in tasks:
            assert task.description is not None

    def test_crew_is_sequential(self):
        """Verify the research crew uses sequential process."""
        crew_instance = ResearchCrew().crew()
        assert str(crew_instance.process) == "Process.sequential"


class TestWritingCrew:
    def test_agents_are_created(self):
        crew = WritingCrew()
        writer = crew.content_writer()
        assert writer.role is not None
        assert writer.tools == []

    def test_tasks_are_created(self):
        crew = WritingCrew()
        tasks = [
            crew.twitter_writing_task(),
            crew.medium_writing_task(),
            crew.discord_writing_task(),
        ]
        assert len(tasks) == 3

    def test_crew_is_sequential(self):
        crew_instance = WritingCrew().crew()
        assert str(crew_instance.process) == "Process.sequential"


class TestPublishingCrew:
    def test_agents_are_created(self):
        crew = PublishingCrew()
        publisher = crew.content_publisher()
        assert publisher.role is not None
        assert len(publisher.tools) == 3  # post_tweet, publish_to_medium, post_to_discord

    def test_tasks_are_created(self):
        crew = PublishingCrew()
        tasks = [
            crew.publish_twitter_task(),
            crew.publish_medium_task(),
            crew.publish_discord_task(),
        ]
        assert len(tasks) == 3

    def test_crew_is_sequential(self):
        crew_instance = PublishingCrew().crew()
        assert str(crew_instance.process) == "Process.sequential"
