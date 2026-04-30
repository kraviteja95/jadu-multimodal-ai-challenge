# Jadu Multimodal AI Challenge — Analysis Findings
## Prepared for Memo Writing

---

## KEY DATA OVERVIEW

| Metric | Images | Videos |
|--------|--------|--------|
| Total entries | 8,111 | 4,141 |
| Completed | 7,889 (97.3%) | 3,966 (95.8%) |
| Failed | 165 (2.0%) | 153 (3.7%) |
| **Has QA score** | **3,022 (37.3%)** | **1,332 (32.2%)** |
| Has reference images | 5,522 (68.1%) | 1,462 (35.3%) |
| Unique models | 45 | 17 |
| Models with scores | 10 | 10 |
| Mean qaScore | 8.41 | 6.99 |
| Median qaScore | 9.0 | 7.0 |
| % scoring ≥8 | 80.9% | 45.6% |
| % scoring ≤4 | 4.2% | 12.2% |

---

## SECTION 1: DATA AUDIT FINDINGS

### What to TRUST
1. **qaReasoning text** — Detailed, specific, references prompt elements. Present for all scored entries.
2. **qaActionableFeedback categories** — Uses structured dimensions (Characters, Setting, Style, Story, Animation). Consistent vocabulary.
3. **Status field** — Reliable for filtering completed vs. failed/cancelled.
4. **Model identification** — modelTitle and modelId consistently populated.
5. **Prompt text** — Original prompts are always present for completed jobs.

### What to TREAT CAREFULLY
1. **qaScore (1-10)** — Heavily skewed towards high scores for images (81% ≥ 8). The QA is likely too lenient or evaluated with a biased rubric. Video scores are more normally distributed (mean 7.0).
2. **qaTransformedScore** — Mapping from qaScore is NOT deterministic. Example: qaScore=4 maps to transformed {1, 2, 4} — the same raw score produces different outputs. This makes the transformed score unreliable for decision-making.
3. **Score-feedback inconsistencies** — 157 image jobs and 64 video jobs have score ≥8 but major negative feedback. Conversely, 28 image and 45 video jobs have score ≤4 but feedback coded as minor.
4. **Rewritten prompts** — Present for 963/1,332 scored videos (72%). The rewritten prompts score LOWER on average (6.75 vs 7.64), which is counterintuitive — the rewrite may be generated post-hoc rather than used for a retry.

### What to EXCLUDE
1. **Entries with no QA** — 63% of images and 68% of videos have zero QA data. Cannot be used for quality analysis.
2. **Failed/processing/cancelled jobs** — 222 image + 175 video entries with non-completed status.
3. **NaN/malformed scores** — At least 1 entry has `{"$numberDouble": "NaN"}` as qaScore. 1 entry has string `"4"` as qaTransformedScore.
4. **Test prompts** — "A strong feather" repeated 49 times, "An image" repeated 30 times — appear to be test/calibration data, not real creative requests.

### Issues Affecting System Design
1. **Score inflation** — Image QA mean of 8.41/10 suggests the evaluator is overconfident. If 81% of outputs are "good," the QA isn't discriminating enough.
2. **No QA on most entries** — Only ~35% of completed jobs get QA'd. This means the system can't learn from 65% of its outputs.
3. **Transformed score mapping is broken** — qaScore 4 can map to transformed 1, 2, OR 4. This inconsistency means the transformed score cannot be trusted for accept/reject decisions.
4. **Top-heavy model coverage** — Only 10/45 image models and 10/17 video models have scored entries. GPT Image 1 and Shot Image OpenAI dominate image scores; Seedance 1 Pro dominates video scores.

---

## SECTION 1: SPECIFIC JOB REVIEWS

### IMAGE JOB 1: `e268c427-dc7d-4f82-a1fa-14268f374460`
- **Model**: Nano Banana | **qaScore**: 3 | **Transformed**: 2
- **Prompt**: "Add a reference image 1 character in the input image 2. And make it a wide-angle shot."
- **QA says**: The black cat from reference image 1 is completely missing.
- **My assessment**: **Agree** — Complete failure. The core requirement (add cat to scene) was not met.
- **Failure mode**: Model unable to composite reference character into scene.
- **System should**: **Switch model** to GPT Image 1 or Shot Image OpenAI (both score higher on multi-character composition tasks).

### IMAGE JOB 2: `6902b24d-2474-46bc-8064-41bffa9d87e1` ⚠️ QA WRONG
- **Model**: Shot Image OpenAI | **qaScore**: 9 | **Transformed**: 3
- **Prompt**: "Priya's silhouette framed by the door, entering a dim, cavernous lobby..."
- **QA says**: "Facial details are not visible in the silhouette, making full character identity confirmation difficult."
- **My assessment**: **Disagree with score** — The QA gives 9/10 but then says identity can't be confirmed. For a silhouette shot this is expected, but the QA is scoring high while acknowledging it can't verify the most important thing (character identity). The score should be lower (6-7) since identity verification is impossible, OR the QA should explicitly mark this as "low-confidence evaluation" and defer to human review.
- **Failure mode**: QA evaluator doesn't adjust scoring rubric based on shot type (silhouette shots make character verification impossible by definition).
- **System should**: **Flag for human review** — silhouette/dark shots should auto-trigger human approval since automated QA can't verify character identity.

### IMAGE JOB 3: `efd7775c-0394-4558-80b4-d5326bb2f72b` ⚠️ QA WRONG
- **Model**: GPT Image 1 | **qaScore**: 8 | **Transformed**: 3
- **Prompt**: "Keep the character and the car proportional..."
- **QA says**: "Differences in facial features and hair from the reference; missing necklace/choker. Pose is similar but not identical."
- **My assessment**: **Disagree with score** — Missing a specific accessory (choker/necklace) mentioned in the reference AND different facial features should result in a score of 5-6, not 8. The QA is being too forgiving of character consistency failures.
- **Failure mode**: QA treats missing costume elements as minor when they're identity-critical for character consistency in animation.
- **System should**: **Retry with prompt change** — add explicit instruction about preserving ruby choker/necklace and facial features.

### IMAGE JOB 4: `ab65492a-83e1-4431-9336-6d2f35d35248` — QA Trustworthy but Trivial
- **Model**: Nano Banana | **qaScore**: 10 | **Transformed**: 4
- **Prompt**: "2 persons dancing together"
- **QA says**: No actionable feedback.
- **My assessment**: **Agree with score, but this is a trivial prompt** — No reference images, extremely simple prompt. A score of 10 here doesn't prove the system handles hard cases well. This type of test case should be categorized separately from complex multi-character scenes.
- **System should**: **Accept** — but note this contributes to score inflation.

### VIDEO JOB 1: `e5406625-7fb0-43b5-a59d-0747acb9b9db`
- **Model**: Seedance 1 Pro | **qaScore**: 3 | **Transformed**: 1
- **Prompt**: "No characters present. The environment should appear calm but empty, moonlight casting soft shadows..."
- **QA says**: Character (dog) present throughout, contradicting the "no characters" prompt.
- **My assessment**: **Agree** — The model completely ignored the core requirement (no characters).
- **Failure mode**: Image-to-video model preserves the reference image character despite the prompt explicitly saying "no characters."
- **System should**: **Switch approach** — For "remove character" requests in i2v, consider using a different pipeline (e.g., generate the environment image first without characters, then animate it).

### VIDEO JOB 2: `9f2ebf65-9831-4c31-80fb-a453a47b61fd` ⚠️ QA WRONG
- **Model**: Seedance 1 Pro | **qaScore**: 8 | **Transformed**: 3
- **Prompt**: "Taxi driver leans forward, giving a low, chilling warning as Priya walks away..."
- **QA says**: "Facial features and hand positions intermittently deform; inconsistent sweat and shifting hair/clothing details reduce realism."
- **My assessment**: **Disagree with score** — Intermittent face/hand deformation is a serious artifact in video. Scoring 8/10 for a video with deforming faces normalizes a defect that would be immediately noticed by creative reviewers. Should be 5-6.
- **Failure mode**: QA over-weights prompt adherence and under-weights visual quality/artifacts.
- **System should**: **Retry** — same model, same prompt, hope for less artifact variance.

### VIDEO JOB 3: `505debbd-704a-4938-a01a-065a04963e97`
- **Model**: Seedance 1 Pro | **qaScore**: 8 | **Transformed**: 3
- **Prompt**: "A stylish woman with a sleek bob haircut and dark sunglasses sits in the driver's seat..."
- **QA says**: "Noticeable consistency issues in facial features (jawline, mouth, line thickness fluctuate between frames), leading to minor identity drift."
- **My assessment**: **Partially agree** — Score 8 is borderline acceptable. The feedback accurately identifies jawline/mouth fluctuation which is a real video artifact issue.
- **Failure mode**: Frame-to-frame consistency in facial details remains a systematic video generation weakness.
- **System should**: **Accept conditionally** — if this is the best available after 2+ attempts, accept. The rewritten prompt already adds consistency instructions.

---

## SECTION 2: KEY FINDINGS FOR V2 DESIGN

### Model Performance Rankings

**Images (by mean qaScore, ≥5 scored jobs):**
1. Shot Image OpenAI: 8.75 (n=1455) — Best performer
2. GPT Image 1: 8.47 (n=1225) — Close second
3. Imagegen4 Fast: 8.35 (n=20) — Small sample
4. Flux Kontext Pro: 6.77 (n=144) — Mid-tier
5. Nano Banana: 6.59 (n=90) — Lower quality
6. Flux Dev: 5.10 (n=10) — Poor

**Videos (by mean qaScore, ≥5 scored jobs):**
1. Seedance 1 Pro: 7.07 (n=885) — Most data, decent quality
2. Hailuo 2.0: 6.98 (n=310) — Similar to Seedance
3. Kling V2.1: 6.96 (n=53) — Good but limited data
4. Wan 2.2 Fast: 6.45 (n=55)
5. Kling V1.6 Pro: 6.00 (n=17)

### Retry Pattern Insights
- "Still life, Camera sliding 360°" was attempted **22 times** with Hailuo 2.0, scores ranging 2-9. Massive variance suggests this type of shot is model-dependent.
- "A woman in a dark green suit..." was tried across **9 different models** (19 attempts), scores 4-9. Seedance 1 Pro eventually reached 9.
- Same prompt with GPT Image 1 vs Flux Dev: GPT gets 9-10, Flux gets 3 on the same Mercedes prompt.

### Rewritten Prompt Analysis
The QA system generates rewritten prompts for 72% of scored videos. Key additions:
- **Consistency instructions**: 16% → 62% (3.8x increase)
- **Smooth animation**: 12% → 47% (4x increase)
- **No artifacts**: 19% → 38% (2x increase)
- **Facial features**: 9% → 35% (4x increase)
- **Sound/audio**: 6% → 18% (3x increase)

This shows the rewrite system correctly identifies that original prompts lack stability/consistency instructions that video models need.

### Common Failure Modes (from feedback)

**Images:**
- Identity drift: 18.5% of feedback
- Missing character: 14.8%
- Style mismatch: 10.0%
- Artifacts: 8.1%
- Wrong action/pose: 7.8%

**Videos:**
- Artifacts: dominant issue (852 regression candidates)
- Identity drift: 105 cases
- Character missing: rare but critical

---

## SECTION 3: METRICS & REGRESSION INSIGHTS

### Metric I Would TRUST: `prompt_fulfillment_binary`
A binary metric: did the output fulfill the core prompt requirement or not? The QA reasoning already captures this well — when a character is missing, the wrong action is shown, or the environment doesn't match, it's clearly stated. This is more reliable than the 1-10 score because it's less subjective.

### Metric I Would TREAT CAREFULLY: `qaScore` (1-10)
The 1-10 scale is too compressed at the top for images (81% ≥ 8), making it nearly useless for discriminating between "good" and "great." For videos, the distribution is healthier but still suffers from score-feedback disagreements.

### Failure Case for Permanent Regression Test:
**jobId `e5406625-7fb0-43b5-a59d-0747acb9b9db`** — Video where prompt says "no characters present" but the model puts the dog from the reference image into every frame. This tests the critical capability of i2v models to follow negative constraints, which is fundamentally broken in the current pipeline. Any V2 system must pass this test.

---

## APPENDIX: FULL JOB REVIEW TABLE

See `analysis_output/appendix_table.md` and `analysis_output/appendix_full_details.json`
See `analysis_output/full_analysis.txt` for complete analysis output.
