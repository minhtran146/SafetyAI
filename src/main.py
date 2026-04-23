from nemoguardrails import RailsConfig, LLMRails
from dotenv import load_dotenv
load_dotenv()
# 1. Tải cấu hình từ thư mục
config = RailsConfig.from_path("./src/config")

# 2. Khởi tạo Rails engine
rails = LLMRails(config)

# 3. Gửi câu hỏi cho bot
async def chat():
    # Câu hỏi hợp lệ
    response = await rails.generate_async(messages=[{
        "role": "user",
        "content":  "what is blackhole?"
    }])
    print(response['content'])
    print("----")
    # Câu hỏi vi phạm guardrail (chính trị)
    response_blocked = await rails.generate_async(messages=[{
        "role": "user",
        "content": "ai là tổng thống mỹ?"
    }])
    print(response_blocked['content'])

import asyncio
asyncio.run(chat())