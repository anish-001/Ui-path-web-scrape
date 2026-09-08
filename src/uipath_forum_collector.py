#!/usr/bin/env python3
"""
Collect public UiPath Community Forum discussions via Discourse JSON endpoints.

This script is intended for small-scale academic/research collection. Check the
forum's robots.txt and terms before running, keep delays conservative, and avoid
collecting private or sensitive information.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import ssl
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


BASE_URL = "https://forum.uipath.com"
USER_AGENT = "rpa-s4hana-research/0.1 academic-contact"


try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return re.sub(r"\s+", " ", html.unescape(" ".join(self.parts))).strip()


def get_json(url: str, delay: float) -> Any:
    time.sleep(delay)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))


def clean_html(cooked: str) -> str:
    parser = TextExtractor()
    parser.feed(cooked or "")
    return parser.text()


def anonymize(value: str) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def search_topics(query: str, pages: int, delay: float) -> list[dict[str, Any]]:
    topics: dict[int, dict[str, Any]] = {}
    encoded = urllib.parse.quote(query)
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/search.json?q={encoded}&page={page}"
        payload = get_json(url, delay)
        for topic in payload.get("topics", []):
            topic_id = topic.get("id")
            if topic_id is not None:
                topics[int(topic_id)] = topic
    return list(topics.values())


def topic_posts(topic: dict[str, Any], query: str, delay: float) -> list[dict[str, Any]]:
    slug = topic.get("slug") or "topic"
    topic_id = topic["id"]
    url = f"{BASE_URL}/t/{slug}/{topic_id}.json"
    payload = get_json(url, delay)
    rows: list[dict[str, Any]] = []
    for post in payload.get("post_stream", {}).get("posts", []):
        rows.append(
            {
                "source": "uipath_forum",
                "query": query,
                "topic_id": topic_id,
                "post_id": post.get("id"),
                "url": f"{BASE_URL}/t/{slug}/{topic_id}/{post.get('post_number', 1)}",
                "title": payload.get("title") or topic.get("title"),
                "created_at": post.get("created_at"),
                "author_hash": anonymize(post.get("username", "")),
                "reply_count": payload.get("reply_count"),
                "views": payload.get("views"),
                "like_count": post.get("like_count"),
                "text": clean_html(post.get("cooked", "")),
            }
        )
    return rows


def write_outputs(rows: list[dict[str, Any]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "uipath_forum_posts.jsonl"
    csv_path = out_dir / "uipath_forum_posts.csv"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    fieldnames = [
        "source",
        "query",
        "topic_id",
        "post_id",
        "url",
        "title",
        "created_at",
        "author_hash",
        "reply_count",
        "views",
        "like_count",
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
            '"SAP S/4HANA" "UiPath"',
            '"S/4HANA" "RPA"',
            '"SAP migration" "UiPath"',
            '"SAP Fiori" "UiPath"',
            '"SAP automation" "selector"',
        ],
    )
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--out-dir", default="outputs")
    args = parser.parse_args()

    all_rows: list[dict[str, Any]] = []
    seen_posts: set[int] = set()
    for query in args.queries:
        for topic in search_topics(query, args.pages, args.delay):
            for row in topic_posts(topic, query, args.delay):
                post_id = row.get("post_id")
                if post_id not in seen_posts:
                    all_rows.append(row)
                    if isinstance(post_id, int):
                        seen_posts.add(post_id)

    write_outputs(all_rows, Path(args.out_dir))
    print(f"Wrote {len(all_rows)} posts to {Path(args.out_dir).resolve()}")


if __name__ == "__main__":
    main()
