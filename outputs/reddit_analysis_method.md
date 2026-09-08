# Reddit Analysis Method

## Purpose

Use Reddit as a comparison source for public discussion around RPA, UiPath, SAP automation, and SAP S/4HANA migration. The UiPath Community Forum should remain the stronger primary source because it is more directly focused on RPA implementation cases.

## Collection approach

Use the official Reddit OAuth API through `work/reddit_api_collector.py`. Do not scrape Reddit pages directly. Reddit's Data API Terms require compliance with API access rules, rate limits, and restrictions on reuse of user content.

Suggested subreddits:

- `uipath`
- `rpa`
- `sap`
- `consulting`
- `sysadmin`

Suggested queries:

- `"SAP S/4HANA" "RPA"`
- `"S/4HANA" "UiPath"`
- `"SAP migration" "bot"`
- `"SAP Fiori" "automation"`
- `"SAP GUI" "UiPath"`
- `"BAPI" "UiPath" "SAP"`
- `"OData" "SAP" "automation"`

## Run sequence

```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USER_AGENT="rpa-s4hana-research/0.1 by your_reddit_username"

python3 work/reddit_api_collector.py --limit 25 --delay 2.0 --out-dir outputs
python3 work/prepare_theme_matrix.py --input outputs/reddit_records.csv --output outputs/reddit_theme_matrix.csv
python3 work/build_reddit_paper_quant_tables.py
```

## Expected outputs

- `outputs/reddit_records.csv`
- `outputs/reddit_theme_matrix.csv`
- `outputs/reddit_thread_level_quantitative_data.csv`
- `outputs/reddit_theme_frequency_table.csv`
- `outputs/reddit_theme_cooccurrence_table.csv`
- `outputs/reddit_quantitative_results.md`

## How to use it in the paper

Reddit should be framed as a secondary public-discussion dataset. Compare it against the UiPath forum by looking at:

- whether Reddit has fewer direct migration cases;
- whether Reddit discussions are more general and less implementation-specific;
- which themes overlap with UiPath forum themes;
- whether Reddit adds practitioner sentiment, risk perception, or external commentary.

Do not treat Reddit counts and UiPath forum counts as equivalent without explaining that the communities have different purposes and user populations.
