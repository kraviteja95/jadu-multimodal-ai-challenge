#!/usr/bin/env python3
"""
Jadu Multimodal AI Challenge — Comprehensive Data Analysis
===========================================================
This script analyzes qc_results.json (images) and qc_results_video.json (videos)
to surface insights for the challenge submission.

Outputs:
  - analysis_output/  directory with all results
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

import pandas as pd
import numpy as np

OUTPUT_DIR = "analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
print("=" * 70)
print("LOADING DATA")
print("=" * 70)

with open("data/qc_results.json") as f:
    img_raw = json.load(f)
with open("data/qc_results_video.json") as f:
    vid_raw = json.load(f)

print(f"Image entries: {len(img_raw)}")
print(f"Video entries: {len(vid_raw)}")


def safe_score(v):
    """Handle dict-type NaN scores from MongoDB export."""
    if isinstance(v, dict):
        return None
    return v


def parse_date(entry):
    """Extract datetime from MongoDB $date format."""
    try:
        d = entry.get("createdAt", {}).get("$date", "")
        return d[:19] if d else None
    except Exception:
        return None


def build_df(raw, media_type):
    """Convert raw JSON entries to a clean DataFrame."""
    rows = []
    for e in raw:
        row = {
            "jobId": e.get("jobId"),
            "createdAt": parse_date(e),
            "status": e.get("status"),
            "modelTitle": e.get("modelTitle", "?"),
            "modelId": e.get("modelId", "?"),
            "prompt": e.get("prompt") or "",
            "qaScore": safe_score(e.get("qaScore")),
            "qaTransformedScore": safe_score(e.get("qaTransformedScore")),
            "qaReasoning": e.get("qaReasoning", ""),
            "qaActionableFeedback": e.get("qaActionableFeedback", ""),
            "mediaType": media_type,
            "hasReferenceImages": bool(
                e.get("images") and any(x for x in e["images"] if x)
            ),
            "numReferenceImages": len(
                [x for x in (e.get("images") or []) if x]
            ),
            "promptLength": len(e.get("prompt") or ""),
        }
        if media_type == "video":
            row["qaRewrittenPrompt"] = e.get("qaRewrittenPrompt", "")
            row["outputVideo"] = e.get("outputVideo", "")
        else:
            row["outputImage"] = e.get("outputImage", "")
        rows.append(row)
    return pd.DataFrame(rows)


df_img = build_df(img_raw, "image")
df_vid = build_df(vid_raw, "video")

# Convert qaTransformedScore to numeric (handle string '4')
df_img["qaTransformedScore"] = pd.to_numeric(
    df_img["qaTransformedScore"], errors="coerce"
)
df_vid["qaTransformedScore"] = pd.to_numeric(
    df_vid["qaTransformedScore"], errors="coerce"
)

print(f"\nImage DF shape: {df_img.shape}")
print(f"Video DF shape: {df_vid.shape}")


# ─────────────────────────────────────────────
# 2. DATA QUALITY OVERVIEW
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("DATA QUALITY OVERVIEW")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    print(f"\n--- {name} ---")
    total = len(df)
    has_score = df["qaScore"].notna().sum()
    has_feedback = (df["qaActionableFeedback"].str.len() > 0).sum()
    has_reasoning = (df["qaReasoning"].str.len() > 0).sum()
    completed = (df["status"] == "completed").sum()
    failed = (df["status"] == "failed").sum()
    processing = (df["status"] == "processing").sum()
    cancelled = (df["status"] == "cancelled").sum()

    print(f"  Total: {total}")
    print(f"  Completed: {completed} ({100*completed/total:.1f}%)")
    print(f"  Failed: {failed} | Processing: {processing} | Cancelled: {cancelled}")
    print(f"  Has QA score: {has_score} ({100*has_score/total:.1f}%)")
    print(f"  Has QA reasoning: {has_reasoning} ({100*has_reasoning/total:.1f}%)")
    print(f"  Has actionable feedback: {has_feedback} ({100*has_feedback/total:.1f}%)")
    print(f"  Has reference images: {df['hasReferenceImages'].sum()} ({100*df['hasReferenceImages'].sum()/total:.1f}%)")

    # Score distributions
    scored = df[df["qaScore"].notna()]
    if len(scored) > 0:
        print(f"\n  qaScore distribution (n={len(scored)}):")
        for score in sorted(scored["qaScore"].unique()):
            cnt = (scored["qaScore"] == score).sum()
            pct = 100 * cnt / len(scored)
            bar = "█" * int(pct / 2)
            print(f"    {int(score):>2}: {cnt:>5} ({pct:5.1f}%) {bar}")

        print(f"\n  qaTransformedScore distribution:")
        ts = scored[scored["qaTransformedScore"].notna()]
        for score in sorted(ts["qaTransformedScore"].unique()):
            cnt = (ts["qaTransformedScore"] == score).sum()
            pct = 100 * cnt / len(ts)
            print(f"    {int(score):>2}: {cnt:>5} ({pct:5.1f}%)")

    if name == "VIDEO":
        has_rewritten = (df_vid["qaRewrittenPrompt"].str.len() > 0).sum()
        print(f"\n  Has rewritten prompt: {has_rewritten} ({100*has_rewritten/total:.1f}%)")


# ─────────────────────────────────────────────
# 3. SCORE MAPPING ANALYSIS (qaScore -> qaTransformedScore)
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("SCORE MAPPING: qaScore → qaTransformedScore")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaScore"].notna() & df["qaTransformedScore"].notna()]
    print(f"\n--- {name} (n={len(scored)}) ---")
    mapping = scored.groupby("qaScore")["qaTransformedScore"].agg(["mean", "std", "count", "min", "max"])
    print(mapping.to_string())


# ─────────────────────────────────────────────
# 4. PER-MODEL QUALITY ANALYSIS
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("PER-MODEL QUALITY ANALYSIS")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaScore"].notna()].copy()
    if len(scored) == 0:
        continue
    print(f"\n--- {name} ---")
    model_stats = scored.groupby("modelTitle").agg(
        count=("qaScore", "count"),
        mean_score=("qaScore", "mean"),
        median_score=("qaScore", "median"),
        std_score=("qaScore", "std"),
        pct_high=("qaScore", lambda x: (x >= 8).mean() * 100),
        pct_low=("qaScore", lambda x: (x <= 4).mean() * 100),
        mean_transformed=("qaTransformedScore", "mean"),
    ).sort_values("mean_score", ascending=False)

    # Only show models with >= 5 scored jobs
    model_stats = model_stats[model_stats["count"] >= 5]
    print(model_stats.round(2).to_string())


# ─────────────────────────────────────────────
# 5. QA INCONSISTENCY DETECTION
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("QA INCONSISTENCY DETECTION")
print("=" * 70)
print("Finding cases where score and feedback disagree...\n")

# Negative feedback keywords
negative_keywords = [
    "missing", "not fulfilled", "fails", "failed", "absent",
    "inconsistent", "incorrect", "not match", "does not match",
    "not visible", "deviates", "not realized", "not clearly",
    "unclear", "not discernible", "impossible to verify",
    "significantly", "inaccurate", "breaks", "not accurately"
]

# Positive/minor feedback keywords
minor_keywords = [
    "minor", "slight", "subtle", "very minor", "barely",
    "no actionable", "no_actionable", "no further"
]


def feedback_severity(feedback):
    """Classify feedback severity: 'none', 'minor', 'major'."""
    if not feedback or feedback.strip() == "" or feedback.strip() == "<no_actionable_feedback>" or feedback.strip() == "<no actionable feedback>":
        return "none"
    fb_lower = feedback.lower()
    # Check for major issues first
    major_count = sum(1 for kw in negative_keywords if kw in fb_lower)
    minor_count = sum(1 for kw in minor_keywords if kw in fb_lower)

    if major_count >= 2:
        return "major"
    elif major_count >= 1 and minor_count == 0:
        return "major"
    elif minor_count > 0 and major_count == 0:
        return "minor"
    elif major_count > 0:
        return "moderate"
    else:
        return "minor"


inconsistencies = []

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaScore"].notna()].copy()
    scored["feedbackSeverity"] = scored["qaActionableFeedback"].apply(feedback_severity)

    # TYPE 1: High score (>=8) but major feedback
    high_score_bad_feedback = scored[
        (scored["qaScore"] >= 8) & (scored["feedbackSeverity"] == "major")
    ]
    print(f"\n--- {name}: HIGH SCORE (≥8) but MAJOR feedback ({len(high_score_bad_feedback)} cases) ---")
    for _, row in high_score_bad_feedback.head(5).iterrows():
        print(f"  jobId: {row['jobId']}")
        print(f"    Model: {row['modelTitle']}, qaScore: {int(row['qaScore'])}, transformed: {row['qaTransformedScore']}")
        print(f"    Prompt: {row['prompt'][:100]}...")
        print(f"    Feedback: {row['qaActionableFeedback'][:200]}")
        print()
        inconsistencies.append({
            "type": "high_score_major_feedback",
            "jobId": row["jobId"],
            "mediaType": name.lower(),
            "qaScore": row["qaScore"],
            "feedback": row["qaActionableFeedback"][:300],
            "model": row["modelTitle"],
        })

    # TYPE 2: Low score (<=4) but no/minor feedback
    low_score_no_feedback = scored[
        (scored["qaScore"] <= 4) & (scored["feedbackSeverity"].isin(["none", "minor"]))
    ]
    print(f"\n--- {name}: LOW SCORE (≤4) but NO/MINOR feedback ({len(low_score_no_feedback)} cases) ---")
    for _, row in low_score_no_feedback.head(5).iterrows():
        print(f"  jobId: {row['jobId']}")
        print(f"    Model: {row['modelTitle']}, qaScore: {int(row['qaScore'])}, transformed: {row['qaTransformedScore']}")
        print(f"    Prompt: {row['prompt'][:100]}...")
        print(f"    Feedback: '{row['qaActionableFeedback'][:200]}'")
        print()
        inconsistencies.append({
            "type": "low_score_minor_feedback",
            "jobId": row["jobId"],
            "mediaType": name.lower(),
            "qaScore": row["qaScore"],
            "feedback": row["qaActionableFeedback"][:300],
            "model": row["modelTitle"],
        })

    # TYPE 3: Empty feedback with mid-range scores (5-7) - should always have feedback
    empty_feedback_mid = scored[
        (scored["qaScore"].between(5, 7)) & (scored["feedbackSeverity"] == "none")
    ]
    print(f"\n--- {name}: MID SCORE (5-7) but EMPTY feedback ({len(empty_feedback_mid)} cases) ---")
    for _, row in empty_feedback_mid.head(3).iterrows():
        print(f"  jobId: {row['jobId']}")
        print(f"    Model: {row['modelTitle']}, qaScore: {int(row['qaScore'])}")
        print()


# ─────────────────────────────────────────────
# 6. INTERESTING JOB DEEP-DIVES
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("INTERESTING JOBS FOR DEEP-DIVE REVIEW")
print("=" * 70)

def print_job_detail(entry, media_type):
    """Print full details of a job for review."""
    print(f"  jobId: {entry.get('jobId')}")
    print(f"  Date: {parse_date(entry)}")
    print(f"  Model: {entry.get('modelTitle')} ({entry.get('modelId')})")
    print(f"  Status: {entry.get('status')}")
    print(f"  qaScore: {safe_score(entry.get('qaScore'))}")
    print(f"  qaTransformedScore: {safe_score(entry.get('qaTransformedScore'))}")
    print(f"  Prompt: {entry.get('prompt', '')[:300]}")
    print(f"  Reference images: {[x for x in (entry.get('images') or []) if x]}")
    if media_type == "image":
        print(f"  Output: {entry.get('outputImage', 'N/A')}")
    else:
        print(f"  Output: {entry.get('outputVideo', 'N/A')}")
    print(f"  QA Reasoning: {entry.get('qaReasoning', '')[:400]}")
    print(f"  QA Feedback: {entry.get('qaActionableFeedback', '')[:400]}")
    if media_type == "video" and entry.get("qaRewrittenPrompt"):
        print(f"  Rewritten Prompt: {entry.get('qaRewrittenPrompt', '')[:300]}")
    print()


# Build index for quick lookup
img_by_id = {e["jobId"]: e for e in img_raw}
vid_by_id = {e["jobId"]: e for e in vid_raw}

# --- Find specific interesting cases ---

# Category A: Complete prompt failures (score <= 3)
print("\n=== CATEGORY A: COMPLETE FAILURES (qaScore ≤ 3) ===\n")
for name, raw, media in [("IMAGE", img_raw, "image"), ("VIDEO", vid_raw, "video")]:
    failures = [
        e for e in raw
        if isinstance(safe_score(e.get("qaScore")), (int, float))
        and safe_score(e.get("qaScore")) is not None
        and safe_score(e.get("qaScore")) <= 3
        and e.get("status") == "completed"
    ]
    print(f"--- {name} failures (score ≤ 3): {len(failures)} total ---")
    for e in failures[:3]:
        print_job_detail(e, media)

# Category B: Near-perfect scores with notable feedback  
print("\n=== CATEGORY B: HIGH SCORES (≥9) WITH FEEDBACK ===\n")
for name, raw, media in [("IMAGE", img_raw, "image"), ("VIDEO", vid_raw, "video")]:
    high_with_feedback = [
        e for e in raw
        if isinstance(safe_score(e.get("qaScore")), (int, float))
        and safe_score(e.get("qaScore")) is not None
        and safe_score(e.get("qaScore")) >= 9
        and e.get("qaActionableFeedback", "").strip()
        and len(e.get("qaActionableFeedback", "")) > 20
    ]
    print(f"--- {name} high scores with feedback: {len(high_with_feedback)} total ---")
    for e in high_with_feedback[:3]:
        print_job_detail(e, media)

# Category C: Repeated retries on similar prompts (same prompt prefix, different jobs)
print("\n=== CATEGORY C: RETRY PATTERNS ===\n")
# Find prompts that appear multiple times (indicating retries)
prompt_groups_img = defaultdict(list)
for e in img_raw:
    if e.get("prompt"):
        key = (e.get("prompt") or "")[:80].strip()
        if key:
            prompt_groups_img[key].append(e)

retry_groups = {k: v for k, v in prompt_groups_img.items() if len(v) >= 3}
print(f"Image prompt groups with ≥3 attempts: {len(retry_groups)}")
# Show top 3 most retried
for prompt_key, entries in sorted(retry_groups.items(), key=lambda x: -len(x[1]))[:3]:
    scores = [safe_score(e.get("qaScore")) for e in entries if safe_score(e.get("qaScore")) is not None]
    models = [e.get("modelTitle") for e in entries]
    print(f"\n  Prompt: '{prompt_key[:100]}'")
    print(f"    Attempts: {len(entries)}")
    print(f"    Models used: {Counter(models).most_common()}")
    print(f"    Scores: {scores}")
    print(f"    JobIds: {[e['jobId'] for e in entries[:5]]}")

prompt_groups_vid = defaultdict(list)
for e in vid_raw:
    if e.get("prompt"):
        key = (e.get("prompt") or "")[:80].strip()
        if key:
            prompt_groups_vid[key].append(e)

retry_groups_vid = {k: v for k, v in prompt_groups_vid.items() if len(v) >= 3}
print(f"\nVideo prompt groups with ≥3 attempts: {len(retry_groups_vid)}")
for prompt_key, entries in sorted(retry_groups_vid.items(), key=lambda x: -len(x[1]))[:3]:
    scores = [safe_score(e.get("qaScore")) for e in entries if safe_score(e.get("qaScore")) is not None]
    models = [e.get("modelTitle") for e in entries]
    print(f"\n  Prompt: '{prompt_key[:100]}'")
    print(f"    Attempts: {len(entries)}")
    print(f"    Models used: {Counter(models).most_common()}")
    print(f"    Scores: {scores}")
    print(f"    JobIds: {[e['jobId'] for e in entries[:5]]}")


# Category D: Score 10 (perfect) - do they deserve it?
print("\n\n=== CATEGORY D: PERFECT SCORES (qaScore = 10) ===\n")
for name, raw, media in [("IMAGE", img_raw, "image"), ("VIDEO", vid_raw, "video")]:
    perfect = [
        e for e in raw
        if safe_score(e.get("qaScore")) == 10
    ]
    print(f"--- {name} perfect scores: {len(perfect)} total ---")
    # Show some with feedback (shouldn't have any if truly perfect)
    with_feedback = [e for e in perfect if e.get("qaActionableFeedback", "").strip() and len(e.get("qaActionableFeedback", "")) > 5]
    print(f"    Of which have non-empty feedback: {len(with_feedback)}")
    for e in with_feedback[:3]:
        print_job_detail(e, media)
    # Show some without
    without_feedback = [e for e in perfect if not e.get("qaActionableFeedback", "").strip()]
    for e in without_feedback[:2]:
        print_job_detail(e, media)


# ─────────────────────────────────────────────
# 7. FEEDBACK PATTERNS ANALYSIS
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("FEEDBACK PATTERN ANALYSIS")
print("=" * 70)

# Extract common feedback dimensions
feedback_dimensions = [
    "Characters", "Setting", "Style", "Story", "Animation",
    "Lighting", "Composition", "Anatomy"
]

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaActionableFeedback"].str.len() > 0]
    print(f"\n--- {name}: Feedback dimension frequency ---")
    for dim in feedback_dimensions:
        count = scored["qaActionableFeedback"].str.contains(dim, case=False, na=False).sum()
        pct = 100 * count / len(scored) if len(scored) > 0 else 0
        print(f"  {dim:>12}: {count:>5} ({pct:.1f}%)")

# Common failure modes from feedback
print("\n--- Common failure mode keywords ---")
failure_modes = [
    ("missing character", r"missing|absent|not.*present"),
    ("identity drift", r"identity|inconsist.*face|facial.*differ"),
    ("wrong expression", r"expression.*wrong|expression.*differ|expression.*not match"),
    ("anatomical issues", r"anatom|hand.*proportion|finger|extra limb"),
    ("style mismatch", r"style.*differ|style.*mismatch|styliz"),
    ("wrong action/pose", r"pose.*differ|action.*not|does not.*match.*prompt"),
    ("artifacts", r"artifact|distort|warp|glitch|flicker"),
    ("background issues", r"background.*differ|setting.*not|environment.*not"),
    ("skin tone issues", r"skin.*tone|grey.*skin|gray.*skin"),
    ("clothing issues", r"outfit|clothing|sleeves|torn|shirt"),
]

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaActionableFeedback"].str.len() > 0]
    print(f"\n  --- {name} ---")
    for mode_name, pattern in failure_modes:
        count = scored["qaActionableFeedback"].str.contains(
            pattern, case=False, na=False, regex=True
        ).sum()
        pct = 100 * count / len(scored) if len(scored) > 0 else 0
        print(f"    {mode_name:>25}: {count:>4} ({pct:.1f}%)")


# ─────────────────────────────────────────────
# 8. EMPTY qaActionableFeedback ANALYSIS
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("EMPTY/SPECIAL FEEDBACK ANALYSIS")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaScore"].notna()]
    empty_fb = scored[
        scored["qaActionableFeedback"].apply(
            lambda x: x.strip() in ["", "<no_actionable_feedback>", "<no actionable feedback>"]
            if isinstance(x, str) else True
        )
    ]
    non_empty = scored[~scored.index.isin(empty_fb.index)]
    print(f"\n--- {name} ---")
    print(f"  Scored entries: {len(scored)}")
    print(f"  Empty/no-action feedback: {len(empty_fb)} ({100*len(empty_fb)/len(scored):.1f}%)")
    print(f"  Score distribution for empty feedback:")
    if len(empty_fb) > 0:
        for s in sorted(empty_fb["qaScore"].dropna().unique()):
            c = (empty_fb["qaScore"] == s).sum()
            print(f"    Score {int(s)}: {c}")


# ─────────────────────────────────────────────
# 9. TRANSFORMED SCORE INCONSISTENCIES
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("TRANSFORMED SCORE MAPPING ANALYSIS")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaScore"].notna() & df["qaTransformedScore"].notna()].copy()
    print(f"\n--- {name} ---")
    # Cross-tab
    ct = pd.crosstab(
        scored["qaScore"].astype(int), 
        scored["qaTransformedScore"].astype(int),
        margins=True
    )
    print(ct.to_string())

    # Are there inconsistencies? Same qaScore mapping to different transformed scores?
    mapping_var = scored.groupby("qaScore")["qaTransformedScore"].nunique()
    inconsistent = mapping_var[mapping_var > 1]
    if len(inconsistent) > 0:
        print(f"\n  INCONSISTENT mappings (qaScore maps to multiple transformed scores):")
        for score, n_unique in inconsistent.items():
            examples = scored[scored["qaScore"] == score]["qaTransformedScore"].value_counts()
            print(f"    qaScore={int(score)} maps to {n_unique} different transformed scores: {dict(examples)}")


# ─────────────────────────────────────────────
# 10. MODEL COMPARISON - SAME PROMPT, DIFFERENT MODELS
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("SAME PROMPT, DIFFERENT MODELS COMPARISON")
print("=" * 70)

for label, groups in [("IMAGE", prompt_groups_img), ("VIDEO", prompt_groups_vid)]:
    multi_model = {}
    for key, entries in groups.items():
        models_used = set(e.get("modelTitle") for e in entries)
        scored_entries = [e for e in entries if safe_score(e.get("qaScore")) is not None]
        if len(models_used) >= 2 and len(scored_entries) >= 2:
            multi_model[key] = scored_entries

    print(f"\n--- {label}: Prompts tried with multiple models AND scored: {len(multi_model)} ---")
    for prompt_key, entries in sorted(multi_model.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"\n  Prompt: '{prompt_key[:120]}'")
        for e in entries:
            print(f"    {e['modelTitle']:>30} | Score: {safe_score(e.get('qaScore'))} | {e['jobId']}")


# ─────────────────────────────────────────────
# 11. ENTRIES WITH NO QA AT ALL
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("ENTRIES WITHOUT QA ANALYSIS")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    no_qa = df[df["qaScore"].isna()]
    completed_no_qa = no_qa[no_qa["status"] == "completed"]
    print(f"\n--- {name} ---")
    print(f"  No QA score: {len(no_qa)} / {len(df)}")
    print(f"  Completed but no QA: {len(completed_no_qa)}")
    print(f"  Model distribution (no QA, completed):")
    model_dist = completed_no_qa["modelTitle"].value_counts().head(10)
    for model, cnt in model_dist.items():
        print(f"    {model}: {cnt}")


# ─────────────────────────────────────────────
# 12. VIDEO-SPECIFIC: REWRITTEN PROMPT ANALYSIS
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("VIDEO: REWRITTEN PROMPT ANALYSIS")
print("=" * 70)

vid_scored = df_vid[df_vid["qaScore"].notna()].copy()
has_rewrite = vid_scored[vid_scored["qaRewrittenPrompt"].str.len() > 0]
no_rewrite = vid_scored[vid_scored["qaRewrittenPrompt"].str.len() == 0]

print(f"Scored videos with rewritten prompt: {len(has_rewrite)}")
print(f"Scored videos without rewritten prompt: {len(no_rewrite)}")

if len(has_rewrite) > 0 and len(no_rewrite) > 0:
    print(f"\nMean qaScore WITH rewrite: {has_rewrite['qaScore'].mean():.2f}")
    print(f"Mean qaScore WITHOUT rewrite: {no_rewrite['qaScore'].mean():.2f}")

# Analyze what the rewrite adds
print("\n--- Common additions in rewritten prompts ---")
rewrite_additions = [
    ("consistency instruction", r"consistent|maintain.*feature|stable"),
    ("smooth animation", r"smooth|natural.*movement|natural.*motion"),
    ("no artifacts", r"artifact|distort|warp|flicker|glitch"),
    ("facial features", r"facial.*feature|face.*consisten|expression.*consisten"),
    ("camera instruction", r"camera.*remain|camera.*track|camera.*follow"),
    ("sound/audio", r"sound|audio|ambient|footstep|creak"),
    ("lighting instruction", r"lighting.*consisten|lighting.*stable|light.*remain"),
]

for add_name, pattern in rewrite_additions:
    in_rewrite = has_rewrite["qaRewrittenPrompt"].str.contains(pattern, case=False, na=False, regex=True).sum()
    in_original = has_rewrite["prompt"].str.contains(pattern, case=False, na=False, regex=True).sum()
    pct_rewrite = 100 * in_rewrite / len(has_rewrite) if len(has_rewrite) > 0 else 0
    pct_original = 100 * in_original / len(has_rewrite) if len(has_rewrite) > 0 else 0
    print(f"  {add_name:>25}: original {pct_original:.1f}% → rewritten {pct_rewrite:.1f}%")


# Show a few rewrite examples
print("\n--- Sample rewrite comparisons ---")
for _, row in has_rewrite.head(3).iterrows():
    print(f"\n  jobId: {row['jobId']}")
    print(f"  Score: {int(row['qaScore'])}")
    print(f"  ORIGINAL:  {row['prompt'][:200]}...")
    print(f"  REWRITTEN: {row['qaRewrittenPrompt'][:200]}...")


# ─────────────────────────────────────────────
# 13. CANDIDATE REGRESSION TEST CASES
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("CANDIDATE REGRESSION TEST CASES")
print("=" * 70)

regression_candidates = []

# Type 1: Character missing entirely (critical failure)
for e in img_raw:
    fb = e.get("qaActionableFeedback", "").lower()
    if "missing" in fb and ("character" in fb or "cat" in fb) and safe_score(e.get("qaScore")) is not None:
        regression_candidates.append({
            "jobId": e["jobId"],
            "type": "character_missing",
            "media": "image",
            "score": safe_score(e.get("qaScore")),
            "reason": e.get("qaActionableFeedback", "")[:200],
        })

# Type 2: Wrong action/pose
for e in img_raw:
    fb = e.get("qaActionableFeedback", "").lower()
    reasoning = e.get("qaReasoning", "").lower()
    if ("does not match" in fb or "not fulfilled" in fb or "not match" in reasoning) and safe_score(e.get("qaScore")) is not None:
        regression_candidates.append({
            "jobId": e["jobId"],
            "type": "prompt_not_fulfilled",
            "media": "image",
            "score": safe_score(e.get("qaScore")),
            "reason": e.get("qaActionableFeedback", "")[:200],
        })

# Type 3: Video identity drift
for e in vid_raw:
    fb = e.get("qaActionableFeedback", "").lower()
    if ("identity" in fb or "inconsist" in fb) and "face" in fb and safe_score(e.get("qaScore")) is not None:
        regression_candidates.append({
            "jobId": e["jobId"],
            "type": "identity_drift",
            "media": "video",
            "score": safe_score(e.get("qaScore")),
            "reason": e.get("qaActionableFeedback", "")[:200],
        })

# Type 4: Video artifacts
for e in vid_raw:
    fb = e.get("qaActionableFeedback", "").lower()
    if ("artifact" in fb or "distort" in fb or "warp" in fb) and safe_score(e.get("qaScore")) is not None:
        regression_candidates.append({
            "jobId": e["jobId"],
            "type": "visual_artifacts",
            "media": "video",
            "score": safe_score(e.get("qaScore")),
            "reason": e.get("qaActionableFeedback", "")[:200],
        })

print(f"Total regression candidates found: {len(regression_candidates)}")
type_counts = Counter(r["type"] for r in regression_candidates)
for t, c in type_counts.most_common():
    print(f"  {t}: {c}")

# Show best candidates per type
print("\n--- Best candidates per failure type ---")
for fail_type in ["character_missing", "prompt_not_fulfilled", "identity_drift", "visual_artifacts"]:
    candidates = [r for r in regression_candidates if r["type"] == fail_type]
    if candidates:
        # Pick ones with clear low scores
        candidates.sort(key=lambda x: x["score"])
        best = candidates[0]
        print(f"\n  [{fail_type}]")
        print(f"    jobId: {best['jobId']}")
        print(f"    Score: {best['score']}")
        print(f"    Reason: {best['reason']}")


# ─────────────────────────────────────────────
# 14. GENERATE APPENDIX TABLE
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("GENERATING APPENDIX TABLE")
print("=" * 70)

# Select interesting jobs for the appendix
appendix_jobs = []

# Pick from each category
# 3+ image jobs, 3+ video jobs, including ≥2 where QA is wrong/incomplete

# Image: Complete failure
for e in img_raw:
    if e.get("jobId") == "e268c427-dc7d-4f82-a1fa-14268f374460":
        appendix_jobs.append({"entry": e, "media": "image", "category": "complete failure", "qa_agree": "agree"})
        break

# Image: High score with notable feedback (possible QA too lenient)
img_scored = [e for e in img_raw if isinstance(safe_score(e.get("qaScore")), (int, float)) and safe_score(e.get("qaScore")) is not None]
high_img_with_fb = [
    e for e in img_scored
    if safe_score(e["qaScore"]) >= 8
    and len(e.get("qaActionableFeedback", "")) > 50
    and any(kw in e.get("qaActionableFeedback", "").lower() for kw in ["not fulfilled", "missing", "fails", "does not match", "not match"])
]
for e in high_img_with_fb[:2]:
    appendix_jobs.append({"entry": e, "media": "image", "category": "QA possibly wrong (too high)", "qa_agree": "disagree"})

# Image: Good score with empty feedback
img_empty_fb = [
    e for e in img_scored
    if safe_score(e["qaScore"]) in [9, 10]
    and not e.get("qaActionableFeedback", "").strip()
]
if img_empty_fb:
    appendix_jobs.append({"entry": img_empty_fb[0], "media": "image", "category": "perfect score no feedback", "qa_agree": "cannot verify"})

# Video: Low score
vid_scored = [e for e in vid_raw if isinstance(safe_score(e.get("qaScore")), (int, float)) and safe_score(e.get("qaScore")) is not None]
vid_low = [e for e in vid_scored if safe_score(e["qaScore"]) <= 4]
for e in vid_low[:2]:
    appendix_jobs.append({"entry": e, "media": "video", "category": "low score", "qa_agree": "partially agree"})

# Video: High score with identity drift feedback
vid_high_drift = [
    e for e in vid_scored
    if safe_score(e["qaScore"]) >= 7
    and "inconsist" in e.get("qaActionableFeedback", "").lower()
]
for e in vid_high_drift[:2]:
    appendix_jobs.append({"entry": e, "media": "video", "category": "QA possibly wrong (overlooking drift)", "qa_agree": "disagree"})

# Video: With rewritten prompt
vid_rewritten = [e for e in vid_scored if e.get("qaRewrittenPrompt", "").strip()]
if vid_rewritten:
    appendix_jobs.append({"entry": vid_rewritten[0], "media": "video", "category": "has rewritten prompt", "qa_agree": "agree"})

print(f"\nAppendix jobs selected: {len(appendix_jobs)}")
print(f"  Image: {sum(1 for j in appendix_jobs if j['media'] == 'image')}")
print(f"  Video: {sum(1 for j in appendix_jobs if j['media'] == 'video')}")

# Write appendix as markdown
appendix_lines = [
    "# Appendix: Reviewed JobIds\n\n",
    "| # | jobId | Media | Model | qaScore | tScore | Category | QA Agreement | Prompt (truncated) | Feedback (truncated) |\n",
    "|---|-------|-------|-------|---------|--------|----------|--------------|-------------------|---------------------|\n",
]

for i, j in enumerate(appendix_jobs, 1):
    e = j["entry"]
    appendix_lines.append(
        f"| {i} | `{e['jobId'][:12]}...` | {j['media']} | {e.get('modelTitle', '?')} | "
        f"{safe_score(e.get('qaScore'))} | {safe_score(e.get('qaTransformedScore'))} | "
        f"{j['category']} | {j['qa_agree']} | "
        f"{e.get('prompt', '')[:80].replace('|', '/')}... | "
        f"{e.get('qaActionableFeedback', '')[:100].replace('|', '/')}... |\n"
    )

appendix_md = "".join(appendix_lines)
with open(os.path.join(OUTPUT_DIR, "appendix_table.md"), "w") as f:
    f.write(appendix_md)
print("\nAppendix table written to analysis_output/appendix_table.md")

# Also write full details
with open(os.path.join(OUTPUT_DIR, "appendix_full_details.json"), "w") as f:
    details = []
    for j in appendix_jobs:
        e = j["entry"]
        details.append({
            "jobId": e["jobId"],
            "media": j["media"],
            "category": j["category"],
            "qa_agree": j["qa_agree"],
            "modelTitle": e.get("modelTitle"),
            "qaScore": safe_score(e.get("qaScore")),
            "qaTransformedScore": safe_score(e.get("qaTransformedScore")),
            "prompt": e.get("prompt", ""),
            "qaReasoning": e.get("qaReasoning", ""),
            "qaActionableFeedback": e.get("qaActionableFeedback", ""),
            "qaRewrittenPrompt": e.get("qaRewrittenPrompt", "") if j["media"] == "video" else "",
            "images": e.get("images", []),
            "output": e.get("outputImage") or e.get("outputVideo", ""),
        })
    json.dump(details, f, indent=2)
print("Full details written to analysis_output/appendix_full_details.json")


# ─────────────────────────────────────────────
# 15. SUMMARY STATISTICS
# ─────────────────────────────────────────────
print("\n" + "=" * 70)
print("SUMMARY STATISTICS FOR MEMO")
print("=" * 70)

for name, df in [("IMAGE", df_img), ("VIDEO", df_vid)]:
    scored = df[df["qaScore"].notna()]
    print(f"\n--- {name} ---")
    print(f"  Total entries: {len(df)}")
    print(f"  Scored: {len(scored)} ({100*len(scored)/len(df):.1f}%)")
    if len(scored) > 0:
        print(f"  Mean qaScore: {scored['qaScore'].mean():.2f}")
        print(f"  Median qaScore: {scored['qaScore'].median():.1f}")
        print(f"  % scoring ≥8 ('good'): {100*(scored['qaScore']>=8).mean():.1f}%")
        print(f"  % scoring ≤4 ('fail'): {100*(scored['qaScore']<=4).mean():.1f}%")
        print(f"  Unique models used: {df['modelTitle'].nunique()}")
        print(f"  Unique models with scores: {scored['modelTitle'].nunique()}")
        
        # Failed jobs
        failed = df[df["status"] == "failed"]
        print(f"  Failed jobs: {len(failed)} ({100*len(failed)/len(df):.1f}%)")


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print(f"\nOutput files in: {OUTPUT_DIR}/")
print("  - appendix_table.md")
print("  - appendix_full_details.json")
