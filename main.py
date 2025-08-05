# main.py
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uuid
import os
from modules.models import init_db
from modules.chatbot import ask_question, init_chatbot
from modules.storage import save_chat, save_user_if_not_exist, get_chat_history
from fastapi.responses import FileResponse


# 🚀 Khởi tạo ứng dụng FastAPI
app = FastAPI()

# 🌍 Cho phép frontend truy cập API từ bất kỳ domain nào (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # hoặc chỉ định ["http://localhost:8080"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 🎯 Khởi tạo hệ thống khi startup
@app.on_event("startup")
async def startup_event():
    init_db()
    init_chatbot() # Khởi tạo chatbot agent

# 📬 Endpoint POST /chat → Nhận câu hỏi và trả lời
@app.post("/chat")
async def chat(
    question: str = Form(...),               # Câu hỏi từ người dùng
    username: str = Form("guest"),           # Tên người dùng
    email: str = Form(""),                   # Email người dùng
    session_id: str = Form(None),            # Session ID (duy trì context)
):
    # 🎯 Nếu không có session_id → sinh session ngẫu nhiên
    session_id = session_id or str(uuid.uuid4())
    user_id = session_id

    # 📌 Lưu người dùng vào DB nếu chưa tồn tại
    save_user_if_not_exist(user_id, username, email)

    # 💡 Gọi AI Agent để xử lý câu hỏi
    result = ask_question(question, session_id)
    answer = result.get("answer", "Rất tiếc, đã có lỗi xảy ra. Vui lòng thử lại.")
    chat_type = result.get("type", "agent_based")

    # 💾 Lưu lịch sử câu hỏi vào DB
    save_chat(user_id, question, answer, chat_type)

    # 🔁 Trả kết quả và session_id cho frontend
    return {"answer": answer, "session_id": session_id}


# 📜 Endpoint GET /history/{session_id} → Trả về lịch sử hội thoại của user
@app.get("/history/{session_id}")
async def history(session_id: str):
    try:
        history = get_chat_history(session_id)
        return JSONResponse(content=history)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
async def serve_frontend():
    return FileResponse("test.html") 

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
