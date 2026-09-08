#!/usr/bin/env python3
"""
Collect Reddit posts/comments through the official OAuth API.

Required environment variables:
  REDDIT_CLIENT_ID
  REDDIT_CLIENT_SECRET
  REDDIT_USER_AGENT

Create an app at https://www.reddit.com/prefs/apps and use conservative limits.
Do not use this data to train or fine-tune AI models unless you have the rights
required by Reddit's Data API Terms and the content owners.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"


try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def get_token(client_id: str, client_secret: str, user_agent: str) -> str:
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
    request = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {auth}",
            "User-Agent": user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))["access_token"]


def api_get(path: str, token: str, user_agent: str, delay: float) -> Any:
    time.sleep(delay)
    request = urllib.request.Request(
        f"{API_BASE}{path}",
        headers={"Authorization": f"bearer {token}", "User-Agent": user_agent},
    )
    with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))


def anonymize(value: str) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def flatten_comments(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for child in children:
        if child.get("kind") != "t1":
            continue
        data = child.get("data", {})
        rows.append(data)
        replies = data.get("replies")
        if isinstance(replies, dict):
            rows.extend(flatten_comments(replies.get("data", {}).get("children", [])))
    return rows


def collect(query: str, subreddits: list[str], limit: int, token: str, user_agent: str, delay: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for subreddit in subreddits:
        encoded_query = urllib.parse.quote(query)
        path = f"/r/{subreddit}/search?restrict_sr=1&sort=relevance&t=all&limit={limit}&q={encoded_query}"
        payload = api_get(path, token, user_agent, delay)
        for child in payload.get("data", {}).get("children", []):
            post = child.get("data", {})
            post_id = post.get("id")
            permalink = post.get("permalink", "")
            url = f"https://www.reddit.com{permalink}"
            base = {
                "source": "reddit",
                "query": query,
                "subreddit": subreddit,
                "thread_id": post_id,
                "url": url,
                "title": post.get("title", ""),
                "created_utc": post.get("created_utc"),
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
            }
            rows.append(
                {
                    **base,
                    "record_type": "post",
                    "record_id": post_id,
                    "author_hash": anonymize(post.get("author", "")),
                    "text": post.get("selftext", ""),
                }
            )
            if post_id:
                comments_path = f"/comments/{post_id}?limit=100&depth=4"
                thread = api_get(comments_path, token, user_agent, delay)
                if len(thread) > 1:
                    for comment in flatten_comments(thread[1].get("data", {}).get("children", [])):
                        rows.append(
                            {
                                **base,
                                "record_type": "comment",
                                "record_id": comment.get("id"),
                                "author_hash": anonymize(comment.get("author", "")),
                                "text": comment.get("body", ""),
                            }
                        )
    return rows


def write_outputs(rows: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "reddit_records.jsonl"
    csv_path = out_dir / "reddit_records.csv"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    fieldnames = [
        "source",
        "query",
        "subreddit",
        "thread_id",
        "record_type",
        "record_id",
        "url",
        "title",
        "created_utc",
        "author_hash",
        "score",
        "num_comments",
        "text",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--queries",
        nargs="+",
        default=[
            '"SAP S/4HANA" "RPA"',
            '"S/4HANA" "UiPath"',
            '"SAP migration" "bot"',
            '"SAP Fiori" "automation"',
        ],
    )
    parser.add_argument("--subreddits", nargs="+", default=["uipath", "rpa", "sap", "consulting", "sysadmin"])
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--out-dir", default="outputs")
    args = parser.parse_args()

    token = get_token(
        require_env("REDDIT_CLIENT_ID"),
        require_env("REDDIT_CLIENT_SECRET"),
        require_env("REDDIT_USER_AGENT"),
    )

    rows: list[dict[str, Any]] = []
    for query in args.queries:
        rows.extend(collect(query, args.subreddits, args.limit, token, require_env("REDDIT_USER_AGENT"), args.delay))

    write_outputs(rows, Path(args.out_dir))
    print(f"Wrote {len(rows)} Reddit records to {Path(args.out_dir).resolve()}")


if __name__ == "__main__":
    main()
