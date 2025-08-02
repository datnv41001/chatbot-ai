from sqlmodel import Session, select
from modules.models import engine, User, ChatHistory, ConversationSummary
from datetime import datetime
import json

# 🧑‍💼 Hàm lưu người dùng nếu chưa tồn tại
def save_user_if_not_exist(user_id, username, email):
    """
    Kiểm tra xem user đã tồn tại trong database chưa.
    Nếu chưa có → lưu mới user vào bảng User.
    """
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()
        if not user:
            session.add(User(id=user_id, username=username, email=email))
            session.commit()


# 💬 Hàm lưu lại 1 lần chat
def save_chat(user_id, question, answer, type="text"):
    """
    Lưu 1 đoạn hội thoại giữa người dùng và chatbot vào bảng ChatHistory.
    """
    with Session(engine) as session:
        session.add(ChatHistory(
            user_id=user_id,
            question=question,
            answer=answer,
            type=type,  # "quick_reply" hoặc "rag"
            timestamp=datetime.utcnow()
        ))
        session.commit()


# 📜 Hàm truy xuất lịch sử hội thoại
def get_chat_history(user_id):
    """
    Trả về danh sách các lần hội thoại của user theo đúng thứ tự thời gian.
    Dùng trong API /history/{user_id}.
    """
    from modules.models import ChatHistory  # ✅ để tránh lỗi vòng lặp import
    with Session(engine) as session:
        results = session.exec(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp)
        ).all()

        return [
            {
                "question": r.question,
                "answer": r.answer,
                "type": r.type,
                "timestamp": str(r.timestamp)
            }
            for r in results
        ]


# 📂 Ghi hoặc cập nhật bản tóm tắt hội thoại vào DB
def save_summary_to_db(session_id, summary):
    summary_str = json.dumps(summary, ensure_ascii=False)  # ✔️ Serialize list to string
    with Session(engine) as session:
        existing = session.exec(
            select(ConversationSummary).where(ConversationSummary.session_id == session_id)
        ).first()
        if existing:
            existing.summary = summary_str
            existing.updated_at = datetime.utcnow()  # ⏱️ Cập nhật thời gian
        else:
            session.add(ConversationSummary(session_id=session_id, summary=summary_str))
        session.commit()


# 🔍 Truy vấn DB để lấy summary nếu có
def load_summary_from_db(session_id):
    with Session(engine) as session:
        summary = session.exec(
            select(ConversationSummary).where(ConversationSummary.session_id == session_id)
        ).first()
        return json.loads(summary.summary) if summary else None