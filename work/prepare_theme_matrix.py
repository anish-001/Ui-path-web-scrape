#!/usr/bin/env python3
"""
Add keyword-based theme suggestion columns to scraped forum/API records.

Use the output as a coding aid, not as final qualitative coding. The point is to
make the first quantitative pass reproducible before manual thematic analysis.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


THEME_KEYWORDS = {
    "T1_ui_selector_breakage": [
        r"\bselector\b",
        r"\banchor\b",
        r"\bclick\b",
        r"\bbutton\b",
        r"\bscreen\b",
        r"\blayout\b",
        r"\bfiori\b",
        r"\bsap gui\b",
        r"\bcomputer vision\b",
    ],
    "T2_data_model_transaction_change": [
        r"\btable\b",
        r"\bfield\b",
        r"\btransaction\b",
        r"\btcode\b",
        r"\bbapi\b",
        r"\bodata\b",
        r"\bapi\b",
        r"\bdata model\b",
    ],
    "T3_auth_landscape_access": [
        r"\bsso\b",
        r"\bmfa\b",
        r"\blogin\b",
        r"\bauthori[sz]ation\b",
        r"\brole\b",
        r"\bcredential\b",
        r"\bcertificate\b",
        r"\bdev\b",
        r"\bqas\b",
        r"\bprd\b",
    ],
    "T4_timing_reliability": [
        r"\btimeout\b",
        r"\blatency\b",
        r"\bslow\b",
        r"\bwait\b",
        r"\bretry\b",
        r"\bqueue\b",
        r"\bfail(?:ed|ure)?\b",
        r"\bintermittent\b",
    ],
    "T5_adaptation_method": [
        r"\brebuild\b",
        r"\brefactor\b",
        r"\bfix\b",
        r"\bworkaround\b",
        r"\btest\b",
        r"\bmonitor\b",
        r"\bexception\b",
        r"\borchestrator\b",
        r"\bregression\b",
    ],
    "T6_governance_change_management": [
        r"\bcoe\b",
        r"\bcenter of excellence\b",
        r"\buat\b",
        r"\bhypercare\b",
        r"\bchange management\b",
        r"\brelease\b",
        r"\bsignoff\b",
        r"\binventory\b",
    ],
    "T7_business_impact": [
        r"\bhours?\b",
        r"\bcost\b",
        r"\bsla\b",
        r"\bdowntime\b",
        r"\bbacklog\b",
        r"\bproductivity\b",
        r"\baccuracy\b",
        r"\bsav(?:e|ed|ings)\b",
    ],
    "T8_strategy_decision": [
        r"\bretire\b",
        r"\breplace\b",
        r"\bmigrate\b",
        r"\bredesign\b",
        r"\bfrom scratch\b",
        r"\bapi-first\b",
        r"\bkeep\b",
    ],
}


def present(patterns: list[str], text: str) -> int:
    return int(any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open(encoding="utf-8", newline="") as in_handle:
        reader = csv.DictReader(in_handle)
        fieldnames = list(reader.fieldnames or [])
        new_fields = [
            "word_count",
            "mentions_s4hana",
            "mentions_fiori",
            "mentions_uipath",
            "mentions_sap_gui",
            *THEME_KEYWORDS.keys(),
            "suggested_theme_count",
        ]
        with output_path.open("w", encoding="utf-8", newline="") as out_handle:
            writer = csv.DictWriter(out_handle, fieldnames=fieldnames + new_fields)
            writer.writeheader()
            for row in reader:
                text = " ".join([row.get("title", ""), row.get("text", "")])
                additions = {
                    "word_count": len(re.findall(r"\w+", row.get("text", ""))),
                    "mentions_s4hana": present([r"\bs/4hana\b", r"\bs4hana\b"], text),
                    "mentions_fiori": present([r"\bfiori\b"], text),
                    "mentions_uipath": present([r"\buipath\b"], text),
                    "mentions_sap_gui": present([r"\bsap gui\b"], text),
                }
                theme_hits = {
                    theme: present(patterns, text)
                    for theme, patterns in THEME_KEYWORDS.items()
                }
                additions.update(theme_hits)
                additions["suggested_theme_count"] = sum(theme_hits.values())
                writer.writerow({**row, **additions})

    print(f"Wrote theme matrix to {output_path.resolve()}")


if __name__ == "__main__":
    main()
