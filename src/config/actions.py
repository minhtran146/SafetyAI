"""
actions.py — Custom actions (chỉ giữ RAG)
Jailbreak, PII, Content Safety, Reference Check
→ đã chuyển sang Guardrail Catalog (built-in) trong config.yml
"""

import os
import json
import torch
from nemoguardrails.actions import action
from sentence_transformers import SentenceTransformer, util
from datasets import load_dataset

# ---------------------------------------------------------------------------
# Embedding model — dùng cho RAG
# ---------------------------------------------------------------------------
print("[RAG] Đang load embedding model...")
embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("[RAG] Embedding model sẵn sàng.")

# ---------------------------------------------------------------------------
# WikiText-2 — cache .pt + .json để tránh encode lại mỗi lần khởi động
# ---------------------------------------------------------------------------
_CACHE_DIR        = os.path.join(os.path.dirname(__file__), ".cache")
_CACHE_EMBEDDINGS = os.path.join(_CACHE_DIR, "wiki_embeddings.pt")
_CACHE_PASSAGES   = os.path.join(_CACHE_DIR, "wiki_passages.json")

os.makedirs(_CACHE_DIR, exist_ok=True)

if os.path.exists(_CACHE_EMBEDDINGS) and os.path.exists(_CACHE_PASSAGES):
    print("[RAG] Tìm thấy cache WikiText-2, đang load...")
    WIKI_EMBEDDINGS = torch.load(_CACHE_EMBEDDINGS, weights_only=True)
    with open(_CACHE_PASSAGES, encoding="utf-8") as f:
        WIKI_PASSAGES = json.load(f)
    print(f"[RAG] WikiText-2 từ cache: {len(WIKI_PASSAGES)} đoạn")
else:
    print("[RAG] Chưa có cache, đang tải WikiText-2 toàn bộ...")
    _wikitext = load_dataset("Salesforce/wikitext", "wikitext-2-raw-v1", split="train")
    WIKI_PASSAGES = [t.strip() for t in _wikitext["text"] if len(t.strip()) > 50]
    del _wikitext

    print(f"[RAG] Encoding {len(WIKI_PASSAGES)} đoạn (lần đầu ~60s)...")
    WIKI_EMBEDDINGS = embedder.encode(
        WIKI_PASSAGES,
        convert_to_tensor=True,
        batch_size=64,
        show_progress_bar=True,
    )
    torch.save(WIKI_EMBEDDINGS, _CACHE_EMBEDDINGS)
    with open(_CACHE_PASSAGES, "w", encoding="utf-8") as f:
        json.dump(WIKI_PASSAGES, f, ensure_ascii=False)
    print(f"[RAG] Đã lưu cache tại {_CACHE_DIR}")

# ---------------------------------------------------------------------------
# Knowledge Base nội bộ — thêm tài liệu domain riêng tại đây
# ---------------------------------------------------------------------------
KB_DOCUMENTS = [
    # --- Khoa học / Vật lý ---
    "A black hole is a region of spacetime where gravity is so strong that nothing, not even light, can escape.",
    "Einstein's theory of relativity includes special relativity (1905) and general relativity (1915).",
    "Special relativity states that the speed of light is constant for all observers.",
    "General relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    "The Big Bang theory describes the origin of the universe approximately 13.8 billion years ago.",
    "Quantum mechanics is the branch of physics dealing with the behavior of particles at atomic scales.",
    # --- Công nghệ / Lập trình ---
    "Python is a high-level, interpreted programming language known for readability and versatility.",
    "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
    "Deep learning uses neural networks with many layers to learn representations from raw data.",
    "Natural language processing (NLP) enables computers to understand and generate human language.",
    "An API (Application Programming Interface) allows software components to communicate with each other.",
    "Docker is a platform for developing, shipping, and running applications in containers.",
    "Git is a distributed version control system for tracking changes in source code.",
    # --- Toán học ---
    "The Pythagorean theorem states that in a right triangle, a² + b² = c².",
    "Calculus studies rates of change (derivatives) and accumulation of quantities (integrals).",
    "Linear algebra deals with vector spaces, matrices, and linear transformations.",
    # --- Lịch sử / Địa lý ---
    "The Second World War lasted from 1939 to 1945 and involved most of the world's nations.",
    "The Internet was developed in the late 1960s as ARPANET by the US Department of Defense.",
    "Vietnam is a Southeast Asian country with a population of approximately 98 million people.",
]

print(f"[RAG] Encoding {len(KB_DOCUMENTS)} tài liệu KB nội bộ...")
KB_EMBEDDINGS = embedder.encode(KB_DOCUMENTS, convert_to_tensor=True)
print("[RAG] KB nội bộ sẵn sàng.")

ALL_PASSAGES   = WIKI_PASSAGES + KB_DOCUMENTS
ALL_EMBEDDINGS = torch.cat([WIKI_EMBEDDINGS, KB_EMBEDDINGS], dim=0)
print(f"[RAG] Corpus tổng hợp: {len(ALL_PASSAGES)} đoạn "
      f"(wiki={len(WIKI_PASSAGES)}, kb={len(KB_DOCUMENTS)})")


# ---------------------------------------------------------------------------
# ACTION: RAG Search — tìm top-3 đoạn liên quan, inject vào context
# ---------------------------------------------------------------------------
@action(name="rag_search")
async def rag_search(context: dict) -> str:
    user_message = context.get("user_message", "")
    if not user_message:
        return ""

    query_emb = embedder.encode(user_message, convert_to_tensor=True)
    scores    = util.cos_sim(query_emb, ALL_EMBEDDINGS)[0]

    top_k       = 3
    top_indices = scores.argsort(descending=True)[:top_k].tolist()
    top_scores  = [float(scores[i]) for i in top_indices]

    print(f"[RAG] Top-{top_k} results:")
    retrieved = []
    for idx, score in zip(top_indices, top_scores):
        if score >= 0.3:
            doc = ALL_PASSAGES[idx]
            print(f"  [{score:.3f}] {doc[:70]}")
            retrieved.append(doc)

    if not retrieved:
        print("[RAG] Không tìm thấy tài liệu liên quan")
        return ""

    rag_context = "Relevant information from knowledge base:\n" + "\n".join(
        f"- {doc}" for doc in retrieved
    )
    context["rag_context"] = rag_context
    return rag_context
