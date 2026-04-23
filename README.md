# SafetyAI

SafetyAI là dự án thử nghiệm kết hợp **NeMo Guardrails** để xây dựng một chatbot AI an toàn, kiểm duyệt nội dung và phòng ngừa các chủ đề nhạy cảm. Dự án tận dụng các API siêu tốc từ **Groq** thông qua chuẩn kết nối của OpenAI.

## Tính năng nổi bật

1. **Lọc Chủ đề (Topical Rails):** Ngăn chặn bot tham gia vào các chủ đề nhạy cảm cụ thể.
2. **Kiểm duyệt Nội dung (Content Safety Rails):** Sử dụng các prompt chuyên sâu để kiểm duyệt cả **Đầu vào (Input)** do người dùng cung cấp và **Đầu ra (Output)** do AI tạo ra, phân loại thành 23 danh mục nội dung không an toàn (bạo lực, tình dục, tự hại, thù ghét, thông tin sai lệch...).
3. **Tích hợp Groq API:** Tận dụng backend Groq với các model LLaMA (như `llama-3.3-70b-versatile`) mang lại độ trễ cực thấp trong việc suy luận cả luồng trò chuyện chính lẫn luồng kiểm duyệt.

## Cấu trúc thư mục

```text
SafetyAI/
├── pyproject.toml              # Quản lý project và dependencies (uv)
├── README.md                   # File tài liệu bạn đang đọc
├── .env                        # Chứa các biến môi trường (API Key) (không push lên git)
└── src/
    ├── main.py                 # File thực thi chính của ứng dụng
    └── config/
        ├── config.yml          # Cấu hình model chính và model safety, luồng Guardrails
        ├── prompts.yml         # Prompts chuyên sâu tùy chỉnh cho content safety check
        └── rails.co            # Định nghĩa các kịch bản/luồng hội thoại của Guardrails (ví dụ chặn chính trị)
```

## Yêu cầu Hệ thống

- Python >= 3.12
- Công cụ quản lý package Python (ví dụ: `uv` hoặc `pip`)
- **Groq API Key** (Đăng ký miễn phí tại [GroqConsole](https://console.groq.com))

## Hướng dẫn cài đặt và Chạy

### 1. Thiết lập biến môi trường

Tạo một file `.env` ở thư mục gốc của dự án (`SafetyAI/.env`) và thêm Groq API Key của bạn vào:

```env
MAIN_MODEL_ENGINE="openai"
MAIN_MODEL_BASE_URL="https://api.groq.com/openai/v1"
OPENAI_API_KEY="gsk_your_groq_api_key_here"
```

*Lưu ý: Mặc dù tên biến là `OPENAI_API_KEY` nhưng chúng ta đang trỏ `base_url` sang Groq nên ở đây bạn sẽ điền key của Groq.*

### 2. Cài đặt thư viện

Dự án sử dụng `uv` làm package manager. Nếu bạn chưa có `uv`, hãy cài đặt nó trước, hoặc có thể dùng `pip`.

Chạy lệnh tự động cài đặt dependency từ `pyproject.toml`:

```bash
uv sync   # (Hoặc dùng `pip install -r requirements.txt` nếu bạn xuất từ toml ra)
```

### 3. Chạy chương trình

Chạy file mã nguồn chính bằng Python (hoặc qua `uv run`):

```bash
uv run src/main.py
```

## Cách thức hoạt động của cấu hình (Config)

- **`config.yml`**: Khai báo 2 model. Cả model chính (`main`) và model kiểm duyệt (`content_safety`) đều sử dụng `llama-3.3-70b-versatile` của Groq. Kích hoạt 2 flow là `content safety check input` và `content safety check output`.
- **`rails.co`**: Chứa ngôn ngữ Colang của NVIDIA NeMo xác định "Hành vi người dùng hỏi về chính trị" và rẽ nhánh sang câu trả lời mặc định là "Xin lỗi, tôi là trợ lý công nghệ và tôi không thể thảo luận về các chủ đề chính trị."
- **`prompts.yml`**: Ghi đè lại prompt mặc định của NeMo để bắt Model Safety trả lời theo định dạng JSON `{"User Safety": "safe/unsafe", ...}`, so sánh câu từ với 23 tiêu chí khắt khe để kết luận. Tránh việc model bị ảo giác và phản hồi sai format.

## Tuỳ chỉnh thêm

- **Thay đổi Model**: Bạn có thể sửa `llama-3.3-70b-versatile` trong `src/config/config.yml` thành các LLM khác đang hỗ trợ trên nền tảng Groq (trừ các mô hình openai/gpt-oss-20b, openai/gpt-oss-120b có vẻ ko tốt)
- **Bổ sung chủ đề cấm**: Mở `src/config/rails.co` và tạo thêm các block `define user ...`, `define bot ...` và `define flow ...` để chặn theo ý muốn tự chọn với ngôn ngữ Colang của NeMo Guardrails.
