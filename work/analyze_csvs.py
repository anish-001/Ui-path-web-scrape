#!/usr/bin/env python3
"""Summarize the RPA/S4HANA CSV outputs."""

from __future__ import annotations

import csv
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path("outputs")
MATRIX = ROOT / "uipath_forum_theme_matrix.csv"
REPORT = ROOT / "csv_analysis_summary.md"

THEME_LABELS = {
    "T1_ui_selector_breakage": "UI / selector breakage",
    "T2_data_model_transaction_change": "Data model / transaction change",
    "T3_auth_landscape_access": "Auth / landscape / access",
    "T4_timing_reliability": "Timing / reliability",
    "T5_adaptation_method": "Adaptation method",
    "T6_governance_change_management": "Governance / change management",
    "T7_business_impact": "Business impact",
    "T8_strategy_decision": "Strategy decision",
}


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def intish(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def main() -> None:
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    theme_cols = list(THEME_LABELS)
    topic_ids = {row["topic_id"] for row in rows}
    post_ids = [row["post_id"] for row in rows]
    urls = [row["url"] for row in rows]
    titles = Counter(row["title"] for row in rows)
    dates = [date for date in (parse_date(row["created_at"]) for row in rows) if date]
    word_counts = [intish(row["word_count"]) for row in rows]

    theme_counts = Counter()
    for row in rows:
        for col in theme_cols:
            theme_counts[col] += intish(row[col])

    cooccurrence = Counter()
    for row in rows:
        active = [col for col in theme_cols if intish(row[col])]
        for i, left in enumerate(active):
            for right in active[i + 1 :]:
                cooccurrence[(left, right)] += 1

    month_counts = Counter()
    for date in dates:
        month_counts[date.strftime("%Y-%m")] += 1

    high_signal = sorted(
        rows,
        key=lambda row: (
            intish(row["suggested_theme_count"]),
            intish(row["views"]),
            intish(row["reply_count"]),
            intish(row["like_count"]),
        ),
        reverse=True,
    )[:8]

    source_query_counts = Counter(row["query"] for row in rows)

    lines = [
        "# CSV Analysis Summary",
        "",
        "## Dataset shape",
        "",
        f"- Records: {len(rows)}",
        f"- Unique topics: {len(topic_ids)}",
        f"- Unique post IDs: {len(set(post_ids))}",
        f"- Unique URLs: {len(set(urls))}",
        f"- Duplicate post IDs: {len(post_ids) - len(set(post_ids))}",
        f"- Date range: {min(dates).date() if dates else 'n/a'} to {max(dates).date() if dates else 'n/a'}",
        f"- Median word count: {statistics.median(word_counts) if word_counts else 0}",
        f"- Mean word count: {round(statistics.mean(word_counts), 1) if word_counts else 0}",
        "",
        "## Theme frequencies",
        "",
    ]

    for theme, count in theme_counts.most_common():
        pct = count / len(rows) * 100 if rows else 0
        lines.append(f"- {THEME_LABELS[theme]}: {count} records ({pct:.1f}%)")

    lines.extend(["", "## Strongest theme co-occurrences", ""])
    for (left, right), count in cooccurrence.most_common(10):
        lines.append(f"- {THEME_LABELS[left]} + {THEME_LABELS[right]}: {count}")

    lines.extend(["", "## Query coverage", ""])
    for query, count in source_query_counts.most_common():
        lines.append(f"- `{query}`: {count} records")

    lines.extend(["", "## Records by month", ""])
    for month, count in sorted(month_counts.items()):
        lines.append(f"- {month}: {count}")

    lines.extend(["", "## Most repeated titles", ""])
    for title, count in titles.most_common(8):
        lines.append(f"- {count}x: {title}")

    lines.extend(["", "## High-signal records for manual review", ""])
    for row in high_signal:
        title = row["title"].replace("\n", " ").strip()
        themes = [
            THEME_LABELS[col]
            for col in theme_cols
            if intish(row[col])
        ]
        lines.append(
            f"- {title} | themes: {', '.join(themes)} | views: {row['views']} | replies: {row['reply_count']} | {row['url']}"
        )

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT.resolve())


if __name__ == "__main__":
    main()
