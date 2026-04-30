# Jadu Multimodal AI Engineer Challenge — Submission

## 0) Relevant Hands-On Experience

> **[YOU MUST WRITE THIS SECTION YOURSELF]**
> Describe up to 2 projects. For each: Context, Your Role, Prompting, Evaluation, Dataset Prep, Metrics, Outcome, Reflection. Be explicit about hands-on vs. hypothesis.

---

## 1) Audit the Data and the Current QA

### Data Trust Assessment

**Trust:** The `qaReasoning` and `qaActionableFeedback` text — detailed, specific, and structurally consistent (uses dimensional vocabulary: Characters, Setting, Style, Story, Animation). Also: `status`, `modelTitle`, and prompt text.

**Treat carefully:** The `qaScore` (1–10) is severely inflated for images — 81% score ≥8, mean 8.41 — making it nearly useless for discriminating quality. Video scores are healthier (mean 6.99). Critically, 157 image and 64 video jobs score ≥8 yet carry major negative feedback (deforming faces, missing accessories). The `qaTransformedScore` has a non-deterministic mapping (`qaScore=4` maps to {1, 2, 4}), breaking any accept/reject logic built on it. Rewritten prompts (72% of scored videos) score *lower* on average (6.75 vs. 7.64), meaning they are generated post-hoc, not used pre-generation.

**Exclude:** 63% of images and 68% of videos have no QA data. Failed/cancelled entries (397 total). Malformed scores (NaN, string types). Test prompts ("A strong feather" ×49, "An image" ×30). Only 10 of 45 image models have any scored data.

**System design issues:** Score inflation means any `qaScore ≥ 8` threshold passes everything. The QA evaluator has no shot-type awareness — it scores silhouettes at 9/10 while admitting identity "cannot be confirmed."

### Specific Job Reviews (see Appendix for full table)

**`e268c427` — Image, Nano Banana, score 3 | Agree.** Cat entirely missing from composited scene. Core requirement unmet. → **Switch model** to Shot Image OpenAI (mean 8.75 vs. 6.59).

**`6902b24d` — Image, Shot Image OpenAI, score 9 | ⚠️ Disagree.** Silhouette shot; QA gives 9/10 but states identity "cannot be confirmed." A score acknowledging it can't verify the most important dimension is unreliable. Should score 6–7 or auto-flag for human review. → **Human review** for all silhouette/dark-shot evaluations. *(proposal)*

**`efd7775c` — Image, GPT Image 1, score 8 | ⚠️ Disagree.** Missing ruby choker + different facial features + non-identical pose. In animation production, any costume inconsistency breaks continuity. Should be 5–6. → **Retry with prompt change** naming the missing accessory explicitly. *(proposal)*

**`e5406625` — Video, Seedance 1 Pro, score 3 | Agree.** Prompt says "no characters present" but the dog from the reference image appears in every frame. → **Switch approach** — generate clean environment image first, then animate. The i2v model inherently preserves reference content; negative constraints require a different pipeline. *(proposal)*

**`9f2ebf65` — Video, Seedance 1 Pro, score 8 | ⚠️ Disagree.** QA reports "facial features and hand positions intermittently deform." Scoring 8/10 for deforming faces normalizes a defect any creative reviewer would reject. Should be 5–6. → **Retry**. *(proposal)*

**`505debbd` — Video, Seedance 1 Pro, score 8 | Partially agree.** Jawline/mouth fluctuation across frames is a known i2v limitation. Borderline acceptable. → **Accept conditionally** after 2+ attempts. *(proposal)*

---

## 2) Design V2 of the Workflow

### Model Selection, Prompting, and Decision Logic *(proposal)*

**Model routing** based on evidence: Images — Shot Image OpenAI (mean 8.75) for multi-character; GPT Image 1 (8.47) for simpler scenes. Videos — Seedance 1 Pro (most data, 7.07) primary; Hailuo 2.0 (6.98) as fallback.

**Prompt rewriting** should happen *before* generation: the current rewrite system correctly enriches prompts with consistency instructions (16%→62%), smooth animation (12%→47%), and facial stability (9%→35%), but applies them too late.

**Accept/retry logic:** Replace the single 1–10 score with 4 independent dimensions scored 1–4: *Prompt Fulfillment, Character Identity, Visual Quality, Temporal Consistency*. All ≥3 → accept. Any =1 → retry (max 3 attempts), then switch model, then escalate to human. Any dimension the QA flags "low confidence" → auto-escalate.

### Revised QA Evaluation Prompt *(proposal)*

```
Score each dimension independently (1–4):
1. PROMPT_FULFILLMENT: Core action/scene present? 1=missing primary element. 4=all elements correct.
2. CHARACTER_IDENTITY: Faces, outfits, accessories match references? 1=unrecognizable.
   2=cannot verify (silhouette/occlusion) → flag human review. 4=clear match all frames.
3. VISUAL_QUALITY: Artifacts, deformations, anatomical errors? 1=faces/hands deform. 4=artifact-free.
4. TEMPORAL_CONSISTENCY (video): Features stable across frames? 1=identity drifts. 4=frame-stable.

Output: {dimension_scores, overall_pass_fail, confidence: high|medium|low, human_review_required: bool}
Set human_review_required=true if any dimension ≤2, confidence low, or average 2.5–3.0.
```

### Eval Set & Regression Suite *(proposal)*

**Eval set:** 50 cases across 9 slices — simple single-character (8), multi-character compositing (8), environment edits (6), fantastical (4), negative constraints (4), static dialogue video (6), high-motion video (6), complex timed sequences (4), silhouette/dark shots (4).

**Regression suite:** 15 permanent tests from real failures including: character missing (`e268c427`), negative constraint violation (`e5406625`), costume fidelity (`efd7775c`), face deformation (`9f2ebf65`), 360° camera stasis (`e651cc2a`), skin tone shift, timed sequence failure, reflection-only framing. All must pass for any release.

### Automated vs. Human Decision Boundaries *(proposal)*

**Auto-decide:** Clear passes (all dims ≥3, high confidence) and clear fails (any dim =1). ~70% of cases. **Human required:** Silhouette/dark shots, borderline scores, fantastical content, and any case flagged low-confidence.

### Example Walkthrough 1: Realistic Multi-Character Scene

*"Vet talks to Amrita while Mohini (cat) watches calmly. Wide shot, living room."* (Based on `6702d149`, `3767e33f`.)

- **Model:** Shot Image OpenAI. **Prompt:** Structured with numbered refs + "Maintain exact facial features and outfit accessories from each reference."
- **Accept:** All 4 dims ≥3, identity check per named character. **Fallback:** Retry with expression correction ("Amrita should appear calm, not anxious") → GPT Image 1 → human escalation.

### Example Walkthrough 2: Fantastical Underwater Sequence

*"Beneath the surface, Irina leads Adam by hand through dark water. Adam struggles, Irina swims gracefully."* (Based on `f35481ec` [score 10], `81fd40a1`.)

- **Model:** Shot Image OpenAI for key frame (scored 10 on this prompt); Seedance 1 Pro for video. **Prompt:** Add "No sweat droplets underwater. Hair floats naturally. Consistent character proportions."
- **Accept:** Prompt fulfillment ≥3, no terrestrial artifacts underwater. **Fallback:** Retry → Hailuo 2.0 → human.

---

## 3) Measure Improvement and Prevent Regressions

**Success =** higher first-attempt acceptance rate than V1, 100% regression suite pass, ≥85% human agreement with auto-QA.

**Primary metrics:** *Prompt fulfillment rate* (% outputs with core scene present — most trustworthy, unambiguous when feedback says "cat is missing"). *First-attempt acceptance rate* (measures prompt+model quality). *Per-dimension pass rates* (≥3 on each of 4 dims).

**Secondary/guardrail metrics:** *Mean retry count* (efficiency). *Human escalation rate* (≤15%; rising = evaluator losing confidence). *qaScore (1–10)* — **metric to treat carefully** — too compressed at the top (81% ≥8 for images), usable only as a secondary signal alongside the 4-dim breakdown.

**Thresholds:** Prompt fulfillment ≥92%, character identity ≥88%, visual quality ≥85% (images) / ≥80% (video), temporal consistency ≥78%. Regression suite: 100%. Any failure blocks release.

**Evaluation slices:** By reference image count (0/1/2/3+), prompt complexity, shot type (close-up/wide/silhouette), motion type (static/action), model, content type (realistic/fantastical), negative constraints.

**Calibrating QA:** Initial: 100 stratified outputs scored by 3 humans on the same rubric; measure auto-human agreement. Ongoing: weekly 5% spot-check of auto-accepted and auto-rejected outputs. Reversal rate >15% → pause auto-decisions and recalibrate. *(proposal)*

**Detecting drift:** Weekly score distribution monitoring (image scores already at 81% ≥8 — further drift = problem). Track the score-feedback divergence count (currently 157 images) — must decrease, not increase. Monthly anchor tests: run 15 regression cases; if the evaluator scores a known failure at 7 instead of 3, it has drifted. *(proposal)*

**What blocks release even if aggregate improves:** (1) Any regression test failure. (2) Any slice dropping >5pp vs. baseline (e.g., aggregate improves but "negative constraints" drops from 60%→40%). (3) Score-feedback disagreement rate increasing.

**Permanent regression test: `e5406625`** — "No characters present" produces video with dog in every frame. Tests the pipeline's ability to handle negative constraints with i2v models. Currently broken. Must be solved before V2 ships. *(proposal)*
