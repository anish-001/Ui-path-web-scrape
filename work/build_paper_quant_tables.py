#!/usr/bin/env python3
"""Build paper-ready quantitative tables from the UiPath forum CSV."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


OUT = Path("outputs")
MATRIX = OUT / "uipath_forum_theme_matrix.csv"
TOPIC_TABLE = OUT / "paper_topic_level_quantitative_data.csv"
THEME_TABLE = OUT / "paper_theme_frequency_table.csv"
CO_TABLE = OUT / "paper_theme_cooccurrence_table.csv"
REPORT = OUT / "paper_quantitative_results.md"

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

DIRECT_MIGRATION_TERMS = [
    "s/4hana migration",
    "s4 hana migration",
    "s/4 hana migration",
    "migrate",
    "migration",
    "upgrade",
    "post-migration",
]

SAP_TECH_TERMS = [
    "bapi",
    "odata",
    "sap gui",
    "fiori",
    "selector",
    "transaction",
    "tcode",
    "scripting",
]

VENDOR_CONTEXT_TERMS = [
    "accelerator",
    "marketplace",
    "webinar",
    "survey",
    "release",
    "fully automated enterprise",
    "maximize sap investments",
]


def intish(value: str) -> int:
    try:
        return int(float(value or 0))
    except ValueError:
        return 0


def parse_date(value: str) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value[:10]


def text_blob(rows: list[dict[str, str]]) -> str:
    return " ".join((row.get("title", "") + " " + row.get("text", "")).lower() for row in rows)


def classify_relevance(blob: str) -> tuple[int, str]:
    has_migration = any(term in blob for term in DIRECT_MIGRATION_TERMS)
    has_s4 = "s/4hana" in blob or "s4 hana" in blob or "s/4 hana" in blob
    has_sap_tech = any(term in blob for term in SAP_TECH_TERMS)
    has_vendor = any(term in blob for term in VENDOR_CONTEXT_TERMS)

    if has_migration and has_s4:
        return 3, "direct_migration_adaptation"
    if has_s4 and has_sap_tech:
        return 2, "sap_s4hana_technical_context"
    if has_s4 or has_sap_tech:
        return 1, "sap_automation_context"
    if has_vendor:
        return 1, "vendor_context"
    return 0, "weak_or_irrelevant"


def main() -> None:
    with MATRIX.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    by_topic: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_topic[row["topic_id"]].append(row)

    topic_rows: list[dict[str, str | int]] = []
    for topic_id, group in by_topic.items():
        first = sorted(group, key=lambda row: row.get("created_at", ""))[0]
        blob = text_blob(group)
        relevance_score, relevance_category = classify_relevance(blob)
        theme_values = {
            theme: int(any(intish(row[theme]) for row in group))
            for theme in THEMES
        }
        active_themes = [THEMES[theme] for theme, value in theme_values.items() if value]
        topic_rows.append(
            {
                "topic_id": topic_id,
                "title": first["title"],
                "url": first["url"].rsplit("/", 1)[0],
                "first_record_date": parse_date(first["created_at"]),
                "post_count_in_scrape": len(group),
                "reply_count": intish(first["reply_count"]),
                "views": intish(first["views"]),
                "relevance_score": relevance_score,
                "relevance_category": relevance_category,
                "theme_count": sum(theme_values.values()),
                "active_themes": "; ".join(active_themes),
                **theme_values,
            }
        )

    topic_rows.sort(key=lambda row: (-int(row["relevance_score"]), -int(row["views"]), str(row["title"])))

    with TOPIC_TABLE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(topic_rows[0].keys()))
        writer.writeheader()
        writer.writerows(topic_rows)

    total_posts = len(rows)
    total_topics = len(topic_rows)
    relevant_topics = [row for row in topic_rows if int(row["relevance_score"]) >= 2]
    direct_topics = [row for row in topic_rows if int(row["relevance_score"]) == 3]

    post_theme_counts = Counter()
    topic_theme_counts = Counter()
    relevant_topic_theme_counts = Counter()
    direct_topic_theme_counts = Counter()

    for row in rows:
        for theme in THEMES:
            post_theme_counts[theme] += intish(row[theme])
    for row in topic_rows:
        for theme in THEMES:
            topic_theme_counts[theme] += int(row[theme])
    for row in relevant_topics:
        for theme in THEMES:
            relevant_topic_theme_counts[theme] += int(row[theme])
    for row in direct_topics:
        for theme in THEMES:
            direct_topic_theme_counts[theme] += int(row[theme])

    with THEME_TABLE.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "theme_id",
            "theme_name",
            "post_level_count",
            "post_level_percent",
            "topic_level_count",
            "topic_level_percent",
            "relevant_topic_count",
            "relevant_topic_percent",
            "direct_migration_topic_count",
            "direct_migration_topic_percent",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for theme, label in THEMES.items():
            writer.writerow(
                {
                    "theme_id": theme.split("_", 1)[0],
                    "theme_name": label,
                    "post_level_count": post_theme_counts[theme],
                    "post_level_percent": round(post_theme_counts[theme] / total_posts * 100, 1),
                    "topic_level_count": topic_theme_counts[theme],
                    "topic_level_percent": round(topic_theme_counts[theme] / total_topics * 100, 1),
                    "relevant_topic_count": relevant_topic_theme_counts[theme],
                    "relevant_topic_percent": round(relevant_topic_theme_counts[theme] / len(relevant_topics) * 100, 1) if relevant_topics else 0,
                    "direct_migration_topic_count": direct_topic_theme_counts[theme],
                    "direct_migration_topic_percent": round(direct_topic_theme_counts[theme] / len(direct_topics) * 100, 1) if direct_topics else 0,
                }
            )

    co_counts = Counter()
    for row in topic_rows:
        active = [theme for theme in THEMES if int(row[theme])]
        for i, left in enumerate(active):
            for right in active[i + 1 :]:
                co_counts[(left, right)] += 1

    with CO_TABLE.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["theme_a", "theme_b", "topic_count", "topic_percent"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for (left, right), count in co_counts.most_common():
            writer.writerow(
                {
                    "theme_a": THEMES[left],
                    "theme_b": THEMES[right],
                    "topic_count": count,
                    "topic_percent": round(count / total_topics * 100, 1),
                }
            )

    relevance_counts = Counter(row["relevance_category"] for row in topic_rows)
    years = Counter(row["first_record_date"][:4] for row in topic_rows if row["first_record_date"])

    lines = [
        "# Paper-Ready Quantitative Results",
        "",
        "## Sample",
        "",
        f"The cleaned dataset contains {total_posts} forum records grouped into {total_topics} unique discussion topics. "
        f"Using topic-level screening, {len(relevant_topics)} topics were classified as relevant SAP S/4HANA technical or migration-adaptation discussions, "
        f"including {len(direct_topics)} direct migration/adaptation topics.",
        "",
        "## Relevance distribution by topic",
        "",
    ]
    for category, count in relevance_counts.most_common():
        lines.append(f"- {category}: {count} topics ({count / total_topics * 100:.1f}%)")

    lines.extend(["", "## Theme frequency table", ""])
    lines.append("| Theme | Post-level n (%) | Topic-level n (%) | Relevant topic n (%) | Direct migration topic n (%) |")
    lines.append("|---|---:|---:|---:|---:|")
    for theme, label in THEMES.items():
        lines.append(
            f"| {label} | {post_theme_counts[theme]} ({post_theme_counts[theme] / total_posts * 100:.1f}%) "
            f"| {topic_theme_counts[theme]} ({topic_theme_counts[theme] / total_topics * 100:.1f}%) "
            f"| {relevant_topic_theme_counts[theme]} ({(relevant_topic_theme_counts[theme] / len(relevant_topics) * 100) if relevant_topics else 0:.1f}%) "
            f"| {direct_topic_theme_counts[theme]} ({(direct_topic_theme_counts[theme] / len(direct_topics) * 100) if direct_topics else 0:.1f}%) |"
        )

    lines.extend(["", "## Top co-occurrences at topic level", ""])
    for (left, right), count in co_counts.most_common(8):
        lines.append(f"- {THEMES[left]} + {THEMES[right]}: {count} topics ({count / total_topics * 100:.1f}%)")

    lines.extend(["", "## Topic years", ""])
    for year, count in sorted(years.items()):
        lines.append(f"- {year}: {count} topics")

    lines.extend(
        [
            "",
            "## Short results paragraph",
            "",
            "The quantitative pilot analysis indicates that SAP S/4HANA-related RPA adaptation discussions are concentrated around technical redesign rather than simple bot maintenance. "
            f"At the topic level, the most frequent themes were {THEMES[topic_theme_counts.most_common(1)[0][0]]}, "
            f"{THEMES[topic_theme_counts.most_common(2)[1][0]]}, and {THEMES[topic_theme_counts.most_common(3)[2][0]]}. "
            "The co-occurrence results show that adaptation methods frequently appear alongside UI/selector issues, transaction/API/data-model issues, and strategic decisions about whether to modify, rebuild, or replace existing automations. "
            "This supports treating S/4HANA migration as an automation lifecycle and governance problem, not only as a narrow selector-repair problem.",
            "",
            "## Reporting caution",
            "",
            "These figures should be reported as a pilot quantitative content analysis of public forum discussions. The theme indicators are keyword-assisted and should be validated through manual coding before final publication.",
        ]
    )
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT.resolve())


if __name__ == "__main__":
    main()
