# RPA Bot Adaptation After SAP S/4HANA Migration: Research Data & Code Architecture

A reproducible research pipeline for harvesting, preprocessing, thematically coding, and quantitatively analyzing community discussions from the **UiPath Community Forum** regarding Robotic Process Automation (RPA) bot breakages, adaptations, and governance during SAP S/4HANA enterprise migrations.

---

## 1. Research Framework & Methodological Loop

This repository implements a **mixed-methods research design** that establishes a continuous feedback loop between qualitative case depth and large-scale quantitative forum analysis:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               METHODOLOGICAL TRIANGULATION FRAMEWORK                                   │
├──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┤
│        1. QUALITATIVE CASES      │     2. FORUM DATA (QUALITATIVE)  │    3. FORUM DATA (QUANTITATIVE)  │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ TOP ROW (Discovery & Completeness):                                                                    │
│ • Case Study:                    │ • Forum Data:                    │ • Forum Data (Quant):            │
│   Themes of things that change   │   Validate completeness          │   Macro prevalence & counts      │
│   (15 UI Path Cases)             │   (Discourse API Scrape)         │   (Frequency table %)            │
├──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┤
│ BOTTOM ROW (Mechanisms & Co-occurrence):                                                               │
│ • Forum Data:                    │ • Case Study:                    │ • Forum Data (Quant):            │
│   Themes of (more) things that   │   In-depth explanation of themes │   Co-occurrence correlations     │
│   change (Emergent topics)       │   (Root-cause incident profiles) │   (Pairwise problem matrix)      │
└──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 NARRATIVE ARC & INVESTIGATION FLOW                                     │
├──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┤
│ 1. Problem: RPA Changes Bad      │ 2. How RPA Changes Are Bad       │ 3. Solutions                     │
│    (ERP upgrade destabilizes     │    (Specific technical failure   │    (Headless API-first model,    │
│     automation substrate)        │     mechanisms & consequences)   │     Basis governance, triage)    │
└──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┘
```

### Why Scrape Public Practitioner Communities?
1. **The Corporate NDA Barrier:** Enterprise ERP transformations and critical automation failures are strictly protected by corporate NDAs. Organizations rarely publish detailed post-mortems documenting unexpected bot crashes, budget blowouts, or operational paralysis.
2. **Unfiltered Diagnostic Reality:** Technical developer forums (e.g., UiPath Community Forum) operate as real-time *"digital trading zones"* where RPA developers, enterprise architects, and SAP Basis administrators troubleshoot production fires without corporate PR or vendor marketing spin.
3. **Conversational Trajectory Analysis:** Multi-turn forum threads preserve the entire problem-solving arc: from initial surface symptoms (UI selector exceptions), to root-cause diagnosis (SAP Basis permissions, database table consolidations), to workaround debates, and final canonical solutions.

---

## 2. What Factors Were Scraped and Why?

The data collection harvested explicit metadata, conversational text, and technical indicators to convert qualitative discourse into quantitative metrics:

| Scraped Factor | Field Name(s) | Methodological Rationale ("Why Scraped") |
| :--- | :--- | :--- |
| **Relational Identifiers** | `topic_id`, `post_id` | **Preserves Conversational Thread Trajectory:** Technical troubleshooting is dialogic. Preserving parent topic and sequential reply IDs ensures we do not treat replies in isolation, allowing multi-level analysis (post-level vs. topic-level). |
| **Anonymized Identity** | `author_hash` | **Research Ethics & Participant Tracking:** Usernames are converted to 16-character SHA-256 hashes (`hashlib.sha256(username).hexdigest()[:16]`). This satisfies academic IRB and GDPR privacy requirements while still tracking unique contributors across threads. |
| **Temporal Timestamps** | `created_at` | **Mapping the Migration Wave:** Captures when discussions occurred (2020–2026) to analyze longitudinal trends coinciding with SAP’s announced ECC end-of-maintenance and peak S/4HANA migrations. |
| **Engagement Metrics** | `views`, `reply_count`, `like_count` | **Severity & Community Consensus Proxy:** Unanswered threads with 0 replies represent isolated queries, while threads with thousands of views and dozens of replies represent systemic enterprise bottlenecks. |
| **Conversational Content**| `title`, `text` | **NLP Feature Extraction & Quote Grounding:** Stripped of raw HTML code tags to produce clean text used for keyword matching, theme frequency classification, and verbatim citation. |
| **Architectural Entity Flags** | `mentions_s4hana`, `mentions_fiori`, `mentions_sap_gui`, `mentions_uipath` | **Substrate Layer Identification:** Identifies which layer of SAP architecture broke (e.g., whether the problem involves classic desktop SAP GUI vs. web-based SAP Fiori Launchpad). |
| **Text Volume** | `word_count` | **Diagnostic Depth Control:** Controls for post length in computational text analysis (filtering out one-line noise like *"thanks"* vs. rich 500-word error diagnoses). |

---

## 3. The 8-Theme Thematic Framework ($T1$ through $T8$)

The pipeline categorizes text into **8 core constructs ($T1$ through $T8$)** defined in [`outputs/rpa_s4hana_thematic_codebook.csv`](outputs/rpa_s4hana_thematic_codebook.csv):

| Theme ID | Construct Name | Definition & Failure Mechanism | Example Keyword Patterns |
| :--- | :--- | :--- | :--- |
| **T1** | **UI & Selector Breakage** | SAP S/4HANA, Fiori web, or GUI skin upgrades break UI selectors or element trees. | `selector`, `anchor`, `click`, `fiori`, `sap gui`, `computer vision`, `aaname` |
| **T2** | **Data Model & Transaction Change** | Deprecation of legacy transaction codes, table consolidation (`ACDOCA`), or BAPI/OData API shifts. | `table`, `field`, `transaction`, `tcode`, `bapi`, `odata`, `data model` |
| **T3** | **Auth, Landscape & Access** | Basis security parameters (`RZ11`), missing authorizations, SSO/MFA, or staging environment parity gaps. | `sso`, `mfa`, `login`, `authorization`, `role`, `credential`, `dev`, `qas`, `prd` |
| **T4** | **Timing & Reliability** | System latency, execution timeouts, scheduled batch session elimination, and lock collisions. | `timeout`, `latency`, `slow`, `wait`, `retry`, `queue`, `failed`, `intermittent` |
| **T5** | **Adaptation Method** | Concrete engineering remediations (refactoring, API rebuilds, fuzzy selectors, test suites). | `rebuild`, `refactor`, `fix`, `workaround`, `test`, `orchestrator`, `regression` |
| **T6** | **Governance & Change Mgmt** | CoE policies, UAT validation, hypercare coordination, and bot portfolio inventories. | `coe`, `center of excellence`, `uat`, `hypercare`, `change management`, `signoff` |
| **T7** | **Business Impact** | Quantified operational fallout: downtime, rework hours, SLA breaches, order backlogs, or ROI. | `hours`, `cost`, `sla`, `downtime`, `backlog`, `productivity`, `savings` |
| **T8** | **Strategy Decision** | Strategic triage: decisions to retire, retain, refactor, or completely rebuild automations. | `retire`, `replace`, `migrate`, `redesign`, `from scratch`, `api-first` |

---

## 4. How the CSV Files Connect (Data Lineage & Pipeline)

The repository processes data through a 4-stage pipeline from raw web harvest to publication-ready statistical tables:

```
[ forum.uipath.com ]
        │
        ▼ (work/uipath_forum_collector.py)
 1. uipath_forum_posts.csv          <── Raw text, views, and SHA-256 author hashes (Post Level)
        │
        ▼ (work/prepare_theme_matrix.py)
 2. uipath_forum_theme_matrix.csv   <── 1-to-1 extension adding word_count, entity flags, & T1–T8
        │
        ▼ (work/build_paper_quant_tables.py)
 3. paper_topic_level_quantitative_data.csv  <── Rolled up by topic_id with relevance scores (Topic Level)
        │
        ├────────────────────────────────────────┬────────────────────────────────────────┐
        ▼                                        ▼                                        ▼
 4. paper_theme_frequency_table.csv    5. paper_theme_cooccurrence_table.csv    6. UI Path Cases.csv
    (Corpus % for T1–T8)                  (Pairwise problem correlation matrix)     (15 qualitative case vignettes)
```

### Relational Schema

| File Name | Primary Key | Link Key | Granularity | Description & Role |
| :--- | :--- | :--- | :--- | :--- |
| **`uipath_forum_posts.csv`** | `post_id` | `topic_id` | Post / Reply | Raw scraped text, view counts, and SHA-256 hashed authors. |
| **`uipath_forum_theme_matrix.csv`** | `post_id` | `topic_id` | Post / Reply | 1-to-1 extension appending `word_count`, `mentions_*`, and binary indicators (`T1`–`T8`). |
| **`paper_topic_level_quantitative_data.csv`** | `topic_id` | `topic_id` | Topic / Thread | Roll-up aggregating all replies per thread, assigning thread relevance scores (0 to 3). |
| **`paper_theme_frequency_table.csv`** | `theme_id` | `theme_id` | Theme (`T1`–`T8`)| Macro summary table showing theme counts and % shares across posts and topics. |
| **`paper_theme_cooccurrence_table.csv`** | `theme_a, theme_b`| `theme_id` | Theme Pair | Pairwise frequency matrix showing which problem themes co-occur in the same discussions. |
| **`rpa_s4hana_thematic_codebook.csv`** | `theme_id` | `theme_id` | Theme (`T1`–`T8`)| Qualitative codebook containing academic definitions, inclusion/exclusion criteria. |
| **`UI Path Cases.csv`** | `case_id` | `url` $\to$ `topic_id` | Case Incident | 15 curated empirical case vignettes with verbatim quotes, specific failure modes, and fixes. |

---

## 5. Repository Directory Structure

```
├── .gitignore                   # Ignores __pycache__, .DS_Store, .env, and temp files
├── README.md                    # Research framework, methodology, data lineage, and guide
├── requirements.txt             # Python dependencies (certifi, pandas, tqdm, praw)
├── run_pipeline.py              # Master CLI orchestrator to run pipeline steps end-to-end
├── work/                        # Execution source scripts
│   ├── uipath_forum_collector.py       # Step 1: Scrapes forum topics & posts via Discourse API
│   ├── prepare_theme_matrix.py         # Step 2: Extracts features & codes themes T1-T8
│   ├── build_paper_quant_tables.py     # Step 3: Aggregates to topic level & builds tables
│   ├── analyze_csvs.py                 # Step 4: Computes dataset summary diagnostics
│   ├── reddit_api_collector.py         # Optional: Complementary Reddit scraper via PRAW
│   └── build_reddit_paper_quant_tables.py
└── outputs/                     # Generated data and markdown reports
    ├── uipath_forum_posts.csv          # Raw post corpus
    ├── uipath_forum_theme_matrix.csv   # Thematic feature matrix
    ├── paper_topic_level_quantitative_data.csv
    ├── paper_theme_frequency_table.csv
    ├── paper_theme_cooccurrence_table.csv
    ├── rpa_s4hana_thematic_codebook.csv
    ├── paper_quantitative_results.md
    ├── csv_analysis_summary.md
    └── csv_interpretive_analysis.md
```

---

## 6. How to Run the Pipeline

You can run the entire pipeline with a single command using the root orchestrator [`run_pipeline.py`](run_pipeline.py):

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the complete end-to-end pipeline (Steps 1-4)
python3 run_pipeline.py --all

# 3. Or run specific steps (e.g., analyze existing raw data without re-scraping)
python3 run_pipeline.py --step 2 3 4

# 4. Dry-run mode (preview execution steps without running)
python3 run_pipeline.py --dry-run
```

---

## 7. Git Commit Guide

To commit this structured repository into Git cleanly:

```bash
# Navigate to project directory
cd /Users/anishsanchith/Documents/Codex/2026-06-22/i-need-to-web-scrape-things

# Initialize git repository (if not already initialized)
git init

# Stage all files (.gitignore will automatically exclude caches and .DS_Store)
git add .

# Check staged files
git status

# Commit with a structured message
git commit -m "feat: complete research pipeline for RPA SAP S/4HANA migration thematic analysis"
```
