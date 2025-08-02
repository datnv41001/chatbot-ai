# modules/vector_store.py
"""
Truy vấn sản phẩm qua API sản phẩm, không còn dùng FAISS/vectorstore.
"""
from modules.product_api import get_product_info

def search_product_vector(product_name, index=None, field=None, extra_params=None):
    """
    Truy vấn sản phẩm qua API. Các tham số:
    - product_name: tên sản phẩm cần tìm
    - field: trường thông tin cụ thể (info, price, inventory...)
    - extra_params: dict các tham số bổ sung (brand, color, size...)
    """
    return get_product_info(product_name=product_name, field=field, extra_params=extra_params)
