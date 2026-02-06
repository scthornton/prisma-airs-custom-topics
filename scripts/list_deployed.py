#!/usr/bin/env python3
"""
List custom topics currently deployed in your Prisma AIRS tenant.

Usage:
    python list_deployed.py                # List all deployed topics
    python list_deployed.py --json         # Output as JSON
    python list_deployed.py --ids          # Show just names and IDs (for scripting)
"""

import sys
import os
import json

try:
    from airs_api_mgmt import MgmtClient
except ImportError:
    print("ERROR: pan-airs-api-mgmt-sdk not installed.")
    print("  pip install --extra-index-url https://test.pypi.org/simple/ pan-airs-api-mgmt-sdk==0.0.1a14")
    sys.exit(1)

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

TOKEN_URL = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"


def get_client() -> MgmtClient:
    client_id = os.environ.get("MODEL_SECURITY_CLIENT_ID") or os.environ.get("PANW_CLIENT_ID")
    client_secret = os.environ.get("MODEL_SECURITY_CLIENT_SECRET") or os.environ.get("PANW_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(f"{RED}ERROR:{RESET} Set MODEL_SECURITY_CLIENT_ID and MODEL_SECURITY_CLIENT_SECRET")
        sys.exit(1)
    return MgmtClient(
        client_id=client_id,
        client_secret=client_secret,
        token_base_url=TOKEN_URL,
    )


def fetch_all_topics(client: MgmtClient) -> list:
    topics = []
    offset = 0
    while True:
        resp = client.custom_topics.retrieve_all_custom_topics_by_tsgid(
            offset=offset, limit=100
        )
        for t in resp.custom_topics or []:
            topics.append(t)
        if not resp.next_offset or resp.next_offset <= offset:
            break
        offset = resp.next_offset
    return topics


def main():
    as_json = "--json" in sys.argv
    ids_only = "--ids" in sys.argv

    client = get_client()
    topics = fetch_all_topics(client)

    if not topics:
        if as_json:
            print("[]")
        else:
            print("No custom topics deployed.")
        return

    if as_json:
        output = []
        for t in topics:
            output.append({
                "topic_id": t.topic_id,
                "topic_name": t.topic_name,
                "description": t.description,
                "examples": t.examples,
                "revision": t.revision,
                "active": t.active,
                "created_by": t.created_by,
            })
        print(json.dumps(output, indent=2))
        return

    if ids_only:
        for t in topics:
            print(f"{t.topic_name}\t{t.topic_id}")
        return

    # Pretty table output
    print(f"\n{BOLD}{CYAN}{'=' * 70}{RESET}")
    print(f"{BOLD}{CYAN}  Deployed Custom Topics ({len(topics)}){RESET}")
    print(f"{CYAN}{'=' * 70}{RESET}")

    for i, t in enumerate(topics, 1):
        desc_preview = t.description[:65] + "..." if t.description and len(t.description) > 65 else (t.description or "")
        ex_count = len(t.examples) if t.examples else 0
        active_str = f"{GREEN}active{RESET}" if t.active else f"{DIM}inactive{RESET}" if t.active is False else f"{DIM}—{RESET}"

        print(f"\n  {BOLD}{i:2d}. {t.topic_name}{RESET}")
        print(f"      ID: {t.topic_id}  |  rev: {t.revision}  |  {active_str}")
        print(f"      {DIM}{desc_preview}{RESET}")
        print(f"      {ex_count} examples", end="")
        if t.created_by:
            print(f"  |  by: {t.created_by}", end="")
        print()

    print(f"\n{BOLD}  Total: {len(topics)} topics{RESET}\n")


if __name__ == "__main__":
    main()
