"""Crew orchestration for the Hedera Content Agent."""

from __future__ import annotations

import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task

from src.tools.youtube_tools import search_hedera_youtube, fetch_video_transcript
from src.tools.twitter_tools import search_hedera_tweets, post_tweet
from src.tools.medium_tools import publish_to_medium
from src.tools.discord_tools import post_to_discord
from src.tools.web_scraper_tools import scrape_hedera_blog


def _llm() -> LLM:
    """Create the shared LLM instance."""
    return LLM(
        model=f"openai/{os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}",
        temperature=0.2,
    )


# =============================================================================
# Research Crew
# =============================================================================

@CrewBase
class ResearchCrew:
    """Crew that researches Hedera content from YouTube, Twitter, and Web."""

    agents_config = "config/research_agents.yaml"
    tasks_config = "config/research_tasks.yaml"

    @agent
    def youtube_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["youtube_researcher"],
            tools=[search_hedera_youtube, fetch_video_transcript],
            llm=_llm(),
            allow_delegation=False,
            max_iter=3,
            verbose=True,
        )

    @agent
    def twitter_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["twitter_researcher"],
            tools=[search_hedera_tweets],
            llm=_llm(),
            allow_delegation=False,
            max_iter=2,
            verbose=True,
        )

    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["web_researcher"],
            tools=[scrape_hedera_blog],
            llm=_llm(),
            allow_delegation=False,
            max_iter=2,
            verbose=True,
        )

    @agent
    def content_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config["content_strategist"],
            tools=[],
            llm=_llm(),
            allow_delegation=False,
            verbose=True,
        )

    @task
    def youtube_research_task(self) -> Task:
        cfg = self.tasks_config["youtube_research_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.youtube_researcher(),
        )

    @task
    def twitter_research_task(self) -> Task:
        cfg = self.tasks_config["twitter_research_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.twitter_researcher(),
        )

    @task
    def web_research_task(self) -> Task:
        cfg = self.tasks_config["web_research_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.web_researcher(),
        )

    @task
    def content_strategy_task(self) -> Task:
        cfg = self.tasks_config["content_strategy_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_strategist(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.youtube_researcher(),
                self.twitter_researcher(),
                self.web_researcher(),
                self.content_strategist(),
            ],
            tasks=[
                self.youtube_research_task(),
                self.twitter_research_task(),
                self.web_research_task(),
                self.content_strategy_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# Writing Crew
# =============================================================================

@CrewBase
class WritingCrew:
    """Crew that writes content for Twitter, Medium, and Discord."""

    agents_config = "config/writing_agents.yaml"
    tasks_config = "config/writing_tasks.yaml"

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_writer"],
            tools=[],
            llm=_llm(),
            allow_delegation=False,
            verbose=True,
        )

    @task
    def twitter_writing_task(self) -> Task:
        cfg = self.tasks_config["twitter_writing_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_writer(),
        )

    @task
    def medium_writing_task(self) -> Task:
        cfg = self.tasks_config["medium_writing_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_writer(),
        )

    @task
    def discord_writing_task(self) -> Task:
        cfg = self.tasks_config["discord_writing_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_writer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.content_writer()],
            tasks=[
                self.twitter_writing_task(),
                self.medium_writing_task(),
                self.discord_writing_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )


# =============================================================================
# Publishing Crew
# =============================================================================

@CrewBase
class PublishingCrew:
    """Crew that publishes content to Twitter, Medium, and Discord."""

    agents_config = "config/publishing_agents.yaml"
    tasks_config = "config/publishing_tasks.yaml"

    @agent
    def content_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config["content_publisher"],
            tools=[post_tweet, publish_to_medium, post_to_discord],
            llm=_llm(),
            allow_delegation=False,
            max_iter=3,
            verbose=True,
        )

    @task
    def publish_twitter_task(self) -> Task:
        cfg = self.tasks_config["publish_twitter_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_publisher(),
        )

    @task
    def publish_medium_task(self) -> Task:
        cfg = self.tasks_config["publish_medium_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_publisher(),
        )

    @task
    def publish_discord_task(self) -> Task:
        cfg = self.tasks_config["publish_discord_task"]
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=self.content_publisher(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.content_publisher()],
            tasks=[
                self.publish_twitter_task(),
                self.publish_medium_task(),
                self.publish_discord_task(),
            ],
            process=Process.sequential,
            verbose=True,
        )
