# NeMo Guardrails — Refactored dùng Guardrail Catalog

## Cấu trúc thư mục

```
.
├── main.py
└── src/
    └── config/
        ├── actions.py      # Chỉ còn RAG logic
        ├── config.yml      # Guardrail Catalog built-in
        ├── rails.co        # Chỉ còn Topic Control + RAG flow
        └── README.md
```

---

## So sánh trước / sau refactor

| Tầng bảo vệ | Trước (thủ công) | Sau (built-in) | Tiết kiệm |
|---|---|---|---|
| Jailbreak | ~40 dòng Python (regex + keyword + semantic) | `jailbreak detection heuristics` NIM | ✅ Xóa hoàn toàn |
| PII Input | ~20 dòng Python (regex patterns) | `mask sensitive data on input` (Presidio) | ✅ Xóa hoàn toàn |
| PII Output | ~15 dòng Python | `mask sensitive data on output` (Presidio) | ✅ Xóa hoàn toàn |
| Content Safety | ~50 dòng prompts.yml thủ công | `llama guard check input/output` NIM | ✅ Xóa hoàn toàn |
| Reference Check | ~30 dòng Python (cosine similarity) | `self check facts` built-in | ✅ Xóa hoàn toàn |
| Topic Control | Giữ nguyên | Giữ nguyên | — |
| RAG Search | Giữ nguyên | Giữ nguyên | — |

**Kết quả: giảm từ ~250 dòng xuống còn ~50 dòng trong actions.py, xóa hoàn toàn prompts.yml**

---

## Luồng xử lý mới

```
Người dùng
    │
    ▼ [INPUT RAILS — built-in]
1. jailbreak detection heuristics   ← NIM model chuyên biệt
2. mask sensitive data on input     ← Presidio (ML-based)
3. llama guard check input          ← Llama Guard NIM

    │
    ▼ [DIALOG RAILS — custom]
4. politics flow                    ← Topic control nghiệp vụ riêng
5. dangerous content flow           ← Topic control nghiệp vụ riêng
6. rag search and respond           ← Inject KB context

    │
    ▼ [LLM]
    llama-3.3-70b-versatile (Groq)

    │
    ▼ [OUTPUT RAILS — built-in]
7. llama guard check output         ← Llama Guard NIM
8. mask sensitive data on output    ← Presidio
9. self check facts                 ← Fact-check built-in
```

---

## Cài đặt

```bash
# Core
pip install nemoguardrails python-dotenv

# PII — Presidio
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg

# RAG
pip install sentence-transformers datasets torch
```

---

## Biến môi trường (.env)

```env
GROQ_API_KEY=gsk_...
NVIDIA_API_KEY=nvapi_...   # Lấy tại https://build.nvidia.com (free tier có sẵn)
```

---

## Fallback nếu chưa có NVIDIA API Key

Nếu chưa có `NVIDIA_API_KEY`, comment 2 model NIM trong `config.yml` và thêm lại
content safety prompt thủ công từ `prompts.yml` cũ:

```yaml
# config.yml — fallback không dùng NIM
rails:
  input:
    flows:
      - mask sensitive data on input     # Presidio vẫn dùng được
      - content safety check input $model=content_safety   # prompt thủ công
  output:
    flows:
      - content safety check output $model=content_safety
      - mask sensitive data on output
      - self check facts
```

---

## Mở rộng Knowledge Base

Sửa `KB_DOCUMENTS` trong `actions.py`:

```python
KB_DOCUMENTS = [
    "Sản phẩm X hỗ trợ thanh toán qua VNPay và Momo.",
    "Chính sách hoàn tiền áp dụng trong vòng 30 ngày kể từ ngày mua.",
    # ...
]
```
