#!/usr/bin/env python3
"""Build quantitative tables from Reddit theme-matrix CSV data."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


OUT = Path("outputs")
MATRIX = OUT / "reddit_theme_matrix.csv"
THREAD_TABLE = OUT / "reddit_thread_level_quantitative_data.csv"
THEME_TABLE = OUT / "reddit_theme_frequency_table.csv"
CO_TABLE = OUT / "reddit_theme_cooccurrence_table.csv"
REPORT = OUT / "reddit_quantitative_results.md"

THEMES = {
    "T1_ui_selector_breakage": "UI / selector breakage",
    "T2_data_model_transaction_change": "Data model / transaction change",
    "T3_auth_landscape_access": "Auth / landscape / access",
    "T4_timing_reliability": "Timing / reliability",
    "T5_adaptation_method": "Adaptation method",
    "T6_governance_change_management": "Governance / change management",
    "T7_business_impact": "Business impact",
    "T8_strategy_decision": "Strategy decision",
}

DIRECT_TERMS = [
    "s/4hana migration",
    "s4 hana migration",
    "s/4 hana migration",
    "sap migration",
    "migrate",
    "migration",
    "upgrade",
]

SAP_RPA_TERMS = [
    "uipath",
    "rpa",
    "bot",
    "automation",
    "sap gui",
    "fiori",
    "bapi",
    "odata",
    "selector",
]


def intish(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def utc_date(value: str) -> str:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).date().isoformat()
    except (TypeError, ValueError):
        return ""


def classify_relevance(blob: str) -> tuple[int, str]:
    has_direct = any(term in blob for term in DIRECT_TERMS)
    has_s4 = "s/4hana" in blob or "s4 hana" in blob or "s/4 hana" in blob
    has_sap_rpa = any(term in blob for term in SAP_RPA_TERMS)
    if has_direct and has_s4 and has_sap_rpa:
        return 3, "direct_s4hana_rpa_migration"
    if has_s4 and has_sap_rpa:
        return 2, "sap_s4hana_rpa_context"
    if has_sap_rpa:
        return 1, "sap_rpa_context"
    return 0, "weak_or_irrelevant"


def main() -> None:
    if not MATRIX.exists():
        raise SystemExit(
            "Missing outputs/reddit_theme_matrix.csv. Run reddit_api_collector.py, "
            "then prepare_theme_matrix.py on outputs/reddit_records.csv first."
        )

    with MATRIX.open(encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))

    if not records:
        raise SystemExit("outputs/reddit_theme_matrix.csv is empty.")

    by_thread: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        by_thread[record.get("thread_id", record.get("record_id", ""))].append(record)

    thread_rows: list[dict[str, str | int]] = []
    for thread_id, group in by_thread.items():
        first = sorted(group, key=lambda row: float(row.get("created_utc") or 0))[0]
        blob = " ".join((row.get("title", "") + " " + row.get("text", "")).lower() for row in group)
        relevance_score, relevance_category = classify_relevance(blob)
        theme_values = {
            theme: int(any(intish(row.get(theme, "0")) for row in group))
            for theme in THEMES
        }
        active_themes = [label for theme, label in THEMES.items() if theme_values[theme]]
        comments = [row for row in group if row.get("record_type") == "comment"]
        posts = [row for row in group if row.get("record_type") == "post"]
        thread_rows.append(
            {
                "thread_id": thread_id,
                "subreddit": first.get("subreddit", ""),
                "title": first.get("title", ""),
                "url": first.get("url", ""),
                "first_record_date": utc_date(first.get("created_utc", "")),
                "records_collected": len(group),
                "posts_collected": len(posts),
                "comments_collected": len(comments),
                "reddit_score": intish(first.get("score", "")),
                "reddit_num_comments": intish(first.get("num_comments", "")),
                "relevance_score": relevance_score,
                "relevance_category": relevance_category,
                "theme_count": sum(theme_values.values()),
                "active_themes": "; ".join(active_themes),
                **theme_values,
            }
        )

    thread_rows.sort(key=lambda row: (-int(row["relevance_score"]), -int(row["reddit_score"]), str(row["title"])))

    with THREAD_TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(thread_rows[0].keys()))
        writer.writeheader()
        writer.writerows(thread_rows)

    total_records = len(records)
    total_threads = len(thread_rows)
    relevant_threads = [row for row in thread_rows if int(row["relevance_score"]) >= 2]
    direct_threads = [row for row in thread_rows if int(row["relevance_score"]) == 3]

    record_theme_counts = Counter()
    thread_theme_counts = Counter()
    relevant_thread_theme_counts = Counter()
    direct_thread_theme_counts = Counter()
    for record in records:
        for theme in THEMES:
            record_theme_counts[theme] += intish(record.get(theme, "0"))
    for thread in thread_rows:
        for theme in THEMES:
            thread_theme_counts[theme] += int(thread[theme])
    for thread in relevant_threads:
        for theme in THEMES:
            relevant_thread_theme_counts[theme] += int(thread[theme])
    for thread in direct_threads:
        for theme in THEMES:
            direct_thread_theme_counts[theme] += int(thread[theme])

    with THEME_TABLE.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "theme_id",
            "theme_name",
            "record_level_count",
            "record_level_percent",
            "thread_level_count",
            "thread_level_percent",
            "relevant_thread_count",
            "relevant_thread_percent",
            "direct_thread_count",
            "direct_thread_percent",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for theme, label in THEMES.items():
            writer.writerow(
                {
                    "theme_id": theme.split("_", 1)[0],
                    "theme_name": label,
                    "record_level_count": record_theme_counts[theme],
                    "record_level_percent": round(record_theme_counts[theme] / total_records * 100, 1),
                    "thread_level_count": thread_theme_counts[theme],
                    "thread_level_percent": round(thread_theme_counts[theme] / total_threads * 100, 1),
                    "relevant_thread_count": relevant_thread_theme_counts[theme],
                    "relevant_thread_percent": round(relevant_thread_theme_counts[theme] / len(relevant_threads) * 100, 1) if relevant_threads else 0,
                    "direct_thread_count": direct_thread_theme_counts[theme],
                    "direct_thread_percent": round(direct_thread_theme_counts[theme] / len(direct_threads) * 100, 1) if direct_threads else 0,
                }
            )

    co_counts = Counter()
    for thread in thread_rows:
        active = [theme for theme in THEMES if int(thread[theme])]
        for i, left in enumerate(active):
            for right in active[i + 1 :]:
                co_counts[(left, right)] += 1

    with CO_TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["theme_a", "theme_b", "thread_count", "thread_percent"])
        writer.writeheader()
        for (left, right), count in co_counts.most_common():
            writer.writerow(
                {
                    "theme_a": THEMES[left],
                    "theme_b": THEMES[right],
                    "thread_count": count,
                    "thread_percent": round(count / total_threads * 100, 1),
                }
            )

    subreddit_counts = Counter(row["subreddit"] for row in thread_rows)
    relevance_counts = Counter(row["relevance_category"] for row in thread_rows)

    lines = [
        "# Reddit Quantitative Results",
        "",
        "## Sample",
        "",
        f"The Reddit dataset contains {total_records} collected records grouped into {total_threads} unique threads. "
        f"{len(relevant_threads)} threads were classified as relevant SAP S/4HANA/RPA context, including {len(direct_threads)} direct migration threads.",
        "",
        "## Subreddit coverage",
        "",
    ]
    for subreddit, count in subreddit_counts.most_common():
        lines.append(f"- r/{subreddit}: {count} threads")

    lines.extend(["", "## Relevance distribution", ""])
    for category, count in relevance_counts.most_common():
        lines.append(f"- {category}: {count} threads ({count / total_threads * 100:.1f}%)")

    lines.extend(["", "## Theme frequency table", ""])
    lines.append("| Theme | Record-level n (%) | Thread-level n (%) | Relevant thread n (%) | Direct thread n (%) |")
    lines.append("|---|---:|---:|---:|---:|")
    for theme, label in THEMES.items():
        lines.append(
            f"| {label} | {record_theme_counts[theme]} ({record_theme_counts[theme] / total_records * 100:.1f}%) "
            f"| {thread_theme_counts[theme]} ({thread_theme_counts[theme] / total_threads * 100:.1f}%) "
            f"| {relevant_thread_theme_counts[theme]} ({(relevant_thread_theme_counts[theme] / len(relevant_threads) * 100) if relevant_threads else 0:.1f}%) "
            f"| {direct_thread_theme_counts[theme]} ({(direct_thread_theme_counts[theme] / len(direct_threads) * 100) if direct_threads else 0:.1f}%) |"
        )

    lines.extend(["", "## Top co-occurrences", ""])
    for (left, right), count in co_counts.most_common(8):
        lines.append(f"- {THEMES[left]} + {THEMES[right]}: {count} threads ({count / total_threads * 100:.1f}%)")

    lines.extend(
        [
            "",
            "## Reporting caution",
            "",
            "These Reddit figures should be reported as an API-based pilot content analysis. Reddit discussions may be sparse for niche enterprise topics, so Reddit is best used as a comparison source against the UiPath forum rather than as the main evidence base unless the collected sample is large enough.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT.resolve())


if __name__ == "__main__":
    main()
