# 📁 File: modules/chatbot.py

import os
from dotenv import load_dotenv

from modules.agent import agent_executor

# Biến toàn cục để kiểm tra trạng thái khởi tạo
is_initialized = False

def init_chatbot():
    """
    Khởi tạo các thành phần cần thiết cho chatbot hoạt động.
    Trong kiến trúc Agent, việc này chủ yếu là load biến môi trường
    và khởi tạo Vector Store cho các công cụ sử dụng.
    Agent và LLM sẽ được khởi tạo lazy khi cần.
    """
    global is_initialized
    if is_initialized:
        print("🤖 Chatbot đã được khởi tạo trước đó.")
        return

    print("🔥 Khởi tạo hệ thống Chatbot Agent...")
    
    # 1. Load biến môi trường (quan trọng nhất là GOOGLE_API_KEY)
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ LỖI: GOOGLE_API_KEY không được tìm thấy. Vui lòng kiểm tra file .env")
        is_initialized = False
        return
    print("✅ Biến môi trường đã được tải.")

    # Vector Store không cần khởi tạo ở đây nữa.
    # Các tools sẽ tự truy cập API hoặc nguồn dữ liệu khi cần.

    is_initialized = True
    print("🎉 Chatbot Agent đã sẵn sàng!")


def ask_question(question: str, session_id: str):
    """
    Hàm xử lý câu hỏi chính.
    Chuyển tiếp câu hỏi trực tiếp đến AI Agent để xử lý.
    """
    if not is_initialized:
        return {
            "answer": "Xin lỗi, hệ thống chưa được khởi tạo thành công. Vui lòng kiểm tra lại cấu hình.",
            "type": "error_not_initialized"
        }
    
    try:
        # Sử dụng agent_executor đã có memory để xử lý
        # session_id sẽ được dùng để quản lý memory sau này
        response = agent_executor.invoke(
            {"input": question},
            config={"configurable": {"session_id": session_id}}
        )
        answer = response.get("output", "Xin lỗi, tôi chưa có câu trả lời cho vấn đề này.")
        return {"answer": answer, "type": "agent_based"}
    except Exception as e:
        print(f"❌ Lỗi trong quá trình Agent thực thi: {e}")
        return {
            "answer": "Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại sau.",
            "type": "error_agent_execution"
        }
        context_mgr.update_summary()
        return {"answer": answer, "type": "about_bot"}
    if any(kw in q_lower for kw in ["xin chào", "hello", "hi"]):
        answer = "Xin chào bạn 👋 Tôi là trợ lý ảo của DaiBoss. Bạn cần hỗ trợ gì hôm nay?"
        context_mgr.remember(intent="greeting", question=question, bot_message=answer)
        context_mgr.update_summary()
        return {"answer": answer, "type": "greeting"}

    fallback = "Xin lỗi, tôi chưa rõ ý bạn hỏi. Tôi là trợ lý ảo chuyên tư vấn sản phẩm và dịch vụ của DaiBoss. Bạn có thể hỏi về sản phẩm, giá, chính sách đổi trả, bảo hành, giao hàng, hoặc các ưu đãi hiện có."
    context_mgr.remember(intent="khac", question=question, bot_message=fallback)
    context_mgr.update_summary()
    return {"answer": fallback, "type": "fallback_ai"}