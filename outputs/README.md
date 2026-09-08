# Dataset Guide: RPA Bot Adaptation after SAP S/4HANA Migration

This folder contains the datasets, thematic coding matrices, and statistical tables for the study on how SAP S/4HANA migrations impact Robotic Process Automation (UiPath) bot fleets.

---

## 1. How the CSV Files Connect

```
[ 1A. RAW FORUM POSTS ]               [ 1B. KEYWORD RULES / CODEBOOK ]
  uipath_forum_posts.csv (and .jsonl)   rpa_s4hana_thematic_codebook.csv
  • What people wrote on the forum      • Rules and keywords derived from
    (raw text, views, timestamps).        existing research (T1–T8).
         │                                       │
         └───────────────────┬───────────────────┘
                             ▼ (src/prepare_theme_matrix.py)
                   [ 2. TAGGED POSTS MATRIX ]
                     uipath_forum_theme_matrix.csv
                     • Raw posts tagged with 1 or 0
                       when a keyword rule matches.
                             │
                             ▼ (src/build_paper_quant_tables.py)
                   [ 3. THREAD-LEVEL SUMMARY ]
                     paper_topic_level_quantitative_data.csv
                     • All replies grouped back into single
                       conversation threads.
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
         [ 4A. FINAL PERCENTAGES ]   [ 4B. PROBLEMS TOGETHER ]
           paper_theme_frequency_      paper_theme_cooccurrence_
           table.csv                   table.csv
           • What % of discussions     • Which problems happen at
             complained about each       the exact same time
             problem.                    (e.g., UI breaks + heavy rework).
```

---

## 2. What Every CSV File Means

### Stage 1: The Inputs
* **`uipath_forum_posts.csv` (and `.jsonl`)**
  * **Plain English:** The raw messages and comments downloaded directly from the UiPath Community Forum.
  * **What it has:** Post text, views, reply counts, dates, and anonymized user IDs.
  * **Role:** The real-world evidence of developer discussions.

* **`rpa_s4hana_thematic_codebook.csv`**
  * **Plain English:** The rulebook (or dictionary) that defines what keywords to look for.
  * **What it has:** Definitions and search keywords for each problem category ($T1$ through $T8$), derived from prior research.
  * **Role:** Tells the computer *how* to categorize forum posts.

---

### Stage 2: Behind-the-Scenes Math (Intermediate)
* **`uipath_forum_theme_matrix.csv`**
  * **Plain English:** The raw messages with checkmarks (`1` or `0`) added whenever a keyword matched.
  * **What it has:** Every post plus binary flags for $T1$ through $T8$ and mentions of SAP GUI or Fiori.
  * **Role:** Intermediate spreadsheet that turns unstructured text into math.

* **`paper_topic_level_quantitative_data.csv`**
  * **Plain English:** Recombines back-and-forth replies into complete forum threads.
  * **What it has:** One row per discussion thread, with overall relevance scores and active problem themes.
  * **Role:** Intermediate calculation step to keep problem symptoms, diagnoses, and solutions linked together.

---

### Stage 3: Final Results (What Goes in Your Paper / Presentation)
* **`paper_theme_frequency_table.csv`**
  * **Plain English:** The scorecard showing what percentage of discussions complained about each problem.
  * **What it has:** Total counts and percentages for each theme across all posts and topics.
  * **Role:** The core statistics for your results section (e.g., UI Breakage is the #1 issue at over 50%).

* **`paper_theme_cooccurrence_table.csv`**
  * **Plain English:** The correlation card showing which problems trigger each other.
  * **What it has:** Pairwise percentages showing how often Theme A and Theme B appear in the same thread.
  * **Role:** Proves that superficial UI errors directly lead to major engineering adaptation efforts.
