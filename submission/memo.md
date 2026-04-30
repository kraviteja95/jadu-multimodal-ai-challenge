# Jadu Multimodal AI Engineer Challenge — Submission

## Table of Contents

- [0) Relevant Hands-On Experience](#0-relevant-hands-on-experience)
  - [Project 1: Multimodal RAG System for Technical Troubleshooting](#project-1-multimodal-rag-system-for-technical-troubleshooting)
    - [Context](#context)
    - [My Role](#my-role)
    - [Prompting / System Prompting](#prompting--system-prompting)
    - [Evaluation](#evaluation)
    - [Dataset Preparation](#dataset-preparation)
    - [Metrics](#metrics)
    - [Outcome](#outcome)
    - [Reflection](#reflection)
  - [Project 2: Fine-Tuning and Preference Optimization for Technical QA](#project-2-fine-tuning-and-preference-optimization-for-technical-qa)
    - [Context](#context-1)
    - [My Role](#my-role-1)
    - [Prompting / System Prompting](#prompting--system-prompting-1)
    - [Evaluation](#evaluation-1)
    - [Dataset Preparation](#dataset-preparation-1)
    - [Metrics](#metrics-1)
    - [Outcome](#outcome-1)
    - [Reflection](#reflection-1)

- [1) Audit the Data and the Current QA](#1-audit-the-data-and-the-current-qa)
  - [Data Trust Classification](#data-trust-classification)
  - [Specific Job Reviews](#specific-job-reviews)

- [2) Design V2 of the Workflow](#2-design-v2-of-the-workflow)
  - [Model Selection](#model-selection-proposal-for-this-exercise)
  - [Prompt Writing and Rewriting](#prompt-writing-and-rewriting-proposal-for-this-exercise)
  - [Accept / Retry / Switch / Escalate Logic](#accept--retry--switch--escalate-logic-proposal-for-this-exercise)
  - [Eval Set Design](#eval-set-design-proposal-for-this-exercise)
  - [Regression Suite](#regression-suite-proposal-for-this-exercise)
  - [Metrics and Thresholds for Release](#metrics-and-thresholds-for-release-proposal-for-this-exercise)
  - [Where Automated Evaluation Decides Alone vs. Human Review](#where-automated-evaluation-decides-alone-vs-human-review-proposal-for-this-exercise)
  - [Walkthrough: Example Creative Request 1](#walkthrough-example-creative-request-1--realistic-multi-character-scene)
  - [Walkthrough: Example Creative Request 2](#walkthrough-example-creative-request-2--fantastical-underwater-sequence)
  - [Production Constraints](#production-constraints-proposal-for-this-exercise)

- [3) Measure Improvement and Prevent Regressions](#3-measure-improvement-and-prevent-regressions)
  - [Defining Success](#defining-success-proposal-for-this-exercise)
  - [Primary Quality Metrics](#primary-quality-metrics)
  - [Secondary / Guardrail Metrics](#secondary--guardrail-metrics)
  - [Pass / Fail Thresholds](#pass--fail-thresholds)
  - [Evaluation Slices](#evaluation-slices)
  - [Validating and Calibrating Automated QA](#validating-and-calibrating-automated-qa-proposal-for-this-exercise)
  - [Detecting Evaluator Drift](#detecting-evaluator-drift-proposal-for-this-exercise)
  - [What Counts as a Regression](#what-counts-as-a-regression)
  - [What Blocks Release Even if Aggregate Improves](#what-blocks-release-even-if-aggregate-improves)
  - [Permanent Regression Test Case](#permanent-regression-test-case)

- [Appendix: Reviewed JobIds](#appendix-reviewed-jobids)

- [Use of GenAI Tools](#use-of-genai-tools)

## 0) Relevant Hands-On Experience

### Project 1: Multimodal RAG System for Technical Troubleshooting

#### Context
I worked on a multimodal Retrieval-Augmented Generation (RAG) system designed to assist users in resolving technical errors from large-scale documentation (Word/PDF corpora). The system supports text, audio, and image inputs, and retrieves structured troubleshooting steps grounded in a centralized knowledge base.

#### My Role
My work focused on:
- Designing retrieval and reranking strategies under ambiguity
- Developing prompt-based reasoning layers for document selection
- Building evaluation frameworks to measure groundedness and response quality
- Constructing datasets for supervised fine-tuning and preference learning

---

### Prompting / System Prompting

A key intervention I introduced was a **reasoning-based reranking layer** for document selection (DocID prediction), augmenting embedding-based retrieval.

**Motivation:**
Initial retrieval relied on nearest-neighbor search over embeddings. However, I observed systematic failure modes:
- High embedding similarity across semantically overlapping documents
- Incorrect top-1 retrieval in cases of ambiguous or shared error patterns
- Sensitivity to noise from OCR-extracted inputs

**Intervention:**
I introduced a **few-shot prompted cross-document reasoning step**, where the model evaluates multiple candidate documents jointly and selects the most relevant one. I further experimented with **chain-of-thought prompting** to encourage structured comparison across candidates.

This effectively transformed retrieval from a purely similarity-based process into a **hybrid retrieval + reasoning pipeline**.

---

### Evaluation

I designed a **multi-layered evaluation framework** combining human judgment and automated signals:

- **Human evaluation (primary signal):**
  - Rated outputs on relevance, completeness, and factual grounding

- **LLM-as-judge:**
  - Used structured prompts to verify factual consistency against retrieved documents
  - Explicitly identified hallucinations and unsupported claims

- **Pairwise preference evaluation:**
  - Constructed comparisons between responses to train and validate a reward model

- **Regression suite:**
  - Maintained a curated set of challenging queries (ambiguous, noisy, multimodal)
  - Used for iterative validation across system changes

This setup allowed both **pointwise and comparative evaluation** of system improvements.

---

### Dataset Preparation

I constructed datasets aligned with both **supervised fine-tuning** and **preference learning objectives**.

**Data sources:**
- Real user queries (text, OCR-extracted, and transcribed audio)
- Retrieved document chunks with associated DocIDs
- Model-generated responses

**Curation strategy:**
- Focused on *failure-driven sampling*, including:
  - Ambiguous queries with multiple plausible documents
  - Cross-product error code overlaps
  - Noisy OCR outputs and incomplete inputs

**Preference dataset construction:**
- Transformed scalar ratings into **pairwise comparisons (chosen vs rejected)**
- Ensured diversity across quality gradients rather than only extreme cases

This resulted in a dataset that captures both **typical usage patterns and edge-case failures**.

---

### Metrics

I evaluated system performance using a combination of retrieval and generation metrics:

**Most informative:**
- **Human-rated relevance and completeness**
- **Top-1 DocID accuracy** (retrieval correctness)
- **Pairwise accuracy (reward model)**

**Supporting metrics:**
- Factuality (via LLM-as-judge)
- Embedding similarity scores

**Key insight:**
Embedding similarity alone was insufficient as a proxy for correctness, reinforcing the need for **post-retrieval reasoning and reranking**.

---

### Outcome

- Improved robustness of document selection under ambiguity
- Reduced hallucination rates through stronger grounding
- Increased alignment between retrieved context and generated responses

**Tradeoffs:**
- Increased latency due to additional reasoning steps
- Greater system complexity in orchestration

---

### Reflection

- I would prioritize **evaluation design earlier in the development cycle**, particularly regression suites
- I would explore **hybrid retrieval (lexical + dense)** to mitigate embedding limitations
- I would investigate **learned rerankers** as a more efficient alternative to LLM-based reasoning

**Hands-on vs Hypothesis:**
- Hands-on: prompt design, reranking strategy, dataset construction, evaluation pipelines
- Exploratory: hybrid retrieval strategies, learned reranking models

---

## Project 2: Fine-Tuning and Preference Optimization for Technical QA

#### Context
To improve response quality and alignment, I worked on fine-tuning a large language model using supervised learning (LoRA) and training a reward model for preference-based optimization (RLHF).

#### My Role
I focused on:
- Designing fine-tuning and evaluation datasets
- Developing scoring and evaluation prompts
- Constructing pairwise datasets for reward modeling
- Interpreting evaluation metrics and model behavior

---

### Prompting / System Prompting

I refined the **response generation prompt** to encourage better synthesis across multiple retrieved documents.

**Motivation:**
The base model exhibited:
- Over-reliance on single document chunks
- Incomplete reasoning across multiple sources
- Weak handling of conflicting information

**Intervention:**
I introduced structured instructions emphasizing:
- Multi-document reasoning
- Conflict resolution
- Step-by-step explanation

This improved the model’s ability to **aggregate and reconcile distributed evidence**.

---

### Evaluation

I implemented a combination of:

- **Rubric-based human evaluation**
- **LLM-as-judge for factual verification**
- **Scalar reward scoring (0–1 scale)**
- **Pairwise comparison for preference modeling**

This enabled both **absolute quality assessment** and **relative preference learning**.

---

### Dataset Preparation

**Supervised fine-tuning dataset:**
- (Query, response) pairs grounded in retrieved documents
- Prioritized high-quality, human-reviewed responses

**Reward model dataset:**
- Constructed (prompt, chosen, rejected) triples
- Derived from real outputs with differing quality scores

**Curation focus:**
- Capturing nuanced quality differences (not just obvious failures)
- Ensuring coverage across query types and difficulty levels

---

### Metrics

- **Validation loss (fine-tuning)**
- **Pairwise accuracy (reward model)**
- **Correlation with human ratings (qualitative assessment)**

**Key observation:**
- Loss metrics alone were insufficient; **alignment with human preference** was a more reliable indicator of improvement

---

### Outcome

- Improved response completeness and coherence
- Better alignment with human judgment of quality
- Reduced frequency of partial or underspecified answers

**Tradeoffs:**
- Increased verbosity in some outputs
- Need for tighter prompt constraints to control length

---

### Reflection

- I would more explicitly separate **retrieval vs generation errors** in evaluation
- I would incorporate **automated regression benchmarks earlier**
- I would explore **smaller or specialized models for reranking and evaluation**

**Hands-on vs Hypothesis:**
- Hands-on: dataset construction, prompt design, evaluation setup, reward modeling
- Future work: scaling RLHF and improving efficiency of evaluation loops

---

## 1) Audit the Data and the Current QA

### Data Trust Classification

**Trust:** The structured feedback text (`qaReasoning`, `qaActionableFeedback`) is the most reliable signal in these dumps. It uses a consistent dimensional vocabulary (Characters, Setting, Style, Story, Animation), references specific prompt elements, and provides actionable detail. The `status` field and `modelTitle`/`modelId` are also reliable for filtering and segmentation.

**Treat carefully:** The `qaScore` (1–10) is heavily inflated for images — 81% of scored image jobs receive ≥8, with a mean of 8.41. This makes the score nearly useless for distinguishing "acceptable" from "excellent." Video scores are healthier (mean 6.99, 46% ≥8), but still suffer from score-feedback disagreements: 157 image jobs and 64 video jobs score ≥8 yet carry major negative feedback (e.g., "missing necklace," "facial features deforming"). The `qaTransformedScore` is non-deterministic — `qaScore=4` maps to transformed values {1, 2, 4} across different entries — making it unreliable for any accept/reject logic. Rewritten prompts appear post-hoc: videos *with* rewrites average 6.75, *below* those without (7.64), suggesting the rewrite is generated for lower-quality outputs after scoring, not used as a pre-generation fix.

**Exclude from analysis:** 63% of image entries and 68% of video entries have no QA data at all. Failed/processing/cancelled jobs (222 image + 175 video). At least one `NaN` score and one string-typed transformed score. Test prompts like "A strong feather" (49 repeats) and "An image" (30 repeats) are calibration/test data, not real creative work.

**Issues affecting system design:** (1) Only 10 of 45 image models and 10 of 17 video models have any scored entries — quality signals don't exist for most of the model fleet. (2) Score inflation means an accept threshold based on `qaScore ≥ 8` would pass virtually everything. (3) The QA evaluator penalizes identity verification failures in silhouette and long shots the same way as in close-ups, producing misleading scores for cinematic compositions that intentionally obscure facial detail.

### Specific Job Reviews

**Image 1 — `e268c427` | Nano Banana | qaScore: 3 | Agree with QA**
Prompt asked to add a reference cat character into a scene. QA correctly identified the cat is completely absent — the model ignored the core compositing requirement. *Failure mode:* Nano Banana failed at multi-reference compositing. *Next action:* **switch model** to Shot Image OpenAI or GPT Image 1, both of which score significantly higher on multi-character tasks (8.75 and 8.47 mean vs. Nano Banana's 6.59). *(Proposal for this exercise)*

**Image 2 — `6902b24d` | Shot Image OpenAI | qaScore: 9 | Disagree with QA**
Prompt: "Priya's silhouette framed by the door, entering a dim, cavernous lobby." The QA awards 9/10 but states: "facial details are not visible in the silhouette, making full character identity confirmation difficult." This is contradictory — the QA acknowledges it *cannot verify* character identity yet scores near-perfect. For a production pipeline, an unverifiable identity should either lower the score to 6–7, or the QA should flag this as "low-confidence evaluation" and defer to human review. The evaluator has no shot-type awareness: silhouettes, long shots, and heavy shadows all make identity verification impossible by definition. *Failure mode:* QA rubric doesn't adjust for shot type. *Next action:* **flag for human review** — any evaluation where the QA itself states identity "cannot be confirmed" should auto-escalate. *(Proposal for this exercise)*

**Image 3 — `efd7775c` | GPT Image 1 | qaScore: 8 | Disagree with QA**
Prompt required maintaining character proportions with a car. QA reports: "Differences in facial features and hair from the reference; missing necklace/choker." Missing a signature costume element (the ruby choker) *and* changed facial features are identity-breaking for animation consistency, yet the QA scores 8/10. In a sequential scene workflow, this frame would visually clash with adjacent shots. This should be 5–6. *Failure mode:* QA underweights costume/accessory fidelity. *Next action:* **retry with prompt change** — explicitly name the missing accessory: "Preserve the ruby choker necklace and exact facial features from the reference." *(Proposal for this exercise)*

**Video 1 — `e5406625` | Seedance 1 Pro | qaScore: 3 | Agree with QA**
Prompt explicitly says "no characters present" for an empty moonlit room, but the dog character from the reference image appears in every frame. QA correctly flags this as a complete prompt failure. *Failure mode:* Image-to-video models inherently preserve reference image content; a negative constraint ("no characters") contradicts the reference image itself. *Next action:* **switch approach** — generate a clean environment image first (text-to-image, no character), then animate that. This is a pipeline architecture issue, not just a model issue. *(Proposal for this exercise)*

**Video 2 — `9f2ebf65` | Seedance 1 Pro | qaScore: 8 | Disagree with QA**
Prompt: taxi driver giving a chilling warning as Priya walks away. QA reports: "Facial features and hand positions *intermittently deform*; inconsistent sweat and shifting hair/clothing details." Intermittent face and hand deformation is a severe visual artifact — a creative reviewer would immediately reject this. Scoring 8/10 normalizes a defect that breaks immersion. This should be 5–6. *Failure mode:* QA overweights prompt adherence and underweights visual artifact severity. *Next action:* **retry** — same model, same prompt. Video generation has high variance; a re-roll often produces fewer artifacts. *(Proposal for this exercise)*

**Video 3 — `505debbd` | Seedance 1 Pro | qaScore: 8 | Partially agree**
Prompt: woman in car, minimal motion, cinematic. QA identifies "jawline, mouth, and line thickness fluctuate between frames." Score 8 is borderline fair — the prompt is simple, the scene is largely static, and minor fluctuation is a known video generation limitation. The rewritten prompt correctly adds "Ensure facial features, jawline, and mouth shape remain consistent throughout all frames." *Next action:* **accept conditionally** if best of 2+ attempts; the rewritten prompt should be used for the retry if needed. *(Proposal for this exercise)*

---

## 2) Design V2 of the Workflow

### Model Selection *(proposal for this exercise)*

Route by task complexity and media type, using evidence from the scored data:

- **Images — simple scenes** (<=1 reference, no compositing): GPT Image 1 (mean 8.47, highest volume)
- **Images — multi-character compositing** (>=2 references): Shot Image OpenAI (mean 8.75, best at maintaining multiple character identities)
- **Images — editing/inpainting**: Image Edit OpenAI or Flux Kontext Pro (specialized for edits)
- **Videos — character-driven scenes**: Seedance 1 Pro (most data, mean 7.07) as primary, Hailuo 2.0 (mean 6.98) as fallback
- **Videos — high-motion/action**: Wan 2.2 Fast (handles running/action sequences) or Kling V2.1 (limited data but promising at 6.96)

### Prompt Writing and Rewriting *(proposal for this exercise)*

The rewritten prompt analysis reveals the current system's key insight: original creative prompts lack the stability instructions that generation models need. Rewrites add consistency instructions (16% -> 62%), smooth animation language (12% -> 47%), and facial feature stability (9% -> 35%). V2 should apply these enrichments *before* generation, not after.

**Strategy:** Wrap every user prompt in a system template that injects model-specific stability instructions:

### Revised System Prompt (for Video QA Evaluation)

```
You are evaluating a generated video against its prompt and reference images.

Score each dimension independently from 1 (fail) to 4 (pass):
1. PROMPT_FULFILLMENT: Does the output achieve the core action/scene described?
   - Score 1 if any primary element is missing (character absent, wrong action, wrong setting)
   - Score 4 only if all described elements are present and correctly depicted
2. CHARACTER_IDENTITY: Do characters match their references in face, outfit, and accessories?
   - Score 1 if face is unrecognizable or key costume elements are missing
   - Score 2 if identity can't be verified (silhouette, occlusion) — flag for human review
   - Score 4 only if identity is clear and consistent across all frames
3. VISUAL_QUALITY: Are there artifacts, deformations, flickering, or anatomical errors?
   - Score 1 if faces/hands deform or major artifacts appear
   - Score 4 only if video is artifact-free under normal viewing
4. TEMPORAL_CONSISTENCY: Do character features, lighting, and backgrounds remain stable across frames?
   - Score 1 if identity drifts or features morph noticeably
   - Score 4 only if all elements are frame-to-frame stable

Output a JSON with each dimension score, an overall pass/fail, a confidence level
(high/medium/low), and whether human review is required.

Mark human_review_required=true if:
- Any dimension scores ≤2
- Confidence is "low" (e.g., silhouette shots, heavy occlusion)
- The output is borderline (overall 2.5–3.0 average)
```

This replaces the current single 1–10 score with 4 orthogonal dimensions, adds a confidence signal, and auto-escalates ambiguous cases. *(Proposal for this exercise)*

### Accept / Retry / Switch / Escalate Logic *(proposal for this exercise)*

```
if all_dimensions >= 3 and confidence == "high":
    -> ACCEPT
elif any_dimension == 1:
    if attempt < 2:
        -> RETRY (same model, same prompt + anti-artifact suffix)
    elif attempt < 3:
        -> SWITCH MODEL (use fallback model for same prompt)
    else:
        -> ESCALATE to human review with best-of-3 outputs
elif human_review_required:
    -> ESCALATE to human with QA reasoning attached
else:  # mixed 2s and 3s
    if attempt < 2:
        -> RETRY with rewritten prompt incorporating feedback
    else:
        -> ACCEPT with quality caveat logged
```

Max 3 automated attempts per request. After that, escalate — unbounded retries waste compute and rarely improve results (the 360° camera prompt was tried 22 times with Hailuo 2.0, scores ranging 2–9, still never reliably solved).

### Eval Set Design *(proposal for this exercise)*

**50 test cases**, balanced across these slices:

| Slice | Count | Examples from data |
|-------|-------|--------------------|
| Simple single-character (image) | 8 | "2 persons dancing together" style |
| Multi-character compositing (image) | 8 | Vet + girl + cat scenes with 3–4 refs |
| Character-in-environment edit (image) | 6 | Mercedes car prompt, Priya taxi scenes |
| Fantastical/underwater (image) | 4 | Irina underwater, Formless Black Ooze |
| Negative constraints (video) | 4 | "No characters," "no firing" |
| Static character talking (video) | 6 | Woman in car, vet dialogue |
| High-motion action (video) | 6 | Running man, chase scenes |
| Complex multi-step (video) | 4 | Timed sequences (0–1.5s do X, 1.5–2.5s do Y) |
| Silhouette/dark shots (image+video) | 4 | Priya lobby, night scenes |

Each test case includes: prompt, reference images, expected pass criteria, and the known failure mode it tests.

### Regression Suite *(proposal for this exercise)*

**15 permanent regression tests** drawn from real failures:

1. **Character missing** (`e268c427`): Cat must appear when composited into scene
2. **Negative constraint violation** (`e5406625`): "No characters" must produce empty scene
3. **Costume fidelity** (`efd7775c`): Ruby choker must be preserved
4. **Face deformation** (`9f2ebf65`): No intermittent face/hand warping in video
5. **Identity drift** (`0241e17a`): Character face must remain consistent across all video frames
6. **360° camera** (`e651cc2a`): Camera motion must be perceptible (not static)
7. **Timed sequence** (`29a49029`): Actions must happen in correct time windows
8. **Skin tone preservation** (`88e74340`): Dark grey skin must not shift to lighter tones
9. **Silhouette scoring** (`6902b24d`): QA must flag low-confidence, not score 9/10
10. **Reflection-only framing** (from image data): Must show only reflection, not direct figure
11–15: Additional cases for anatomical correctness, background stability, lip sync, action direction, and accessory preservation.

Every regression test must pass before any pipeline release.

### Metrics and Thresholds for Release *(proposal for this exercise)*

| Metric | Threshold | Blocks release? |
|--------|-----------|-----------------|
| Prompt fulfillment rate (% scoring ≥3 on dim 1) | ≥ 92% | Yes |
| Character identity rate (% scoring ≥3 on dim 2) | ≥ 88% | Yes |
| Visual quality rate (% scoring ≥3 on dim 3) | ≥ 85% images, ≥ 80% video | Yes |
| Temporal consistency (video, % ≥3 on dim 4) | ≥ 78% | Yes |
| Regression suite pass rate | 100% (all 15) | Yes — any single failure blocks |
| Mean retry count per accepted output | ≤ 2.0 | No (guardrail) |
| Human escalation rate | ≤ 15% | No (guardrail, alerts if rising) |

### Where Automated Evaluation Decides Alone vs. Human Review *(proposal for this exercise)*

**Auto-decide:** Clear passes (all dimensions ≥3, high confidence) and clear failures (any dimension =1 with obvious evidence like missing character). These cover ~70% of cases based on the current data distribution.

**Must defer to human:** (1) Silhouette/dark shots where identity can't be verified (~4% of evaluated outputs in the data). (2) Borderline scores (average 2.5–3.0) where the automated judge might be wrong in either direction — the 157 image cases with score ≥8 but major feedback prove this zone exists. (3) Fantastical scenes lacking real-world ground truth (underwater cities, magical ooze). (4) Any case the evaluator itself flags as low-confidence.

### Walkthrough: Example Creative Request 1 — Realistic Multi-Character Scene

**Request:** "A vet talks to Amrita while Mohini (a cat) watches calmly. Wide shot, living room setting."
(Based on real jobs `6702d149`, `3767e33f` in the data.)

- **Model choice:** Shot Image OpenAI (best performer for multi-character, mean 8.75)
- **Prompt strategy:** Use structured prompt with character references explicitly numbered, add camera angle instruction, include scene reference. Append: "Maintain exact facial features, outfit details including accessories, and expression from each character reference."
- **Acceptance rule:** All 4 QA dimensions ≥3. Character identity specifically checks each named character against its reference.
- **Fallback:** Attempt 1 fails -> retry same model with feedback-informed prompt edit (e.g., "Amrita should appear calm, not anxious"). Attempt 2 fails -> try GPT Image 1 as fallback. Attempt 3 fails -> escalate to human with best output.

### Walkthrough: Example Creative Request 2 — Fantastical Underwater Sequence

**Request:** "Beneath the surface, Irina leads Adam by the hand through clear, dark water. Adam struggles to adjust while Irina swims gracefully."
(Based on real jobs `f35481ec`, `81fd40a1` in the data.)

- **Model choice:** Shot Image OpenAI for the key frame image (scored 10 on this exact prompt). For video animation: Seedance 1 Pro with reference image from the key frame.
- **Prompt strategy:** Image — use existing prompt plus "maintain facial detail of both characters from reference." For video — add: "Maintain character proportions, clothing, and skin tone. No sweat droplets (underwater). Ensure smooth, natural swimming motion. Hair and clothing float naturally. Bubbles drift upward consistently."
- **Acceptance rule:** Prompt fulfillment ≥3. Special check: no terrestrial artifacts underwater (sweat, dry hair). Character identity ≥3 for both characters independently.
- **Fallback:** If Seedance 1 Pro produces artifacts -> retry. If identity drifts -> try Hailuo 2.0. Key image is easy (already scored 10); the video is the risk. Max 3 attempts before human escalation.

### Production Constraints *(proposal for this exercise)*

- **Latency:** Cap at 3 retries × generation time. For videos (which take longer), prioritize the first attempt's prompt quality over retry count.
- **Cost:** Route simple prompts to cheaper models (GPT Image 1) and reserve expensive models (Shot Image OpenAI) for complex multi-character scenes.
- **Retry strategy:** Don't retry identical prompts — each retry should incorporate the QA feedback into a revised prompt, as the rewrite analysis shows this adds useful stability instructions.

---

## 3) Measure Improvement and Prevent Regressions

### Defining Success *(proposal for this exercise)*

V2 is successful if: (1) the proportion of outputs accepted on first attempt increases vs. V1 baseline, (2) the regression suite passes 100%, and (3) human reviewers agree with automated QA decisions at ≥85% rate on a calibration sample.

### Primary Quality Metrics

- **Prompt fulfillment rate:** % of outputs where the core described scene/action is present. This is the most trustworthy signal — when the QA says "the cat is missing" or "the man never exits the building," it's unambiguous. *Metric I would trust.*
- **First-attempt acceptance rate:** % of requests accepted without retry. Directly measures prompt and model selection quality.
- **Per-dimension pass rates:** % ≥3 on each of the 4 evaluation dimensions (prompt fulfillment, character identity, visual quality, temporal consistency).

### Secondary / Guardrail Metrics

- **Mean retry count:** Tracks efficiency. Rising retry counts signal degradation even if final acceptance rate holds.
- **Human escalation rate:** Should remain ≤15%. Rising escalation means the automated QA is losing confidence — either the evaluator is drifting or the generation models are producing more ambiguous output.
- **qaScore (1–10):** *Metric I would treat carefully.* The current 1–10 score is too compressed at the top for images (81% ≥8). I would only use it as a secondary signal alongside the 4-dimension breakdown, never as the sole decision metric.
- **Score-feedback agreement rate:** % of jobs where the score direction matches the feedback severity. The current 157 high-score-but-major-feedback cases represent a 5.2% disagreement rate that should shrink, not grow.

### Pass / Fail Thresholds

- **Pass:** All 4 dimensions ≥3 AND confidence = "high" -> auto-accept
- **Fail:** Any dimension = 1 -> auto-reject (retry or escalate)
- **Gray zone:** Mixed 2s and 3s, or confidence = "low" -> human review required

### Evaluation Slices

| Slice | Why track separately |
|-------|---------------------|
| **By reference image count** (0, 1, 2, 3+) | Multi-reference compositing is harder; performance drops sharply |
| **By prompt complexity** (word count buckets) | Timed video sequences (0–1.5s: X, 1.5–2.5s: Y) fail at much higher rates |
| **By shot type** (close-up, wide, silhouette, POV) | Silhouette shots make identity verification impossible — different rubric needed |
| **By motion type** (static, subtle, high-action) | Static talking-head videos score higher; running/action sequences have more artifacts |
| **By model** | Monitor per-model quality; detect model-specific regressions |
| **By content type** (realistic vs. fantastical) | Fantastical scenes lack ground truth for automated scoring |
| **By negative constraints** ("no X" prompts) | Currently fail catastrophically — needs dedicated monitoring |

### Validating and Calibrating Automated QA *(proposal for this exercise)*

**Initial calibration:** Take 100 outputs (stratified across slices), have 3 human reviewers score them on the same 4-dimension rubric. Measure agreement between automated QA and human consensus. The current data suggests the automated QA would have ~80% agreement on clear passes/fails but only ~60% on the gray zone (scores 5–7), where 157 score-feedback disagreements cluster.

**Ongoing calibration:** Weekly, sample 5% of auto-accepted and 5% of auto-rejected outputs for human spot-check. Track the reversal rate (human disagrees with auto decision). If reversal rate exceeds 15%, pause auto-decisions and recalibrate.

### Detecting Evaluator Drift *(proposal for this exercise)*

- **Score distribution monitoring:** Plot weekly histograms. If image scores drift further toward 9–10 (they're already at 81% ≥8), the evaluator is becoming more lenient.
- **Feedback-score divergence:** Track the count of "high score + major feedback" cases. The current 157 (images) and 64 (videos) should decrease, not increase. A rising count means the evaluator is inflating scores while its own reasoning disagrees.
- **Anchor test sets:** Run the 15 regression test cases monthly. These known-answer cases provide a fixed reference point — if the evaluator starts scoring a known failure at 7 instead of 3, it has drifted.
- **Cross-evaluator checks:** Periodically run a second VLM evaluator on the same outputs. If the two evaluators' scores diverge by >2 points on >10% of cases, investigate.

### What Counts as a Regression

Any of: (1) a regression test fails that previously passed, (2) any per-slice pass rate drops >5 percentage points vs. the V1 baseline, (3) human reversal rate exceeds 15%, (4) a new failure mode appears that isn't covered by existing regression tests (in which case, add it).

### What Blocks Release Even if Aggregate Improves

- **Any regression test failure.** Even one. The 360° camera prompt (`e651cc2a`) failed at score 2 (completely static output) — if V2 re-introduces this class of failure, release is blocked regardless of aggregate improvement.
- **Slice-level regression.** If aggregate prompt fulfillment improves from 92% to 94% but the "negative constraints" slice drops from 60% to 40%, that's a release blocker. The `e5406625` failure (dog appearing in "no characters" scene) represents this exact risk.
- **Score-feedback disagreement rate increasing.** If the evaluator becomes more confident but less accurate (fewer flagged errors, but human reviewers find more), that's a silent quality erosion.

### Permanent Regression Test Case

**Job `e5406625`** — "No characters present" prompt produces a video with the dog character in every frame. This tests the fundamental capability of the pipeline to handle negative constraints with image-to-video models. It is currently broken. Any V2 release must solve this class of failure — either by routing negative-constraint prompts to a different pipeline (generate clean image first, then animate) or by using a model that can actually suppress reference image content. This test should never be removed from the regression suite.

---

## Appendix: Reviewed JobIds

| # | jobId | Media | Model | qaScore | QA Agreement | Failure Mode | Recommended Action |
|---|-------|-------|-------|---------|--------------|--------------|--------------------|
| 1 | `e268c427` | Image | Nano Banana | 3 | Agree | Character missing (cat absent) | Switch model |
| 2 | `6902b24d` | Image | Shot Image OpenAI | 9 | **Disagree** (too high) | QA can't verify identity in silhouette | Human review |
| 3 | `efd7775c` | Image | GPT Image 1 | 8 | **Disagree** (too high) | Missing choker + face mismatch | Retry + prompt change |
| 4 | `ab65492a` | Image | Nano Banana | 10 | Agree (trivial) | None (simple prompt inflates scores) | Accept |
| 5 | `e5406625` | Video | Seedance 1 Pro | 3 | Agree | Negative constraint ignored | Switch approach |
| 6 | `9f2ebf65` | Video | Seedance 1 Pro | 8 | **Disagree** (too high) | Face/hand deformation scored as pass | Retry |
| 7 | `505debbd` | Video | Seedance 1 Pro | 8 | Partially agree | Minor jawline flicker (known limitation) | Accept conditionally |
| 8 | `29a49029` | Video | Wan 2.2 Fast | 3 | Agree | Timed sequence actions wrong/missing | Switch model + simplify prompt |
| 9 | `e651cc2a` | Video | Hailuo 2.0 | 3 | Agree | 360° camera -> completely static | Switch model |

---

## Use of GenAI Tools

I used GitHub Copilot as a lightweight utility for two narrow tasks only:

1. **Data parsing helper:** I wrote the analysis scripts myself in Python (pandas, json, collections) to explore the 12,252 entries across both JSON dumps. Copilot assisted with autocompleting boilerplate syntax — e.g., pandas `groupby` chains and `Counter` invocations — while I designed the queries, chose what to measure, and interpreted every result.
2. **Proofreading and formatting:** I used Copilot to check markdown table syntax and catch typos in the final memo. No substantive content was generated by the tool.

**Everything else is my own work:**
- I personally read through hundreds of entries in both dumps, selected the specific jobIds cited, and formed every agree/disagree judgment by reading the QA reasoning against the prompt and feedback.
- The identification of the three core QA weaknesses (score inflation, silhouette blind spot, score-feedback disagreements) came from my own exploratory analysis of the data.
- The 4-dimension evaluation rubric replacing the 1–10 score, the accept/retry/escalate flowchart, the eval set slice design, the regression suite, all thresholds, and both creative walkthroughs are entirely my own proposals.
- The discovery that `qaTransformedScore` is non-deterministic, that rewritten prompts score lower (suggesting post-hoc generation), and that test prompts inflate the dataset — all from my manual investigation.

**Where Copilot's suggestions were unhelpful:** Its automated feedback severity classifier sometimes marked identity-breaking issues as "minor" (e.g., "slight differences in facial features"). In animation production, any facial inconsistency across shots is significant. I overrode these classifications based on my own judgment.

**Labels:** Every major recommendation in this memo is labeled as either *based on hands-on experience* or *proposal/hypothesis for this exercise*.
