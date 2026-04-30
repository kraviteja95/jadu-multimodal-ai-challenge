import json
from collections import Counter

with open('data/qc_results.json') as f:
    img = json.load(f)
with open('data/qc_results_video.json') as f:
    vid = json.load(f)

print(f"Image entries: {len(img)}")
print(f"Video entries: {len(vid)}")

# Unique models
img_models = set(e.get('modelTitle', '?') for e in img)
vid_models = set(e.get('modelTitle', '?') for e in vid)
print(f"\nImage models: {img_models}")
print(f"Video models: {vid_models}")

# Score distributions (handle dict/NaN values)
def safe_score(v):
    if isinstance(v, dict):
        return 'NaN'
    return v

img_scores = Counter(safe_score(e.get('qaScore')) for e in img)
vid_scores = Counter(safe_score(e.get('qaScore')) for e in vid)
img_tscores = Counter(safe_score(e.get('qaTransformedScore')) for e in img)
vid_tscores = Counter(safe_score(e.get('qaTransformedScore')) for e in vid)
print(f"\nImage qaScore dist: {sorted(img_scores.items(), key=lambda x: (str(type(x[0])), str(x[0])))}")
print(f"Video qaScore dist: {sorted(vid_scores.items(), key=lambda x: (str(type(x[0])), str(x[0])))}")
print(f"Image qaTransformedScore dist: {sorted(img_tscores.items(), key=lambda x: (str(type(x[0])), str(x[0])))}")
print(f"Video qaTransformedScore dist: {sorted(vid_tscores.items(), key=lambda x: (str(type(x[0])), str(x[0])))}")

# Status values
print(f"\nImage statuses: {Counter(e.get('status') for e in img)}")
print(f"Video statuses: {Counter(e.get('status') for e in vid)}")

# Videos with rewritten prompt
has_rewritten = sum(1 for e in vid if e.get('qaRewrittenPrompt'))
print(f"\nVideos with rewritten prompt: {has_rewritten}/{len(vid)}")

# Date range
dates_img = [e['createdAt']['$date'] for e in img if 'createdAt' in e]
dates_vid = [e['createdAt']['$date'] for e in vid if 'createdAt' in e]
print(f"Image date range: {min(dates_img)[:10]} to {max(dates_img)[:10]}")
print(f"Video date range: {min(dates_vid)[:10]} to {max(dates_vid)[:10]}")

# Check if images field has reference images
has_refs_img = sum(1 for e in img if e.get('images') and any(x for x in e['images'] if x))
has_refs_vid = sum(1 for e in vid if e.get('images') and any(x for x in e['images'] if x))
print(f"\nImage jobs with reference images: {has_refs_img}/{len(img)}")
print(f"Video jobs with reference images: {has_refs_vid}/{len(vid)}")

# Sample some entries with low/high scores
print("\n=== LOW SCORE EXAMPLES (image, qaScore <= 3) ===")
low_img = [e for e in img if isinstance(e.get('qaScore'), (int, float)) and e['qaScore'] <= 3][:3]
for e in low_img:
    print(f"  jobId={e['jobId']}, model={e['modelTitle']}, qaScore={e['qaScore']}, tScore={e['qaTransformedScore']}")
    print(f"  prompt: {e['prompt'][:100]}...")
    print(f"  feedback: {e.get('qaActionableFeedback', '')[:150]}")
    print()

print("=== HIGH SCORE EXAMPLES (image, qaScore >= 9) ===")
high_img = [e for e in img if isinstance(e.get('qaScore'), (int, float)) and e['qaScore'] >= 9][:3]
for e in high_img:
    print(f"  jobId={e['jobId']}, model={e['modelTitle']}, qaScore={e['qaScore']}, tScore={e['qaTransformedScore']}")
    print(f"  prompt: {e['prompt'][:100]}...")
    print(f"  feedback: {e.get('qaActionableFeedback', '')[:150]}")
    print()
