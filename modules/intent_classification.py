"""
Intent Classification module (rule-based + model-ready)
- Classifies user utterances into intents: product_info, product_price, inventory_query, confirm, deny, greeting, faq, fallback, etc.
- Can be swapped out for ML model if needed.
"""
import re

# Intent keyword patterns (expandable)
# Ưu tiên intent sản phẩm lên trên confirm/deny
def _intent_patterns():
    return [
        ("greeting", [r"\b(xin chào|hello|hi|chào bạn|chào)\b"]),
        ("inventory_query", [r"tồn kho|còn hàng|còn bao nhiêu|inventory|stock|số lượng còn|còn không"]),
        ("product_price", [r"giá|bao nhiêu tiền|bao nhiêu|cost|price|giá bán"]),
        ("product_info", [r"thông tin|mô tả|chi tiết|spec|đặc điểm|giới thiệu|miêu tả"]),
        ("product_suggestion", [r"gợi ý sản phẩm|các loại|loại nào tốt|liệt kê|sản phẩm phổ biến|đề xuất|tư vấn chọn|nên mua gì|cho tôi (một|1|vài|mấy|một số) loại|tư vấn sản phẩm"]),
        ("faq", [r"giao hàng|ship|vận chuyển|đổi trả|bảo hành|thanh toán|khuyến mãi|liên hệ|hotline|hướng dẫn mua"]),
        ("confirm", [r"\b(đúng rồi|phải|ok|chuẩn|uh|ừ|ừm|ừ đúng|chính xác|chuẩn rồi)\b"]),
        ("deny", [r"\b(không phải|sai rồi|không đúng|không|chưa|chưa đúng|không phải đâu)\b"]),
    ]
INTENT_PATTERNS = _intent_patterns()


def classify_intent(text: str):
    """
    Classify user utterance into intent.
    Returns (intent, matched_keyword) or (None, None) if not found.
    """
    text = text.lower().strip()
    for intent, patterns in INTENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, text):
                return intent, pat
    # fallback
    return None, None

# Example usage:
if __name__ == "__main__":
    tests = [
        "cho tôi xem giá gạch này",
        "trong kho còn bao nhiêu",
        "thông tin sản phẩm này",
        "đúng rồi",
        "không phải đâu",
        "xin chào",
        "bảo hành thế nào",
        "tôi muốn hỏi về ship",
        "sai rồi",
        "mô tả chi tiết sản phẩm",
    ]
    for t in tests:
        print(f"{t} => {classify_intent(t)}")
