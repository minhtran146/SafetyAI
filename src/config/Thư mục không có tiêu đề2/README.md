# NeMo Guardrails — Nâng cấp đầy đủ 6 tầng bảo vệ

## Cấu trúc thư mục

```
.
├── main.py
└── src/
    └── config/
        ├── actions.py      # Custom actions (Python)
        ├── config.yml      # Cấu hình model và flows
        ├── prompts.yml     # Prompt templates
        └── rails.co        # Định nghĩa flows Colang
```

---

## So sánh trước / sau

| Rail | Trước | Sau |
|------|-------|-----|
| Input: Content Safety | ✅ (23 danh mục) | ✅ (giữ nguyên) |
| Input: Jailbreak Protection | ❌ | ✅ Regex + keyword + semantic |
| Input: PII Masking | ❌ | ✅ Email, phone, CCCD, credit card, IP |
| Dialog: Topic Control | Một phần (3 mẫu VI) | ✅ 15+ mẫu, cả VI + EN |
| Output: Content Safety | ✅ | ✅ (giữ nguyên) |
| Output: PII Detection | ❌ | ✅ Mask PII trong response |
| Output: Reference Check | Một phần (WikiText-2, ngưỡng 0.25) | ✅ KB nội bộ, ngưỡng 0.35, bỏ qua câu từ chối |
| RAG | ❌ | ✅ Top-3 retrieval từ KB |

---

## Thứ tự xử lý (Input → Output)

```
Người dùng
    │
    ▼ [INPUT RAILS]
1. check jailbreak          ← Regex + keyword + semantic similarity
2. mask pii input           ← Mask email/phone/CCCD/credit card
3. content safety input     ← LLM chấm 23 danh mục

    │
    ▼ [DIALOG RAILS]
4. politics flow            ← Khớp intent → từ chối cứng
5. dangerous content flow   ← Khớp intent → từ chối cứng
6. rag_search               ← Inject KB context vào prompt

    │
    ▼ [LLM]
    llama-3.3-70b-versatile (Groq)

    │
    ▼ [OUTPUT RAILS]
7. content safety output    ← LLM kiểm tra cả user + response
8. check pii output         ← Mask PII trong câu trả lời
9. validate response        ← Similarity vs KB (ngưỡng 0.35)
```

---

## Mở rộng Knowledge Base

Sửa `KB_DOCUMENTS` trong `actions.py` để thêm tài liệu của domain bạn:

```python
KB_DOCUMENTS = [
    # Thêm tài liệu về sản phẩm, dịch vụ, FAQ...
    "Sản phẩm X hỗ trợ thanh toán qua VNPay và Momo.",
    "Chính sách hoàn tiền áp dụng trong vòng 30 ngày kể từ ngày mua.",
    # ...
]
```

Sau khi thêm, `KB_EMBEDDINGS` sẽ tự được encode lại khi khởi động.

---

## Biến môi trường (.env)

```env
GROQ_API_KEY=gsk_...
```

---

## Cài đặt

```bash
pip install nemoguardrails sentence-transformers python-dotenv
```
