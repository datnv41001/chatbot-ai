# modules/entities.py
import re

def extract_entities(text: str) -> dict:
    text = text.lower()
    entities = {}

    # 🧱 Tên sản phẩm - bao phủ nhiều loại vật liệu hơn
    PRODUCT_PATTERN = r"""
        (gạch(?:\s?(viglacera|taicera|ceramic|men|bóng kiếng|đá granite|trang trí|lát nền|ốp tường|thẻ|bông))?|
        ximăng|xi măng|cát|sỏi|đá(?:\s?(1x2|4x6|mi bụi|mi sàng))?|
        keo dán|vữa|chống thấm|bột trét|sơn(?:\s?(nước|dầu))?|ống nước|thiết bị vệ sinh|bồn cầu|lavabo)
    """
    product_match = re.findall(PRODUCT_PATTERN, text, re.VERBOSE)
    if product_match:
        entities["product"] = list({p[0].strip() for p in product_match if p[0]})

    # 🎨 Màu sắc - bao gồm màu mô tả và mã màu
    COLOR_PATTERN = r"""
        (trắng|xám|đen|vàng|be|xanh|nâu|hoa văn|vân đá|vân gỗ|xanh rêu|xanh ngọc|
        mã\s?(màu)?\s?\d{2,4}|màu\s?[a-zA-Z0-9]+)
    """
    color_match = re.findall(COLOR_PATTERN, text, re.VERBOSE)
    if color_match:
        entities["color"] = list(set(color_match))

    # 📏 Kích thước - dạng 60x60, 30x60cm, 600x600...
    SIZE_PATTERN = r"(\d{2,3}\s?[xX]\s?\d{2,3}(?:\s?cm|mm)?)"
    size_match = re.findall(SIZE_PATTERN, text)
    if size_match:
        entities["size"] = list(set(size_match))

    # 🔢 Số lượng
    QUANTITY_PATTERN = r"(\d{1,4})\s?(viên|m2|mét vuông|bao|thùng|tấn|kg|bịch|mét|m3|mét khối)"
    quantity_match = re.findall(QUANTITY_PATTERN, text)
    if quantity_match:
        entities["quantity"] = [" ".join(q) for q in quantity_match]

    # 💵 Giá tiền
    PRICE_PATTERN = r"(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?|\d+[.,]?\d*)\s?(k|nghìn|triệu|vnd|đ|vnđ)"
    price_match = re.findall(PRICE_PATTERN, text)
    if price_match:
        entities["price"] = ["".join(p).strip() for p in price_match]

    # 🏷️ Thương hiệu (brand) - nếu có
    BRAND_PATTERN = r"(viglacera|taicera|kingstone|hải long|prime|dong tam|nhựa bình minh)"
    brand_match = re.findall(BRAND_PATTERN, text)
    if brand_match:
        entities["brand"] = list(set(brand_match))

    return entities