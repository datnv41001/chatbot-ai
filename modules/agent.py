# 📁 modules/agent.py
# Nơi chứa "bộ não" của AI Agent, kết hợp LLM, Tools và Memory.

import os
from modules.langchain_timing_callback import TimingCallbackHandler
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
    get_contact_info, get_purchasing_guide, get_company_info,
    recommend_products
)

load_dotenv()
# 1. Khởi tạo LLM chính cho Agent
# - temperature=0.1 để giảm tính ngẫu nhiên, giúp Agent hoạt động nhất quán hơn.
# - convert_system_message_to_human=True là tham số quan trọng để tương thích tốt hơn với model Gemini.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest", 
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    callbacks=[TimingCallbackHandler()]
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
    get_company_info,
    recommend_products
]

# 3. Thiết kế Prompt Template - "Linh hồn" của Agent
# Đây là nơi chúng ta "dạy" AI cách hành xử, suy nghĩ và sử dụng công cụ.
agent_prompt_template = """
Bạn là DaiBoss AI, trợ lý ảo thân thiện của cửa hàng vật liệu xây dựng DaiBoss.
Nhiệm vụ: Hỗ trợ khách hàng chính xác, ngắn gọn, sử dụng công cụ phù hợp khi cần.

Công cụ khả dụng: {tool_names}
{tools}

Quy trình:
1. Đọc kỹ câu hỏi (`input`) và lịch sử chat gần nhất (`chat_history`, chỉ 3-5 lượt gần nhất).
2. Nếu trả lời được từ kiến thức chung hoặc lịch sử, hãy trả lời ngay (không cần công cụ).
3. Nếu người dùng hỏi về các loại sản phẩm, sản phẩm phổ biến, gợi ý sản phẩm, đề xuất sản phẩm, tư vấn chọn sản phẩm, hoặc dùng các từ như "các loại", "gợi ý", "nên mua gì", "loại nào tốt"... thì LUÔN ưu tiên sử dụng công cụ recommend_products với từ khóa sản phẩm chính (ví dụ: "gạch ceramic"). Nếu không chắc từ khóa, hãy hỏi lại người dùng để xác định sản phẩm cần gợi ý.
4. Nếu cần thông tin khác, chọn đúng 1 công cụ phù hợp, format:
    Thought: [Suy nghĩ]
    Action: [Tên công cụ]
    Action Input: [Dữ liệu đầu vào]
5. Khi đủ thông tin, format:
    Thought: Đã đủ thông tin.
    Final Answer: [Trả lời ngắn gọn, tiếng Việt]

Giọng điệu: Chuyên nghiệp, thân thiện, chủ động.
Chỉ trả lời đúng trọng tâm, không lan man.

Lịch sử hội thoại:
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
    max_token_limit=700,  # Giới hạn độ dài tóm tắt, chỉ giữ 3-5 lượt gần nhất
    memory_key="chat_history",
    return_messages=True
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,  # Có thể chỉ truyền tool liên quan nếu xác định intent trước đó
    verbose=False,  # Tắt log chi tiết khi đã ổn định
    memory=memory,
    handle_parsing_errors=True,
    max_iterations=4  # Giới hạn số vòng lặp để tránh agent loop vô hạn
)


