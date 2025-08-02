# DaiBoss AI Chatbot - Agent Architecture

Đây là dự án chatbot AI thông minh cho cửa hàng vật liệu xây dựng DaiBoss, được xây dựng với kiến trúc AI Agent mạnh mẽ, sử dụng LangChain và Google Gemini Pro.

## ✨ Tính năng nổi bật

-   **Kiến trúc Agent:** Thay vì các luồng if-else cứng nhắc, chatbot sử dụng một "bộ não" AI (Agent) có khả năng suy luận, lập kế hoạch và tự quyết định hành động.
-   **Sử dụng Công cụ (Tools):** Agent được trang bị một bộ công cụ chuyên dụng (lấy giá, kiểm tra kho, tra cứu chính sách...) để truy xuất thông tin chính xác và tức thời, thay vì dựa vào các file PDF tĩnh.
-   **Trí nhớ Ngữ cảnh:** Tích hợp bộ nhớ đệm tóm tắt cuộc trò chuyện (`ConversationSummaryBufferMemory`), giúp chatbot hiểu sâu sắc toàn bộ lịch sử hội thoại và trả lời một cách tự nhiên, có tính liên kết.
-   **Linh hoạt & Mở rộng:** Dễ dàng thêm các "năng lực" mới cho chatbot chỉ bằng cách tạo thêm các công cụ trong `modules/tools.py`.

## 🚀 Cài đặt và Chạy

### 1. Yêu cầu hệ thống
-   Python 3.9+
-   Google API Key (cho Gemini Pro)

### 2. Hướng dẫn cài đặt

**a. Clone project về máy:**
```bash
git clone <URL_REPOSITORY_CUA_BAN>
cd ten_thu_muc_project
```

**b. (Khuyến khích) Tạo và kích hoạt môi trường ảo:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**c. Cài đặt các thư viện cần thiết:**
```bash
pip install -r requirements.txt
```

**d. Cấu hình biến môi trường:**

Tạo một file mới tên là `.env` trong thư mục gốc của project và thêm vào nội dung sau:
```env
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY_HERE"
```
> **Lưu ý:** Bạn cần có API Key từ Google AI Studio.

### 3. Khởi chạy ứng dụng

Sử dụng lệnh sau để khởi động server FastAPI:
```bash
uvicorn main:app --reload
```
Ứng dụng sẽ chạy tại địa chỉ `http://127.0.0.1:8000`. Bạn có thể truy cập vào đây để xem giao diện API tự động của FastAPI và tương tác với chatbot qua file `test.html`.

## 🏗️ Kiến trúc hệ thống

### Cấu trúc thư mục mới

```
rag_chatbot/
├── main.py                 # FastAPI server, điểm khởi đầu.
├── modules/
│   ├── agent.py            # "Bộ não" của AI: Chứa prompt, memory và agent executor.
│   ├── chatbot.py          # Cầu nối giữa main.py và agent.
│   ├── tools.py            # "Hộp công cụ" của AI, chứa các năng lực cụ thể.
│   └── ...                 # Các module hỗ trợ khác.
├── .env                    # File chứa API key.
├── README.md               # File hướng dẫn này.
└── requirements.txt        # Danh sách các thư viện cần thiết.
```

### Luồng xử lý của AI Agent

1.  **User Input:** `main.py` nhận câu hỏi từ người dùng.
2.  **Invoke Agent:** `chatbot.py` chuyển câu hỏi cho `agent_executor` trong `agent.py`.
3.  **Reasoning (Suy luận):**
    -   Agent nhận câu hỏi và lịch sử trò chuyện.
    -   Dựa trên "linh hồn" (prompt hệ thống), nó suy nghĩ (`Thought`) về cách trả lời.
4.  **Tool Selection (Chọn công cụ):**
    -   Nếu cần thông tin, Agent quyết định chọn một công cụ (`Action`) từ `tools.py` và chuẩn bị dữ liệu đầu vào (`Action Input`).
5.  **Execution & Observation (Thực thi & Quan sát):**
    -   Công cụ được thực thi.
    -   Kết quả (`Observation`) được trả về cho Agent.
6.  **Final Answer (Câu trả lời cuối cùng):**
    -   Agent phân tích kết quả quan sát. Nếu đủ thông tin, nó sẽ tạo ra câu trả lời cuối cùng (`Final Answer`) và gửi lại cho người dùng. Nếu chưa, nó sẽ tiếp tục vòng lặp suy luận.

## 📞 Hỗ trợ

Nếu gặp vấn đề trong quá trình cài đặt hoặc chạy, hãy kiểm tra:
1.  Log lỗi trong terminal nơi bạn chạy lệnh `uvicorn`.
2.  Đảm bảo `requirements.txt` đã được cài đặt đầy đủ trong môi trường ảo.
3.  Chắc chắn rằng `GOOGLE_API_KEY` trong file `.env` là chính xác và còn hiệu lực.