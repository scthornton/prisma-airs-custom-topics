#!/usr/bin/env python3
"""
Export Prisma AIRS custom topics from JSON to CSV format.

Usage:
    python export_csv.py                    # Export all topics to exports/
    python export_csv.py --summary          # Export summary view only
    python export_csv.py --api-ready        # Export API-deployable format (no metadata)
"""

import json
import csv
import sys
import os
from pathlib import Path

TOPICS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "topics")
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


def load_all_topics() -> list[dict]:
    """Load all topics from JSON files."""
    topics = []
    for filepath in sorted(Path(TOPICS_DIR).glob("*.json")):
        with open(filepath, "r") as f:
            data = json.load(f)
        category = data.get("category", "<unknown>")
        for topic in data.get("topics", []):
            topic["_category"] = category
            topic["_source_file"] = filepath.name
            topics.append(topic)
    return topics


def export_full_csv(topics: list[dict], output_path: str):
    """Export full topic details to CSV."""
    fieldnames = [
        "category",
        "topic_name",
        "type",
        "description",
        "example_1",
        "example_2",
        "example_3",
        "example_4",
        "example_5",
        "total_chars",
        "chars_remaining",
        "source_file",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for topic in topics:
            examples = topic.get("examples", [])
            name_len = len(topic.get("topic_name", ""))
            desc_len = len(topic.get("description", ""))
            ex_total = sum(len(ex) for ex in examples)
            total = name_len + desc_len + ex_total

            row = {
                "category": topic.get("_category", ""),
                "topic_name": topic.get("topic_name", ""),
                "type": topic.get("type", "DENY"),
                "description": topic.get("description", ""),
                "example_1": examples[0] if len(examples) > 0 else "",
                "example_2": examples[1] if len(examples) > 1 else "",
                "example_3": examples[2] if len(examples) > 2 else "",
                "example_4": examples[3] if len(examples) > 3 else "",
                "example_5": examples[4] if len(examples) > 4 else "",
                "total_chars": total,
                "chars_remaining": 1000 - total,
                "source_file": topic.get("_source_file", ""),
            }
            writer.writerow(row)

    print(f"  Exported {len(topics)} topics to {output_path}")


def export_summary_csv(topics: list[dict], output_path: str):
    """Export condensed summary view to CSV."""
    fieldnames = [
        "category",
        "topic_name",
        "type",
        "description",
        "num_examples",
        "total_chars",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for topic in topics:
            examples = topic.get("examples", [])
            name_len = len(topic.get("topic_name", ""))
            desc_len = len(topic.get("description", ""))
            ex_total = sum(len(ex) for ex in examples)
            total = name_len + desc_len + ex_total

            row = {
                "category": topic.get("_category", ""),
                "topic_name": topic.get("topic_name", ""),
                "type": topic.get("type", "DENY"),
                "description": topic.get("description", ""),
                "num_examples": len(examples),
                "total_chars": total,
            }
            writer.writerow(row)

    print(f"  Exported {len(topics)} topics to {output_path}")


def export_api_ready_csv(topics: list[dict], output_path: str):
    """Export API-deployable format (only fields the Management API accepts)."""
    fieldnames = [
        "topic_name",
        "description",
        "example_1",
        "example_2",
        "example_3",
        "example_4",
        "example_5",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for topic in topics:
            examples = topic.get("examples", [])
            row = {
                "topic_name": topic.get("topic_name", ""),
                "description": topic.get("description", ""),
                "example_1": examples[0] if len(examples) > 0 else "",
                "example_2": examples[1] if len(examples) > 1 else "",
                "example_3": examples[2] if len(examples) > 2 else "",
                "example_4": examples[3] if len(examples) > 3 else "",
                "example_5": examples[4] if len(examples) > 4 else "",
            }
            writer.writerow(row)

    print(f"  Exported {len(topics)} topics to {output_path}")


def main():
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    topics = load_all_topics()

    if not topics:
        print("No topics found in topics/ directory")
        sys.exit(1)

    summary_only = "--summary" in sys.argv
    api_only = "--api-ready" in sys.argv

    print(f"\nLoaded {len(topics)} topics from {len(set(t['_source_file'] for t in topics))} category files\n")

    if api_only:
        export_api_ready_csv(topics, os.path.join(EXPORTS_DIR, "all-topics-api-ready.csv"))
    elif summary_only:
        export_summary_csv(topics, os.path.join(EXPORTS_DIR, "all-topics-summary.csv"))
    else:
        export_full_csv(topics, os.path.join(EXPORTS_DIR, "all-topics.csv"))
        export_summary_csv(topics, os.path.join(EXPORTS_DIR, "all-topics-summary.csv"))
        export_api_ready_csv(topics, os.path.join(EXPORTS_DIR, "all-topics-api-ready.csv"))

    print(f"\nDone. Files written to {EXPORTS_DIR}/")


if __name__ == "__main__":
    main()
