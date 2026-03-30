#!/usr/bin/env python3
"""HederaAgentContent - CLI entry point.

Orchestrates a multi-agent pipeline to research, write, and publish
Hedera blockchain content across X/Twitter, Medium, and Discord.

Usage:
    python main.py                     # Full pipeline (research + write + publish)
    python main.py --research-only     # Only research, no writing or publishing
    python main.py --dry-run           # Full pipeline but skip actual publishing
    python main.py --topic "HCS"       # Research a specific topic
"""

from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

load_dotenv()

from src.crew import ResearchCrew, WritingCrew, PublishingCrew


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hedera Content Agent - Research, write, and publish Hedera content.",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="Hedera latest news",
        help="Topic to research (default: 'Hedera latest news')",
    )
    parser.add_argument(
        "--research-only",
        action="store_true",
        help="Run only the research crew (no writing or publishing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run research and writing but skip actual publishing",
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["en", "es"],
        default="en",
        help="Content language: 'en' (English) or 'es' (Spanish). Default: 'en'",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Disable verbose agent output",
    )
    return parser.parse_args()


def run_research(topic: str) -> str:
    """Run the research crew and return the content strategy."""
    print("\n" + "=" * 60)
    print("PHASE 1: RESEARCH")
    print("=" * 60)

    research_crew = ResearchCrew()
    result = research_crew.crew().kickoff(inputs={"topic": topic})

    print("\n--- Research Result ---")
    print(str(result)[:2000])
    return str(result)


def run_writing(content_plan: str, language: str = "en") -> dict:
    """Run the writing crew and return content for all platforms."""
    lang_label = "Spanish" if language == "es" else "English"
    print("\n" + "=" * 60)
    print(f"PHASE 2: WRITING ({lang_label})")
    print("=" * 60)

    writing_crew = WritingCrew()
    result = writing_crew.crew().kickoff(inputs={
        "content_plan": content_plan,
        "language": language,
        "language_name": lang_label,
    })

    print("\n--- Writing Result ---")
    output = str(result)
    print(output[:2000])

    return {"content": output}


def run_publishing(content: dict) -> dict:
    """Run the publishing crew to post content to all platforms."""
    print("\n" + "=" * 60)
    print("PHASE 3: PUBLISHING")
    print("=" * 60)

    publishing_crew = PublishingCrew()
    result = publishing_crew.crew().kickoff(inputs=content)

    print("\n--- Publishing Result ---")
    output = str(result)
    print(output[:2000])

    return {"result": output}


def main():
    args = parse_args()

    print("=" * 60)
    print("  HEDERA CONTENT AGENT")
    print(f"  Topic: {args.topic}")
    lang_label = "Spanish" if args.language == "es" else "English"
    print(f"  Language: {lang_label}")
    print(f"  Mode: {'research-only' if args.research_only else 'dry-run' if args.dry_run else 'full'}")
    print("=" * 60)

    # Phase 1: Research
    research_result = run_research(args.topic)

    if args.research_only:
        print("\n[Research-only mode] Stopping after research phase.")
        print("\nResearch output saved. Use --dry-run to also generate content.")
        return

    # Phase 2: Writing
    writing_result = run_writing(research_result, language=args.language)

    if args.dry_run:
        print("\n[Dry-run mode] Stopping before publishing.")
        print("\nGenerated content:")
        print(json.dumps(writing_result, indent=2, default=str)[:3000])
        print("\nRemove --dry-run to publish to all platforms.")
        return

    # Phase 3: Publishing
    publish_result = run_publishing(writing_result)

    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(json.dumps(publish_result, indent=2, default=str)[:2000])


if __name__ == "__main__":
    main()
