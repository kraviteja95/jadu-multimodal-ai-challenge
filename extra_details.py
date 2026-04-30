"""Pull additional specific job details needed for the memo sections 2 & 3."""
import json

with open("data/qc_results.json") as f:
    img = json.load(f)
with open("data/qc_results_video.json") as f:
    vid = json.load(f)

def ss(v):
    return None if isinstance(v, dict) else v

# For Section 2 walkthrough: find a fantastical prompt example
print("=== FANTASTICAL / CREATIVE PROMPTS (image) ===")
for e in img:
    p = (e.get("prompt") or "").lower()
    if ss(e.get("qaScore")) and ss(e.get("qaScore")) >= 8 and any(kw in p for kw in ["underwater", "dragon", "fantasy", "magic", "ooze", "formless"]):
        print(f"  jobId: {e['jobId']}")
        print(f"  Model: {e['modelTitle']}, Score: {ss(e['qaScore'])}")
        print(f"  Prompt: {(e.get('prompt') or '')[:250]}")
        print(f"  Feedback: {e.get('qaActionableFeedback','')[:200]}")
        print()
        break

# For Section 2: find a multi-character scene with reference images
print("=== MULTI-CHARACTER WITH REFS (image) ===")
count = 0
for e in img:
    p = (e.get("prompt") or "").lower()
    refs = [x for x in (e.get("images") or []) if x]
    if ss(e.get("qaScore")) and len(refs) >= 3 and ("character" in p or "vet" in p or "together" in p):
        print(f"  jobId: {e['jobId']}")
        print(f"  Model: {e['modelTitle']}, Score: {ss(e['qaScore'])}")
        print(f"  Refs: {len(refs)}")
        print(f"  Prompt: {(e.get('prompt') or '')[:250]}")
        print(f"  Feedback: {e.get('qaActionableFeedback','')[:200]}")
        print()
        count += 1
        if count >= 2:
            break

# For Section 2: video walkthrough - running man chase scene
print("=== ACTION VIDEO (running/chase) ===")
count = 0
for e in vid:
    p = (e.get("prompt") or "").lower()
    if ss(e.get("qaScore")) and ("sprint" in p or "runs forward" in p) and ss(e.get("qaScore")) >= 7:
        print(f"  jobId: {e['jobId']}")
        print(f"  Model: {e['modelTitle']}, Score: {ss(e['qaScore'])}")
        print(f"  Prompt: {(e.get('prompt') or '')[:250]}")
        print(f"  Feedback: {e.get('qaActionableFeedback','')[:200]}")
        print(f"  Rewrite: {(e.get('qaRewrittenPrompt') or '')[:200]}")
        print()
        count += 1
        if count >= 2:
            break

# For the silhouette job referenced in findings - get full details
print("=== SILHOUETTE JOB FULL DETAIL ===")
for e in img:
    if e["jobId"] == "6902b24d-2474-46bc-8064-41bffa9d87e1":
        print(json.dumps(e, indent=2)[:2000])
        break

# For Section 3: find a video with score variance on same prompt
print("\n=== 360-DEGREE CAMERA RETRY GROUP ===")
for e in vid:
    p = (e.get("prompt") or "")
    if p.startswith("Still life, Camera sliding 360") and ss(e.get("qaScore")):
        print(f"  jobId: {e['jobId']}, Score: {ss(e['qaScore'])}, Model: {e['modelTitle']}")
        print(f"  Feedback: {e.get('qaActionableFeedback','')[:150]}")
        print()

# Check the specific image job with score 8 and "not fulfilled" feedback
print("=== SCORE 8 BUT STORY NOT FULFILLED ===")
for e in img:
    fb = e.get("qaActionableFeedback", "").lower()
    if ss(e.get("qaScore")) == 8 and "not fulfilled" in fb:
        print(f"  jobId: {e['jobId']}")
        print(f"  Model: {e['modelTitle']}")
        print(f"  Prompt: {(e.get('prompt') or '')[:200]}")
        print(f"  Reasoning: {e.get('qaReasoning','')[:300]}")
        print(f"  Feedback: {e.get('qaActionableFeedback','')[:300]}")
        print()
        break

# Irina underwater scene - a good fantastical example
print("=== UNDERWATER/FANTASTICAL SCENES ===")
count = 0
for e in img:
    p = (e.get("prompt") or "").lower()
    if ss(e.get("qaScore")) and ("underwater" in p or "irina" in p.lower()):
        print(f"  jobId: {e['jobId']}")
        print(f"  Model: {e['modelTitle']}, Score: {ss(e['qaScore'])}")
        print(f"  Prompt: {(e.get('prompt') or '')[:300]}")
        print(f"  Feedback: {e.get('qaActionableFeedback','')[:200]}")
        print()
        count += 1
        if count >= 3:
            break
