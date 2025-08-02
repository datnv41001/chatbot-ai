# 📁 modules/agent.py
# Nơi chứa "bộ não" của AI Agent, kết hợp LLM, Tools và Memory.

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache
from dotenv import load_dotenv

# --- Tối ưu hóa: Bật LLM Caching ---
# Điều này sẽ lưu trữ các cặp (prompt, response) vào bộ nhớ.
# Nếu LLM nhận được cùng một prompt, nó sẽ trả về kết quả đã lưu thay vì gọi lại API.
set_llm_cache(InMemoryCache())
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory

from modules.tools import (
    get_product_info, get_product_price, check_product_inventory,
    get_shipping_policy, get_payment_policy, get_return_policy,
    get_warranty_policy, get_promotions, get_opening_hours,
    get_contact_info, get_purchasing_guide, get_company_info
)

load_dotenv()
# 1. Khởi tạo LLM chính cho Agent
# - temperature=0.1 để giảm tính ngẫu nhiên, giúp Agent hoạt động nhất quán hơn.
# - convert_system_message_to_human=True là tham số quan trọng để tương thích tốt hơn với model Gemini.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest", 
    temperature=0.1,
    convert_system_message_to_human=True,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 2. Tập hợp tất cả các công cụ vào một danh sách
tools = [
    get_product_info,
    get_product_price,
    check_product_inventory,
    get_shipping_policy,
    get_payment_policy,
    get_return_policy,
    get_warranty_policy,
    get_promotions,
    get_opening_hours,
    get_contact_info,
    get_purchasing_guide,
    get_company_info
]

# 3. Thiết kế Prompt Template - "Linh hồn" của Agent
# Đây là nơi chúng ta "dạy" AI cách hành xử, suy nghĩ và sử dụng công cụ.
agent_prompt_template = """Bạn là DaiBoss AI, một trợ lý ảo chuyên nghiệp, thông minh và thấu cảm của cửa hàng vật liệu xây dựng DaiBoss.
Nhiệm vụ của bạn là hỗ trợ khách hàng một cách tốt nhất có thể, sử dụng các công cụ có sẵn để cung cấp thông tin chính xác.

CÁC CÔNG CỤ BẠN CÓ THỂ SỬ DỤNG:
Đây là danh sách các công cụ có sẵn: {tool_names}

Đây là mô tả chi tiết về từng công cụ:
{tools}

QUY TRÌNH SUY NGHĨ VÀ HÀNH ĐỘNG:
1.  **Phân tích Yêu cầu:** Đọc kỹ câu hỏi cuối cùng của người dùng (`input`) và toàn bộ `chat_history` để hiểu rõ bối cảnh và ý định thực sự.
2.  **Lựa chọn Công cụ:** Dựa trên yêu cầu, hãy chọn MỘT công cụ phù hợp từ danh sách `tool_names`. Chỉ chọn công cụ khi thực sự cần thông tin. Nếu có thể trả lời từ kiến thức chung hoặc lịch sử trò chuyện, hãy làm vậy.
3.  **Định dạng Action:** Khi dùng công cụ, hãy tuân thủ định dạng sau:
    ```
    Thought: [Suy nghĩ của bạn về bước cần làm]
    Action: [Tên công cụ bạn đã chọn, ví dụ: get_product_price]
    Action Input: [Dữ liệu đầu vào cho công cụ, ví dụ: 'gạch men 30x60']
    ```
4.  **Quan sát và Lặp lại:** Sau khi nhận được `Observation` (kết quả từ công cụ), hãy phân tích nó. Nếu đã đủ thông tin, hãy chuyển sang bước 5. Nếu chưa, hãy lặp lại từ bước 2.
5.  **Tổng hợp và Trả lời:** Khi đã có đủ thông tin, hãy đưa ra câu trả lời cuối cùng cho người dùng. Luôn trả lời bằng tiếng Việt.
    ```
    Thought: Tôi đã có đủ thông tin để trả lời người dùng.
    Final Answer: [Câu trả lời cuối cùng của bạn bằng tiếng Việt]
    ```

GIỌNG ĐIỆU:
-   **Chuyên nghiệp, đáng tin cậy, thân thiện và thấu cảm.**
-   **Chủ động:** Đoán trước nhu cầu của khách hàng và gợi ý các bước tiếp theo.

LỊCH SỬ TRÒ CHUYỆN (quan trọng để hiểu bối cảnh):
{chat_history}

CÂU HỎI CỦA NGƯỜI DÙNG:
{input}

QUÁ TRÌNH SUY NGHĨ CỦA BẠN (bao gồm `tool_names` và `agent_scratchpad`):
{agent_scratchpad}
"""

prompt = PromptTemplate.from_template(agent_prompt_template)

# 4. Khởi tạo Agent
agent = create_react_agent(llm, tools, prompt)

# 5. Tạo Agent Executor với Memory
# Memory cho phép agent "nhớ" các cuộc trò chuyện trước đó.
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=1000, # Giới hạn độ dài của tóm tắt
    memory_key="chat_history",
    return_messages=True
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True, # Bật chế độ log để theo dõi quá trình suy nghĩ của agent
    memory=memory,
    handle_parsing_errors=True # Xử lý lỗi nếu LLM trả về định dạng không đúng
)


