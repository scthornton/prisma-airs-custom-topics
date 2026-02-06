#!/usr/bin/env python3
"""
Validate Prisma AIRS custom topics against platform constraints.

Usage:
    python validate.py topics/ai-security.json        # Validate one file
    python validate.py topics/                         # Validate all files in directory
    python validate.py topics/ --strict                # Fail on warnings too
"""

import json
import sys
import os
from pathlib import Path

# Prisma AIRS Custom Topic Constraints
MAX_TOPIC_NAME_CHARS = 100
MAX_DESCRIPTION_CHARS = 250
MAX_EXAMPLE_CHARS = 250
MAX_EXAMPLES = 5
MIN_EXAMPLES = 1
MAX_TOTAL_CHARS = 1000
MAX_TOPICS_PER_PROFILE = 20

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def validate_topic(topic: dict, category: str) -> tuple[list, list]:
    """Validate a single topic. Returns (errors, warnings)."""
    errors = []
    warnings = []
    name = topic.get("topic_name", "<missing>")

    # Required fields
    if not topic.get("topic_name"):
        errors.append(f"Missing required field: topic_name")
    if not topic.get("description"):
        errors.append(f"Missing required field: description")
    if not topic.get("examples"):
        errors.append(f"Missing required field: examples")
        return errors, warnings

    # Name length
    name_len = len(topic["topic_name"])
    if name_len > MAX_TOPIC_NAME_CHARS:
        errors.append(f"topic_name is {name_len} chars (max {MAX_TOPIC_NAME_CHARS})")

    # Description length
    desc_len = len(topic["description"])
    if desc_len > MAX_DESCRIPTION_CHARS:
        errors.append(f"description is {desc_len} chars (max {MAX_DESCRIPTION_CHARS})")
    elif desc_len < 50:
        warnings.append(f"description is only {desc_len} chars - invest more in description (carries ~40-50% classifier weight)")
    elif desc_len > 230:
        pass  # Good - using the budget well

    # Examples count
    examples = topic["examples"]
    if len(examples) < MIN_EXAMPLES:
        errors.append(f"needs at least {MIN_EXAMPLES} example (has {len(examples)})")
    if len(examples) > MAX_EXAMPLES:
        errors.append(f"has {len(examples)} examples (max {MAX_EXAMPLES})")

    # Example lengths
    for i, ex in enumerate(examples):
        ex_len = len(ex)
        if ex_len > MAX_EXAMPLE_CHARS:
            errors.append(f"example[{i}] is {ex_len} chars (max {MAX_EXAMPLE_CHARS})")

    # Total character budget
    total = name_len + desc_len + sum(len(ex) for ex in examples)
    if total > MAX_TOTAL_CHARS:
        errors.append(f"total chars {total} exceeds {MAX_TOTAL_CHARS} limit (over by {total - MAX_TOTAL_CHARS})")
    elif total > 950:
        warnings.append(f"total chars {total} -close to {MAX_TOTAL_CHARS} limit ({MAX_TOTAL_CHARS - total} remaining)")

    # Example diversity check (warn if examples are too similar)
    if len(examples) >= 3:
        first_words = [ex.split()[0].lower() if ex.split() else "" for ex in examples]
        if len(set(first_words)) < len(first_words) * 0.6:
            warnings.append(f"examples may lack diversity -{len(set(first_words))} unique starting words out of {len(first_words)}")

    # Type check
    topic_type = topic.get("type", "")
    if topic_type and topic_type not in ("DENY", "ALLOW"):
        errors.append(f"type must be DENY or ALLOW (got '{topic_type}')")

    return errors, warnings


def validate_file(filepath: str) -> dict:
    """Validate a category JSON file. Returns results dict."""
    results = {
        "file": filepath,
        "category": "",
        "topics": [],
        "total_errors": 0,
        "total_warnings": 0,
    }

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        results["total_errors"] = 1
        results["topics"].append({"name": "<file>", "errors": [f"Invalid JSON: {e}"], "warnings": []})
        return results

    results["category"] = data.get("category", "<unknown>")
    topics = data.get("topics", [])

    for topic in topics:
        name = topic.get("topic_name", "<unnamed>")
        errors, warnings = validate_topic(topic, results["category"])

        # Compute char budget for display
        name_len = len(topic.get("topic_name", ""))
        desc_len = len(topic.get("description", ""))
        examples = topic.get("examples", [])
        ex_total = sum(len(ex) for ex in examples)
        total = name_len + desc_len + ex_total

        results["topics"].append({
            "name": name,
            "errors": errors,
            "warnings": warnings,
            "chars": {
                "name": name_len,
                "description": desc_len,
                "examples": ex_total,
                "total": total,
                "remaining": MAX_TOTAL_CHARS - total,
            }
        })
        results["total_errors"] += len(errors)
        results["total_warnings"] += len(warnings)

    return results


def print_results(results: dict, verbose: bool = True):
    """Pretty-print validation results."""
    category = results["category"]
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {category}{RESET} -{results['file']}")
    print(f"{CYAN}{'=' * 60}{RESET}")

    for topic in results["topics"]:
        name = topic["name"]
        errors = topic["errors"]
        warnings = topic["warnings"]
        chars = topic.get("chars", {})

        if errors:
            status = f"{RED}FAIL{RESET}"
        elif warnings:
            status = f"{YELLOW}WARN{RESET}"
        else:
            status = f"{GREEN}PASS{RESET}"

        print(f"\n  [{status}] {BOLD}{name}{RESET}")

        if chars:
            total = chars["total"]
            remaining = chars["remaining"]
            bar_pct = min(total / MAX_TOTAL_CHARS, 1.0)
            bar_len = int(bar_pct * 30)
            bar_color = GREEN if remaining > 100 else (YELLOW if remaining > 0 else RED)
            bar = f"{bar_color}{'█' * bar_len}{RESET}{'░' * (30 - bar_len)}"
            print(f"         Budget: [{bar}] {total}/{MAX_TOTAL_CHARS} ({remaining} remaining)")
            print(f"         name({chars['name']}) + desc({chars['description']}) + examples({chars['examples']})")

        for err in errors:
            print(f"         {RED}ERROR:{RESET} {err}")
        for warn in warnings:
            print(f"         {YELLOW}WARN:{RESET}  {warn}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <file_or_directory> [--strict]")
        sys.exit(1)

    target = sys.argv[1]
    strict = "--strict" in sys.argv

    files = []
    if os.path.isdir(target):
        files = sorted(Path(target).glob("*.json"))
    elif os.path.isfile(target):
        files = [Path(target)]
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    if not files:
        print(f"No JSON files found in {target}")
        sys.exit(1)

    all_results = []
    total_topics = 0
    total_errors = 0
    total_warnings = 0
    all_topic_names = []

    for f in files:
        results = validate_file(str(f))
        all_results.append(results)
        total_topics += len(results["topics"])
        total_errors += results["total_errors"]
        total_warnings += results["total_warnings"]
        all_topic_names.extend(t["name"] for t in results["topics"])
        print_results(results)

    # Check for duplicate topic names across files
    seen = set()
    duplicates = []
    for name in all_topic_names:
        if name in seen:
            duplicates.append(name)
        seen.add(name)

    # Summary
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  SUMMARY{RESET}")
    print(f"{'=' * 60}")
    print(f"  Files validated:  {len(files)}")
    print(f"  Total topics:     {total_topics}")
    print(f"  Errors:           {RED if total_errors else GREEN}{total_errors}{RESET}")
    print(f"  Warnings:         {YELLOW if total_warnings else GREEN}{total_warnings}{RESET}")

    if duplicates:
        print(f"\n  {RED}DUPLICATE TOPIC NAMES:{RESET}")
        for dup in duplicates:
            print(f"    - {dup}")
        total_errors += len(duplicates)

    if total_topics > MAX_TOPICS_PER_PROFILE:
        print(f"\n  {YELLOW}NOTE:{RESET} {total_topics} topics total -exceeds {MAX_TOPICS_PER_PROFILE}/profile limit.")
        print(f"  Select up to {MAX_TOPICS_PER_PROFILE} topics per security profile.")

    if total_errors > 0:
        print(f"\n  {RED}{BOLD}VALIDATION FAILED{RESET} -fix {total_errors} error(s) before deploying")
        sys.exit(1)
    elif strict and total_warnings > 0:
        print(f"\n  {YELLOW}{BOLD}STRICT MODE: FAILED{RESET} -fix {total_warnings} warning(s)")
        sys.exit(1)
    else:
        print(f"\n  {GREEN}{BOLD}VALIDATION PASSED{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
