"""
Entity Linking service module
- Độc lập với context_manager, chỉ nhận vào text + product_history (list[dict])
- Trả về product entity được resolve (dict) hoặc None
- Dùng để test/tích hợp riêng, dễ unit test
"""
from typing import List, Dict, Optional
import re

REFERENCE_KEYWORDS = ["ý", "trên", "đó", "này", "sp trên", "sp đó", "sản phẩm trên", "sản phẩm đó", "nó"]


def resolve_product_reference(text: str, product_history: List[Dict]) -> Optional[Dict]:
    """
    Liên kết entity tham chiếu trong text với product_history.
    - Nếu text chứa từ khóa tham chiếu (ví dụ: "nó", "trên", ...), trả về entity phù hợp.
    - Nếu không, trả về None.
    """
    text = text.lower()
    for ref in REFERENCE_KEYWORDS:
        if ref in text:
            # Nếu ref là "trên" và có >=2 sản phẩm
            if ref in ["trên", "sp trên", "sản phẩm trên"] and len(product_history) >= 2:
                return sorted(product_history, key=lambda x: -x['turn'])[1]
            # Nếu ref là "nó", "đó", "này"... lấy sản phẩm gần nhất
            if product_history:
                return sorted(product_history, key=lambda x: -x['turn'])[0]
    return None

# Example test
if __name__ == "__main__":
    phist = [
        {"name": "Gạch A", "turn": 1},
        {"name": "Gạch B", "turn": 2},
    ]
    print(resolve_product_reference("tồn kho nó còn không", phist))
    print(resolve_product_reference("giá sp trên", phist))
