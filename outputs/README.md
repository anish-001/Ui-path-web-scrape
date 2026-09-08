# Dataset Guide: RPA Bot Adaptation after SAP S/4HANA Migration

This folder contains the datasets, thematic coding matrices, and statistical tables for the study on how SAP S/4HANA migrations impact Robotic Process Automation (UiPath) bot fleets.

---

## 1. How the CSV Files Connect

The files represent a 4-stage data pipeline, moving from **raw scraped forum posts** $\longrightarrow$ **thematic feature extraction** $\longrightarrow$ **thread-level aggregation** $\longrightarrow$ **final quantitative tables & case studies**:

```
[ 1. RAW FORUM POSTS ]
  uipath_forum_posts.csv (and .jsonl)
  • Raw text, timestamps, engagement metrics, and hashed usernames.
        │
        ▼ (src/prepare_theme_matrix.py)
[ 2. CODED THEMATIC MATRIX ]
  uipath_forum_theme_matrix.csv
  • Each post tagged with themes T1–T8 and SAP entity mention flags.
        │
        ▼ (src/build_paper_quant_tables.py)
[ 3. TOPIC-LEVEL AGGREGATION ]
  paper_topic_level_quantitative_data.csv
  • Posts rolled up by topic_id; scored for S/4HANA migration relevance (0–3).
        │
        ├────────────────────────────────┬────────────────────────────────┐
        ▼                                ▼                                ▼
[ 4A. THEME FREQUENCIES ]       [ 4B. CO-OCCURRENCE ]           [ 4C. QUALITATIVE CASES ]
  paper_theme_frequency_          paper_theme_                    UI_Path_Cases.csv
  table.csv                       cooccurrence_table.csv          • 15 curated incident
  • Prevalence % for              • Pairwise correlation            post-mortems with
    themes T1 through T8.           matrix showing which            verbatim quotes and
                                    problems compound.              verified fixes.
```

---

## 2. What Every CSV File Means

### Raw & Coded Post Data (Post Level)

* **`uipath_forum_posts.csv` (and `.jsonl`)**
  * **What it means:** The raw, unfiltered text of discussion posts scraped from the UiPath Community Forum via Discourse REST API.
  * **Key Columns:** `topic_id`, `post_id`, `created_at`, `author_hash` (SHA-256 anonymized username), `views`, `reply_count`, `like_count`, `text`.
  * **Purpose:** Acts as the primary empirical evidence base representing real-world developer discussions.

* **`uipath_forum_theme_matrix.csv`**
  * **What it means:** A 1-to-1 extension of `uipath_forum_posts.csv` with automated NLP keyword coding and technology tags added.
  * **Key Columns:** All columns from above, plus `word_count`, `mentions_*` (`s4hana`, `fiori`, `sap_gui`, `uipath`), `T1_ui_selector_breakage` through `T8_strategy_decision` (binary `1` or `0`), and `suggested_theme_count`.
  * **Purpose:** Converts unstructured human dialogue into structured binary variables for quantitative analysis.

---

### Aggregated & Statistical Data (Topic & Corpus Level)

* **`paper_topic_level_quantitative_data.csv`**
  * **What it means:** Discussion posts aggregated into complete thread units, treating the entire multi-turn dialogue as a single unit of analysis.
  * **Key Columns:** `topic_id`, `title`, `url`, `first_record_date`, `post_count_in_scrape`, `views`, `reply_count`, `relevance_score` (0 = off-topic, 1 = general context, 2 = technical context, 3 = direct migration), `relevance_category`, `active_themes`, `T1`..`T8`.
  * **Purpose:** Preserves conversational context (from symptom to root-cause diagnosis to resolution) and filters out general forum chit-chat.

* **`paper_theme_frequency_table.csv`**
  * **What it means:** Macro summary table showing how frequently each theme appears across the corpus.
  * **Key Columns:** `theme_id`, `theme_name`, `post_level_count`, `post_level_percent`, `topic_level_count`, `topic_level_percent`, `relevant_topic_count`, `relevant_topic_percent`, `direct_migration_topic_count`, `direct_migration_topic_percent`.
  * **Purpose:** Provides hard statistical percentages for your paper (e.g., proving that UI Breakage and Data Model Changes account for over 60% of all migration discussions).

* **`paper_theme_cooccurrence_table.csv`**
  * **What it means:** A 2-way matrix measuring which failure themes appear together in the same discussions.
  * **Key Columns:** `theme_a`, `theme_b`, `topic_count`, `topic_percent`.
  * **Purpose:** Statistically proves compounding problems—such as demonstrating that superficial UI Breakage ($T1$) co-occurs with major Adaptation Effort ($T5$) in 68% of threads.

---

### Qualitative & Methodological References

* **`UI_Path_Cases.csv`**
  * **What it means:** 15 curated incident vignettes from `forum.uipath.com` capturing specific real-world migration failures.
  * **Key Columns:** `case_id`, `title`, `url`, `date_posted`, `replies`, `views`, `category`, `key_failure_mode`, `resolution`, `quote`.
  * **Purpose:** Provides the qualitative ground truth, technical root causes (e.g., GUI 760 `aaname` breaks, `SAP_NCo` connector hangs, `RZ11` parameter resets), and verified developer fixes.

* **`rpa_s4hana_thematic_codebook.csv`**
  * **What it means:** The research codebook defining the rules and criteria for coding themes $T1$ through $T8$.
  * **Key Columns:** `theme_id`, `theme_name`, `definition`, `include_when`, `exclude_when`, `example_indicators`, `quant_variables`.
  * **Purpose:** Ensures academic rigor and auditability, allowing reviewers to verify the classification rules.
