# Jadu Multimodal AI Engineer Challenge

## Table of Contents

- [Overview](#overview)
- [Repository Structure](#repository-structure)
- [Setup](#setup)
- [How to Run](#how-to-run)
  - [Step 1: Quick Data Exploration](#step-1-quick-data-exploration)
  - [Step 2: Full Analysis](#step-2-full-analysis)
  - [Step 3: Pull Extra Job Details (optional)](#step-3-pull-extra-job-details-optional)
- [What the Analysis Covers](#what-the-analysis-covers)
- [Submission](#submission)

## Overview

This repository contains my submission for the Jadu Multimodal AI Engineer Challenge. The challenge involves auditing QA data from Jadu's image and video generation pipeline, identifying weaknesses in the current evaluation system, and proposing a V2 workflow with improved prompting, evaluation, and regression testing.

## Repository Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── data/
│   ├── qc_results.json                # Image generation QA logs (8,111 entries)
│   └── qc_results_video.json          # Video generation QA logs (4,141 entries)
├── requirements/
│   └── Jadu Multimodal AI Engineer Challenge.pdf   # Challenge brief
├── explore.py                         # Quick data exploration script
├── extra_details.py                   # Pulls specific job details for walkthroughs
├── analysis.py                        # Main analysis script (generates all findings)
├── analysis_output/
│   ├── full_analysis.txt              # Complete terminal output from analysis.py
│   ├── findings_report.md             # Structured findings used to write the memo
│   ├── appendix_table.md              # Appendix table of reviewed jobIds
│   └── appendix_full_details.json     # Full JSON details for each reviewed job
├── submission/
│   └── memo.md                        # Final submission memo (Sections 0–3 + Appendix)
└── venv/                              # Python virtual environment
```

## Setup

### Prerequisites

- Python 3.8+

### Installation

```bash
# 1. Clone or navigate to the project directory
cd jadu-multimodal-ai-challenge

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 4. Install required libraries
pip install -r requirements.txt
```

### Required Libraries

| Library | Purpose |
|---------|---------|
| `pandas` | DataFrame operations for score distributions, per-model analysis, cross-tabs |
| `numpy` | Numeric handling (NaN scores, statistical aggregations) |

All other imports (`json`, `os`, `re`, `collections`, `datetime`) are Python standard library.

## How to Run

### Step 1: Quick Data Exploration

Get basic stats — entry counts, model lists, score distributions, sample entries:

```bash
python3 explore.py
```

### Step 2: Full Analysis

Run the comprehensive analysis that generates all findings, inconsistency detection, per-model rankings, retry patterns, regression candidates, and the appendix:

```bash
python3 analysis.py
```

Output is printed to the terminal. To save it to a file:

```bash
python3 analysis.py > analysis_output/full_analysis.txt 2>&1
```

This produces the following in `analysis_output/`:
- `full_analysis.txt` — Complete 962-line analysis output
- `appendix_table.md` — Markdown table of 9 reviewed jobIds
- `appendix_full_details.json` — Full JSON for each reviewed job
- `findings_report.md` — Structured findings organized by memo section

### Step 3: Pull Extra Job Details (optional)

Fetch specific job details for the Section 2 creative walkthroughs (fantastical scenes, action videos, multi-character compositing):

```bash
python3 extra_details.py
```

## What the Analysis Covers

| Analysis | Script | Key Output |
|----------|--------|------------|
| Data quality overview (scores, statuses, coverage) | `analysis.py` | Section 1 of memo |
| Score mapping (`qaScore` → `qaTransformedScore`) | `analysis.py` | Non-deterministic mapping discovery |
| Per-model quality rankings | `analysis.py` | Model selection evidence for Section 2 |
| QA inconsistency detection (high score + bad feedback) | `analysis.py` | 157 image + 64 video disagreements |
| Retry pattern analysis (same prompt, multiple attempts) | `analysis.py` | Retry strategy evidence |
| Rewritten prompt comparison (original vs. rewrite) | `analysis.py` | Prompt enrichment insights |
| Regression test candidate identification | `analysis.py` | 15 regression test cases |
| Feedback dimension & failure mode frequency | `analysis.py` | Common failure patterns |

## Submission

The final deliverable is **`submission/memo.md`**, which contains:

- **Section 0:** Relevant hands-on experience
- **Section 1:** Data audit with 4 image + 3 video job reviews (including 3 QA disagreements)
- **Section 2:** V2 workflow design with revised QA prompt, eval set, regression suite, and 2 creative walkthroughs
- **Section 3:** Metrics, thresholds, evaluation slices, drift detection, and release blockers
- **Appendix:** Table of 9 reviewed jobIds with conclusions
- **GenAI disclosure**
