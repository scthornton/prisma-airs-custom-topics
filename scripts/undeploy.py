#!/usr/bin/env python3
"""
Remove custom topics from your Prisma AIRS tenant.

Usage:
    python undeploy.py system_prompt_disclosure         # Remove one topic by name
    python undeploy.py topics/ai-security.json          # Remove all topics in a category file
    python undeploy.py --all                             # Remove ALL custom topics
    python undeploy.py --all --force                     # Skip confirmation
    python undeploy.py --prefix SDK-TEST-                # Remove topics matching a prefix
"""

import json
import sys
import os
import time
from pathlib import Path

try:
    from airs_api_mgmt import MgmtClient
    from airs_api_mgmt.exceptions import MgmtSdkClientError
except ImportError:
    print("ERROR: pan-airs-api-mgmt-sdk not installed.")
    print("  pip install --extra-index-url https://test.pypi.org/simple/ pan-airs-api-mgmt-sdk==0.0.1a14")
    sys.exit(1)

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
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


def fetch_all_topics(client: MgmtClient) -> dict[str, str]:
    """Returns {topic_name: topic_id}."""
    topics = {}
    offset = 0
    while True:
        resp = client.custom_topics.retrieve_all_custom_topics_by_tsgid(
            offset=offset, limit=100
        )
        for t in resp.custom_topics or []:
            topics[t.topic_name] = t.topic_id
        if not resp.next_offset or resp.next_offset <= offset:
            break
        offset = resp.next_offset
    return topics


def names_from_file(filepath: str) -> list[str]:
    """Extract topic names from a category JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f)
    return [t["topic_name"] for t in data.get("topics", [])]


def delete_topics(client: MgmtClient, targets: dict[str, str], force: bool = False):
    """Delete topics by {name: topic_id}. Tries standard delete, falls back to force."""
    deleted = 0
    failed = 0

    for name, topic_id in targets.items():
        try:
            client.custom_topics.delete_custom_topic(topic_id=topic_id)
            print(f"  {GREEN}DELETED{RESET} {name}")
            deleted += 1
        except MgmtSdkClientError:
            # Standard delete failed — try force
            try:
                client.custom_topics.force_delete_custom_topic(
                    topic_id=topic_id, updated_by="undeploy-script"
                )
                print(f"  {GREEN}DELETED{RESET} {name} (force)")
                deleted += 1
            except Exception as e:
                print(f"  {RED}FAILED{RESET}  {name}: {e}")
                failed += 1
        except Exception as e:
            print(f"  {RED}FAILED{RESET}  {name}: {e}")
            failed += 1
        time.sleep(0.2)

    print(f"\n  Deleted: {deleted}  Failed: {failed}")


def main():
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    remove_all = "--all" in sys.argv
    force = "--force" in sys.argv

    # Get prefix filter
    prefix = ""
    for i, arg in enumerate(sys.argv):
        if arg == "--prefix" and i + 1 < len(sys.argv):
            prefix = sys.argv[i + 1]

    client = get_client()
    deployed = fetch_all_topics(client)

    if not deployed:
        print("No custom topics deployed. Nothing to remove.")
        return

    # Determine which topics to remove
    if remove_all:
        targets = deployed
    elif prefix:
        targets = {n: tid for n, tid in deployed.items() if n.startswith(prefix)}
    else:
        # First non-flag argument
        target = sys.argv[1]
        if os.path.isfile(target):
            names = names_from_file(target)
            targets = {n: deployed[n] for n in names if n in deployed}
            not_found = [n for n in names if n not in deployed]
            if not_found:
                print(f"  {YELLOW}Not deployed (skipping):{RESET} {', '.join(not_found)}")
        elif os.path.isdir(target):
            names = []
            for f in sorted(Path(target).glob("*.json")):
                names.extend(names_from_file(str(f)))
            targets = {n: deployed[n] for n in names if n in deployed}
        else:
            # Treat as a topic name
            if target in deployed:
                targets = {target: deployed[target]}
            else:
                print(f"{RED}ERROR:{RESET} Topic '{target}' not found in deployed topics.")
                print(f"  Deployed: {', '.join(sorted(deployed.keys()))}")
                sys.exit(1)

    if not targets:
        print("No matching topics to remove.")
        return

    # Confirmation
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  Topic Removal{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"  Removing {BOLD}{len(targets)}{RESET} of {len(deployed)} deployed topics:\n")
    for name in sorted(targets.keys()):
        print(f"    - {name}")

    if not force:
        print(f"\n  {YELLOW}This cannot be undone.{RESET}")
        answer = input(f"  Continue? [y/N] ").strip().lower()
        if answer != "y":
            print("  Cancelled.")
            return

    print()
    delete_topics(client, targets, force=force)


if __name__ == "__main__":
    main()
