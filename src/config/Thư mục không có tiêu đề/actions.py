from nemoguardrails.actions import action
from datasets import load_dataset
from sentence_transformers import SentenceTransformer, util

print("[SafetyAI] Đang tải WikiText-2...")
wikitext = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")

wiki_passages = [
    t.strip() for t in wikitext["text"]
    if len(t.strip()) > 50
][:300]

print("[SafetyAI] Đang load embedding model...")
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
wiki_embeddings = embedder.encode(wiki_passages, convert_to_tensor=True)
print(f"[SafetyAI] WikiText-2 san sang: {len(wiki_passages)} doan van")

BLOCKED_KEYWORDS = [
    "hack", "tan cong", "vu khi", "malware",
    "sql injection", "ro ri du lieu", "mat khau nguoi khac",
    "danh bom", "phishing", "bypass"
]

@action(name="reference_check")
async def reference_check(response: str) -> bool:
    if not response or len(response.strip()) < 5:
        print("[Reference Check] CHAN — response rong")
        return False
    resp_emb   = embedder.encode(response, convert_to_tensor=True)
    scores     = util.cos_sim(resp_emb, wiki_embeddings)[0]
    best_score = float(scores.max())
    best_idx   = int(scores.argmax())
    print(f"[Reference Check] Similarity: {best_score:.3f}")
    print(f"[Reference Check] Matched: {wiki_passages[best_idx][:80]}")
    if best_score < 0.25:
        print("[Reference Check] CHAN")
        return False
    print("[Reference Check] OK")
    return True
