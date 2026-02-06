#!/usr/bin/env python3
"""
Deploy custom topics to Prisma AIRS via the Management SDK.

Usage:
    python deploy.py topics/                           # Deploy all categories
    python deploy.py topics/ai-security.json           # Deploy one category
    python deploy.py topics/ --dry-run                 # Preview without deploying
    python deploy.py topics/ --created-by "scott"      # Tag who deployed
"""

import json
import sys
import os
import time
from pathlib import Path

# ── SDK Import ──────────────────────────────────────────────
try:
    from airs_api_mgmt import MgmtClient
    from airs_api_mgmt.exceptions import MgmtSdkClientError
except ImportError:
    print("ERROR: pan-airs-api-mgmt-sdk not installed.")
    print("  pip install --extra-index-url https://test.pypi.org/simple/ pan-airs-api-mgmt-sdk==0.0.1a14")
    sys.exit(1)

# ── ANSI Colors ─────────────────────────────────────────────
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ── Auth ────────────────────────────────────────────────────
# SDK v0.0.1a14 defaults to auth.appsvc which TLS-resets from some networks.
# Override to the working endpoint.
TOKEN_URL = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"


def get_client(created_by: str = "") -> MgmtClient:
    """Create an authenticated MgmtClient."""
    client_id = os.environ.get("MODEL_SECURITY_CLIENT_ID") or os.environ.get("PANW_CLIENT_ID")
    client_secret = os.environ.get("MODEL_SECURITY_CLIENT_SECRET") or os.environ.get("PANW_CLIENT_SECRET")

    if not client_id or not client_secret:
        print(f"{RED}ERROR:{RESET} Set MODEL_SECURITY_CLIENT_ID and MODEL_SECURITY_CLIENT_SECRET")
        print(f"       (or PANW_CLIENT_ID / PANW_CLIENT_SECRET)")
        sys.exit(1)

    return MgmtClient(
        client_id=client_id,
        client_secret=client_secret,
        token_base_url=TOKEN_URL,
    )


def load_topics_from_file(filepath: str) -> list[dict]:
    """Load topics from a category JSON file."""
    with open(filepath, "r") as f:
        data = json.load(f)
    category = data.get("category", Path(filepath).stem)
    topics = data.get("topics", [])
    for t in topics:
        t["_category"] = category
        t["_source"] = Path(filepath).name
    return topics


def load_topics(target: str) -> list[dict]:
    """Load topics from a file or directory."""
    topics = []
    if os.path.isdir(target):
        for f in sorted(Path(target).glob("*.json")):
            topics.extend(load_topics_from_file(str(f)))
    elif os.path.isfile(target):
        topics.extend(load_topics_from_file(target))
    else:
        print(f"{RED}ERROR:{RESET} {target} not found")
        sys.exit(1)
    return topics


def get_existing_topics(client: MgmtClient) -> dict[str, str]:
    """Fetch all deployed topics. Returns {topic_name: topic_id}."""
    existing = {}
    offset = 0
    while True:
        resp = client.custom_topics.retrieve_all_custom_topics_by_tsgid(
            offset=offset, limit=100
        )
        for t in resp.custom_topics or []:
            existing[t.topic_name] = t.topic_id
        if not resp.next_offset or resp.next_offset <= offset:
            break
        offset = resp.next_offset
    return existing


def deploy(target: str, dry_run: bool = False, created_by: str = ""):
    """Deploy topics to Prisma AIRS."""
    topics = load_topics(target)
    if not topics:
        print("No topics found.")
        sys.exit(1)

    categories = sorted(set(t["_category"] for t in topics))
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  Custom Topic Deployment{RESET}")
    print(f"{CYAN}{'=' * 60}{RESET}")
    print(f"  Topics:     {len(topics)} across {len(categories)} categories")
    print(f"  Categories: {', '.join(categories)}")
    if dry_run:
        print(f"  Mode:       {YELLOW}DRY RUN{RESET} (no changes will be made)")
    if created_by:
        print(f"  Created by: {created_by}")

    if dry_run:
        print(f"\n{BOLD}  Dry-run preview:{RESET}\n")
        for t in topics:
            name = t["topic_name"]
            desc = t["description"][:60] + "..." if len(t["description"]) > 60 else t["description"]
            ex_count = len(t.get("examples", []))
            print(f"  [{t['_category']}] {BOLD}{name}{RESET}")
            print(f"    {DIM}{desc}{RESET}")
            print(f"    {ex_count} examples")
        print(f"\n  {YELLOW}Dry run complete — no topics deployed.{RESET}")
        print(f"  Remove --dry-run to deploy.\n")
        return

    # Authenticate
    print(f"\n  Authenticating...", end=" ", flush=True)
    client = get_client(created_by)
    print(f"{GREEN}OK{RESET}")

    # Get existing topics to skip duplicates
    print(f"  Checking existing topics...", end=" ", flush=True)
    existing = get_existing_topics(client)
    print(f"{GREEN}{len(existing)} found{RESET}")

    # Deploy
    created = 0
    skipped = 0
    failed = 0
    errors = []

    current_cat = ""
    for t in topics:
        cat = t["_category"]
        if cat != current_cat:
            current_cat = cat
            print(f"\n{BOLD}  {cat}{RESET}")

        name = t["topic_name"]

        # Skip if already exists
        if name in existing:
            print(f"    {YELLOW}EXISTS{RESET}  {name} (ID: {existing[name][:8]}...)")
            skipped += 1
            continue

        try:
            kwargs = dict(
                topic_name=name,
                description=t["description"],
                examples=t["examples"],
                revision=1,
            )
            if created_by:
                kwargs["created_by"] = created_by

            result = client.custom_topics.create_new_custom_topic(**kwargs)
            print(f"    {GREEN}CREATED{RESET} {name} (ID: {result.topic_id[:8]}...)")
            created += 1
            # Small delay to avoid rate limiting
            time.sleep(0.3)

        except MgmtSdkClientError as e:
            # 409 = already exists (race condition with our check)
            if "409" in str(e) or "already exists" in str(e).lower():
                print(f"    {YELLOW}EXISTS{RESET}  {name} (conflict)")
                skipped += 1
            else:
                print(f"    {RED}FAILED{RESET}  {name}: {e}")
                errors.append((name, str(e)))
                failed += 1

        except Exception as e:
            print(f"    {RED}FAILED{RESET}  {name}: {type(e).__name__}: {e}")
            errors.append((name, str(e)))
            failed += 1

    # Summary
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"{BOLD}  Summary{RESET}")
    print(f"{'=' * 60}")
    print(f"  {GREEN}Created:{RESET}  {created}")
    print(f"  {YELLOW}Skipped:{RESET}  {skipped} (already deployed)")
    if failed:
        print(f"  {RED}Failed:{RESET}   {failed}")
        for name, err in errors:
            print(f"    - {name}: {err}")
    print()


def main():
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)

    target = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    created_by = ""

    for i, arg in enumerate(sys.argv):
        if arg == "--created-by" and i + 1 < len(sys.argv):
            created_by = sys.argv[i + 1]

    deploy(target, dry_run=dry_run, created_by=created_by)


if __name__ == "__main__":
    main()
