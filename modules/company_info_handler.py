import os
from modules.llm import call_gemini
import difflib

def fuzzy_in(text, keywords, cutoff=0.7):
    text_lower = text.lower()
    for kw in keywords:
        for word in text_lower.split():
            if difflib.SequenceMatcher(None, word, kw.split()[0]).ratio() >= cutoff:
                return True
        if difflib.SequenceMatcher(None, text_lower, kw).ratio() >= cutoff:
            return True
    return False

def get_company_info_dict():
    py_path = os.path.join(os.path.dirname(__file__), "../documents/company_info.py")
    if os.path.exists(py_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("company_info", py_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, "COMPANY_INFO", {})
    return {}

def get_company_info_text():
    txt_path = os.path.join(os.path.dirname(__file__), "../documents/company_info.txt")
    if os.path.exists(txt_path):
        with open(txt_path, encoding="utf-8") as f:
            return f.read()
    info = get_company_info_dict()
    if info:
        return "\n".join(f"{k}: {v}" for k, v in info.items())
    return ""

def handle_company_info_llm(question: str, entities: dict) -> str:
    info_dict = get_company_info_dict()
    info_text = get_company_info_text()
    if not info_text:
        return "Thông tin doanh nghiệp hiện chưa sẵn sàng."
    keywords = ["giới thiệu", "về shop", "về daiboss", "shop là gì", "cửa hàng là gì", "daisan.vn là gì"]
    if fuzzy_in(question, keywords, cutoff=0.7):
        if info_dict.get("gioi_thieu"):
            return info_dict["gioi_thieu"]
        else:
            print("[LOG] Không tìm thấy trường 'gioi_thieu' trong file company_info.py!")
    prompt = (
        "Bạn là trợ lý ảo chuyên nghiệp của DaiBoss/Daisan.vn. "
        "Dựa vào thông tin dưới đây, hãy trả lời chính xác, tự nhiên và ngắn gọn cho câu hỏi sau:\n"
        f"Câu hỏi: {question}\n\n"
        f"Thông tin shop:\n{info_text}\n"
        "Nếu không tìm thấy thông tin, hãy trả lời lịch sự rằng hiện tại chưa có dữ liệu phù hợp."
    )
    answer = call_gemini(prompt)
    return answer or "Xin lỗi, hiện tại tôi chưa có thông tin phù hợp để trả lời câu hỏi này."
