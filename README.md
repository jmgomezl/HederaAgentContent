# HederaAgentContent

A multi-agent AI system that researches, writes, and publishes content for the Hedera blockchain ecosystem across **X/Twitter**, **Medium**, and **Discord**.

Built with **CrewAI** for agent orchestration, **LangChain** for LLM chains, and **Pydantic** for structured outputs. Supports **English** and **Spanish** content generation.

---

## Architecture

The system uses a 3-phase pipeline with 6 specialized agents organized into 3 crews:

```
+-------------------------------------------------------------+
|                      RESEARCH CREW                          |
|                                                             |
|  YouTube Researcher --> Twitter Researcher --> Web           |
|  (search + transcript)  (search @Hedera)      Researcher   |
|                                                (blog scrape)|
|                           |                                 |
|                   Content Strategist                        |
|                   (pick topic + plan)                       |
+---------------------------+---------------------------------+
                            | content plan + language
+---------------------------v---------------------------------+
|                      WRITING CREW                           |
|                                                             |
|  Content Writer --> Twitter Thread (en/es)                  |
|                 --> Medium Article  (en/es)                  |
|                 --> Discord Message (en/es)                  |
+---------------------------+---------------------------------+
                            | finalized content
+---------------------------v---------------------------------+
|                    PUBLISHING CREW                          |
|                                                             |
|  Content Publisher --> Post to X/Twitter                     |
|                   --> Publish to Medium (draft)              |
|                   --> Post to Discord (webhook)              |
+-------------------------------------------------------------+
```

### Agents

| Agent | Role | Tools |
|-------|------|-------|
| `youtube_researcher` | Searches Hedera YouTube channel, fetches transcripts | `search_hedera_youtube`, `fetch_video_transcript` |
| `twitter_researcher` | Monitors @Hedera on X for trends | `search_hedera_tweets` |
| `web_researcher` | Scrapes hedera.com/blog for articles | `scrape_hedera_blog` |
| `content_strategist` | Analyzes research, creates content plan | None (reasoning only) |
| `content_writer` | Writes platform-specific content (bilingual EN/ES) | None (reasoning only) |
| `content_publisher` | Publishes to all platforms | `post_tweet`, `publish_to_medium`, `post_to_discord` |

### Tools

| Tool | API | Description |
|------|-----|-------------|
| `search_hedera_youtube` | YouTube Data API v3 | Search Hedera's official channel for recent videos |
| `fetch_video_transcript` | youtube-transcript-api | Extract English transcripts from YouTube videos |
| `search_hedera_tweets` | Twitter API v2 | Search recent tweets from/about @Hedera |
| `post_tweet` | Twitter API v2 (OAuth1) | Post tweet threads |
| `publish_to_medium` | Medium API | Publish articles as drafts or public posts |
| `post_to_discord` | Discord Webhooks | Post rich embed messages to a channel |
| `scrape_hedera_blog` | Web scraping | Extract recent articles from hedera.com/blog |

---

## Setup

### Prerequisites

- Python 3.11+ (required by CrewAI)
- API keys for: OpenAI, YouTube, Twitter/X, Medium, Discord

### Installation

```bash
cd HederaAgentContent

# Create virtual environment (must use Python 3.11+)
python3.11 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### API Keys

| Service | How to Get |
|---------|-----------|
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **YouTube Data API v3** | [Google Cloud Console](https://console.cloud.google.com/) > APIs & Services > Enable YouTube Data API v3 > Create credentials |
| **Twitter/X API v2** | [developer.twitter.com](https://developer.twitter.com/) > Projects & Apps > Create app with OAuth 1.0a (read + write) |
| **Medium** | [medium.com/me/settings/security](https://medium.com/me/settings/security) > Integration tokens > Get token |
| **Discord Webhook** | Server Settings > Integrations > Webhooks > New Webhook > Copy URL |
| **Serper** (optional) | [serper.dev](https://serper.dev/) for web search fallback |

---

## Usage

### Full Pipeline (Research + Write + Publish)

```bash
python main.py
```

### Research Only (no writing or publishing)

```bash
python main.py --research-only
```

### Dry Run (research + write, skip publishing)

```bash
python main.py --dry-run
```

### Custom Topic

```bash
python main.py --topic "Hedera Token Service"
python main.py --topic "HBAR DeFi" --dry-run
```

### Language Selection (English / Spanish)

Content can be generated in English (default) or Spanish:

```bash
# Generate content in English (default)
python main.py --language en --topic "Hedera Token Service"

# Generate content in Spanish
python main.py --language es --topic "Hedera Token Service"

# Combine with other flags
python main.py --language es --topic "HBAR DeFi" --dry-run
```

When `--language es` is set:
- All tweet threads are written in Spanish
- Medium articles are written entirely in Spanish (title, body, headings)
- Discord announcements are written in Spanish with natural idiomatic phrasing
- Technical terms (Hedera, HBAR, HTS, etc.) remain in their original form
- Research phase always runs in English (source data is English)

### CLI Options

| Flag | Description |
|------|-------------|
| `--topic TEXT` | Research topic (default: "Hedera latest news") |
| `--language {en,es}` | Content language: English or Spanish (default: en) |
| `--research-only` | Stop after research phase |
| `--dry-run` | Generate content but don't publish |
| `--quiet` | Disable verbose agent output |

---

## Project Structure

```
HederaAgentContent/
  main.py                           # CLI entry point
  requirements.txt                  # Python dependencies
  .env.example                      # API keys template
  .env                              # Your API keys (gitignored)
  .gitignore
  config/
    agents.yaml                     # All agent definitions (reference copy)
    tasks.yaml                      # All task definitions (reference copy)
  src/
    __init__.py
    crew.py                         # 3 CrewAI crews: Research, Writing, Publishing
    models.py                       # Pydantic models for structured I/O
    config/                         # Per-crew YAML configs (loaded by @CrewBase)
      research_agents.yaml          #   4 research agents
      research_tasks.yaml           #   4 research tasks
      writing_agents.yaml           #   1 bilingual writer agent
      writing_tasks.yaml            #   3 writing tasks (Twitter, Medium, Discord)
      publishing_agents.yaml        #   1 publisher agent
      publishing_tasks.yaml         #   3 publishing tasks
    tools/
      __init__.py
      youtube_tools.py              # YouTube Data API v3 search + transcript
      twitter_tools.py              # X/Twitter API v2 search + post
      medium_tools.py               # Medium REST API publish
      discord_tools.py              # Discord webhook post
      web_scraper_tools.py          # BeautifulSoup scraper for hedera.com/blog
    prompts/
      __init__.py
      templates.py                  # Prompt templates with language support
  tests/
    __init__.py
    conftest.py                     # Shared pytest fixtures
    test_models.py                  # Pydantic model tests (incl. language)
    test_tools.py                   # Tool unit tests (mocked API calls)
    test_crew.py                    # Crew integration tests
```

---

## Testing

```bash
# Run all tests (44 tests)
python -m pytest tests/ -v

# Run by category
python -m pytest tests/test_models.py -v    # 16 model tests
python -m pytest tests/test_tools.py -v     # 19 tool tests
python -m pytest tests/test_crew.py -v      #  9 crew tests
```

All tool tests use **mocked API responses** -- no real API keys are needed to run the test suite.

### What the tests cover

- **test_models.py** -- Validates all Pydantic models (VideoInfo, TweetInfo, WebArticle, ResearchResult, ContentPlan, TwitterContent, MediumArticle, DiscordMessage, PublishResult) including language field defaults and Spanish content creation
- **test_tools.py** -- Tests each tool function with mocked HTTP/API responses: YouTube search and transcript extraction, Twitter search and posting, Medium publishing, Discord webhook, Hedera blog scraping, and error handling for missing API keys
- **test_crew.py** -- Verifies that all 3 crews (Research, Writing, Publishing) can instantiate their agents, create their tasks, and configure sequential process execution

---

## Customization

### Adding a New Language

1. Add the language code and instruction to `LANGUAGE_INSTRUCTIONS` in `src/prompts/templates.py`:
   ```python
   LANGUAGE_INSTRUCTIONS = {
       "en": "Write ALL content in English.",
       "es": "Escribe TODO el contenido en espanol...",
       "pt": "Escreva TODO o conteudo em portugues...",  # new
   }
   ```
2. Add the choice to `--language` in `main.py`:
   ```python
   choices=["en", "es", "pt"],
   ```
3. Update the writer agent backstory in `src/config/writing_agents.yaml` to include the new language

### Adding a New Source

1. Create a new tool in `src/tools/` using the `@tool` decorator pattern
2. Create a new `{crew}_agents.yaml` and `{crew}_tasks.yaml` in `src/config/`
3. Wire the agent/task into the appropriate crew in `src/crew.py`

### Adding a New Publishing Platform

1. Create a new tool in `src/tools/` (e.g., `linkedin_tools.py`)
2. Add a new publishing task in `src/config/publishing_tasks.yaml`
3. Add the tool to the `content_publisher` agent in `src/crew.py`

### Changing the LLM

Edit `OPENAI_MODEL` in `.env`:

```
OPENAI_MODEL=gpt-4o-mini    # Default -- good balance of quality and cost
OPENAI_MODEL=gpt-4o         # More capable, higher cost
OPENAI_MODEL=gpt-5.1        # Latest, best quality
```

The model string is passed to CrewAI's `LLM` class as `openai/{model_name}`.

### Adjusting Content Style

Edit the prompt templates in `src/prompts/templates.py` to change tone, length, structure, or formatting rules for each platform. Each platform (Twitter, Medium, Discord) has its own prompt template with language-aware instructions.

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Agent Orchestration | CrewAI | 1.12+ |
| LLM Integration | OpenAI (via CrewAI LLM) | 1.x |
| Data Validation | Pydantic | 2.x |
| YouTube | YouTube Data API v3 + youtube-transcript-api | 1.2+ |
| Twitter/X | Twitter API v2 + requests-oauthlib | -- |
| Medium | Medium REST API | v1 |
| Discord | Discord Webhooks | -- |
| Web Scraping | BeautifulSoup4 + requests | 4.x |
| Testing | pytest + pytest-mock | 8.x |
| Language | Python | 3.11+ |

---

## Authors

- **Mateo** ([@0xCastro](https://github.com/0xCastro))
- **Juan** ([@jmgomezl](https://github.com/jmgomezl))
