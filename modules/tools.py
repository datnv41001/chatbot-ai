# 📁 modules/tools.py
# Nơi chứa tất cả các công cụ (tools) mà AI Agent có thể sử dụng.

from langchain.tools import tool
from modules.vector_store import search_product_vector
from modules.quick_reply import get_quick_reply
from modules.company_info_handler import handle_company_info_llm

@tool
def get_product_info(product_name: str) -> str:
    """Sử dụng công cụ này khi người dùng hỏi thông tin chi tiết, mô tả, hoặc đặc điểm của một sản phẩm cụ thể. 
    Ví dụ: 'gạch này có chống thấm không?', 'mô tả gạch bóng kiếng'.
    Đầu vào là tên sản phẩm (product_name)."""
    return search_product_vector(product_name, field="info") or "Tôi chưa tìm thấy thông tin cho sản phẩm này."

@tool
def get_product_price(product_name: str) -> str:
    """Sử dụng công cụ này khi người dùng hỏi về giá của một sản phẩm cụ thể.
    Ví dụ: 'giá gạch này bao nhiêu?', 'xi măng bao nhiêu tiền một bao'.
    Đầu vào là tên sản phẩm (product_name)."""
    return search_product_vector(product_name, field="price") or "Tôi chưa tìm thấy giá cho sản phẩm này."

@tool
def check_product_inventory(product_name: str) -> str:
    """Sử dụng công cụ này khi người dùng hỏi về tình trạng tồn kho, 'còn hàng không' của một sản phẩm cụ thể.
    Ví dụ: 'gạch này còn hàng không?', 'kiểm tra kho gạch ABC'.
    Đầu vào là tên sản phẩm (product_name)."""
    return search_product_vector(product_name, field="inventory") or "Tôi chưa thể kiểm tra tồn kho cho sản phẩm này."

@tool
def get_shipping_policy(query: str = "chính sách giao hàng") -> str:
    """Sử dụng khi người dùng hỏi về chính sách giao hàng, phí ship, thời gian giao hàng."""
    return get_quick_reply("giao_hang")

@tool
def get_payment_policy(query: str = "chính sách thanh toán") -> str:
    """Sử dụng khi người dùng hỏi về các phương thức thanh toán, COD, chuyển khoản."""
    return get_quick_reply("thanh_toan")

@tool
def get_return_policy(query: str = "chính sách đổi trả") -> str:
    """Sử dụng khi người dùng hỏi về chính sách đổi trả sản phẩm."""
    return get_quick_reply("doi_tra")

@tool
def get_warranty_policy(query: str = "chính sách bảo hành") -> str:
    """Sử dụng khi người dùng hỏi về chính sách bảo hành."""
    return get_quick_reply("bao_hanh")

@tool
def get_promotions(query: str = "chương trình khuyến mãi") -> str:
    """Sử dụng khi người dùng hỏi về các chương trình khuyến mãi, giảm giá hiện có."""
    return get_quick_reply("khuyen_mai")

@tool
def get_opening_hours(query: str = "giờ làm việc") -> str:
    """Sử dụng khi người dùng hỏi về giờ mở cửa, lịch làm việc của cửa hàng."""
    return get_quick_reply("gio_lam_viec")

@tool
def get_contact_info(query: str = "thông tin liên hệ") -> str:
    """Sử dụng khi người dùng hỏi về thông tin liên hệ, số điện thoại, hotline, email."""
    return get_quick_reply("lien_he")

@tool
def get_purchasing_guide(query: str = "hướng dẫn mua hàng") -> str:
    """Sử dụng khi người dùng hỏi về cách mua hàng, quy trình đặt hàng."""
    return get_quick_reply("quy_trinh_mua")

@tool
def get_company_info(query: str) -> str:
    """Sử dụng khi người dùng hỏi thông tin chung về công ty, cửa hàng, 'shop bán gì', 'bạn là ai'."""
    return handle_company_info_llm(query, {})
