# RPA Bot Adaptation After SAP S/4HANA Migration: Scraping and Thematic Analysis Method

## Research focus

Use forum and case-study text to quantify recurring adaptation problems and responses after SAP S/4HANA migration:

- What breaks in existing RPA bots after S/4HANA/Fiori migration?
- Which adaptation methods are discussed most often?
- Which issues are associated with measurable operational impact?
- Do community discussions differ from vendor/forum case material?

## Recommended data sources

Use API-style access where possible:

- UiPath Community Forum: Discourse JSON endpoints such as `/search.json` and `/t/{slug}/{id}.json`.
- Reddit: official Reddit OAuth API only. Avoid raw scraping and respect rate limits and API terms.
- RPA/SAP case studies: collect only pages with permission to crawl, then extract metadata and short analytic fields rather than republishing full text.

## Search query seed set

Start broad, then narrow after inspecting the first 50-100 records:

- `"SAP S/4HANA" "UiPath"`
- `"S/4HANA" "RPA"`
- `"SAP migration" "bot"`
- `"SAP Fiori" "automation"`
- `"SAP GUI" "UiPath" "migration"`
- `"selector" "SAP" "UiPath"`
- `"OData" "UiPath" "SAP"`
- `"BAPI" "UiPath" "S/4HANA"`
- `"RPA CoE" "SAP migration"`

## Data fields to capture

Minimum fields:

- `source`, `query`, `url`, `title`, `created_at`
- `record_type`: post, comment, case-study paragraph, forum reply
- `author_hash`: hashed username, not the raw username
- `score`, `reply_count`, `views`, `like_count` where available
- `text`

Derived quantitative fields:

- `word_count`
- `mentions_s4hana`, `mentions_fiori`, `mentions_uipath`, `mentions_sap_gui`
- `theme_T1` through `theme_T8`
- `impact_metric_present`
- `adaptation_strategy`
- `business_impact_direction`: positive, negative, mixed, none

## Thematic analysis workflow

1. Collect records with the scripts in `work/`.
2. Remove duplicates by URL plus normalized text hash.
3. Exclude irrelevant records that mention SAP or RPA but not bot adaptation, migration, breakage, remediation, testing, or operational impact.
4. Manually code a pilot sample of 50-100 records using `rpa_s4hana_thematic_codebook.csv`.
5. Revise the codebook after pilot coding.
6. Code the full dataset manually, with assisted keyword suggestions if needed.
7. Quantify theme frequency, source differences, co-occurrence, and impact mentions.
8. Report with representative paraphrases, not large copied forum excerpts.

## Example analysis outputs

- Frequency table: themes by source.
- Co-occurrence matrix: breakage themes vs adaptation methods.
- Timeline: posts by month around migration-related terms.
- Impact table: counts of downtime, rework, SLA, cost, hours saved.
- Strategy split: refactor vs rebuild vs retire vs move to API.

## Run commands

UiPath forum:

```bash
python3 work/uipath_forum_collector.py --pages 2 --delay 2.0 --out-dir outputs
```

Reddit:

```bash
export REDDIT_CLIENT_ID="..."
export REDDIT_CLIENT_SECRET="..."
export REDDIT_USER_AGENT="rpa-s4hana-research/0.1 by your_reddit_username"
python3 work/reddit_api_collector.py --limit 25 --delay 2.0 --out-dir outputs
```

## Ethics and compliance notes

- Do not bypass logins, paywalls, robots.txt, API limits, or anti-scraping controls.
- Store usernames as hashes unless you have a reason and permission to identify people.
- Keep quotations short and necessary; paraphrase for reporting.
- Reddit's Data API Terms restrict use and require compliance with their API access rules. Do not use Reddit content for AI model training without the rights required by Reddit and the content owners.
