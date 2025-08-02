from sqlmodel import SQLModel, Field, create_engine
from datetime import datetime
from typing import Optional

# 🎯 Khởi tạo kết nối đến database SQLite
# Database sẽ lưu vào file chat.db ở thư mục gốc
engine = create_engine("sqlite:///chat.db")


# 👤 Bảng User - Lưu thông tin người dùng
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)            # ID duy nhất cho mỗi user (dùng session_id làm ID)
    username: str                                # Tên người dùng
    email: Optional[str] = None                  # Email nếu có
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Thời điểm tạo user


# 💬 Bảng ChatHistory - Lưu lịch sử câu hỏi và trả lời của người dùng
class ChatHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # ID tự tăng
    user_id: str                           # Tham chiếu đến User.id
    question: str                          # Câu hỏi mà user gửi
    answer: str                            # Câu trả lời từ chatbot
    type: str = "text"                     # Loại câu trả lời: quick_reply hoặc rag
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # Thời điểm xảy ra hội thoại


# 📦 Model lưu tóm tắt hội thoại
class ConversationSummary(SQLModel, table=True):
    session_id: str = Field(primary_key=True)        # 🔑 ID phiên chat
    summary: str                                     # 💬 Tóm tắt hội thoại
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # ⏱️ Thời gian cập nhật


# 🛠 Hàm khởi tạo database (tạo bảng nếu chưa có)
def init_db():
    SQLModel.metadata.create_all(engine)
