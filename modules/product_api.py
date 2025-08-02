import requests
import os
from functools import lru_cache

PRODUCT_API_URL = os.getenv("PRODUCT_API_URL", "http://localhost:8000/api/products")


@lru_cache(maxsize=128)
def get_product_info(product_name=None, field=None, extra_params=None):
    """
    Truy vấn thông tin sản phẩm từ API sản phẩm.
    Nếu có product_name: trả về mô tả chi tiết sản phẩm.
    Nếu không: trả về danh mục sản phẩm nổi bật.
    Nếu field: lọc trường cụ thể (vd: price, info, inventory...)
    extra_params: dict các tham số bổ sung (brand, color, size...)
    """
    try:
        params = {}
        if product_name:
            params['name'] = product_name
        if field:
            params['field'] = field
        if extra_params:
            params.update(extra_params)
        resp = requests.get(PRODUCT_API_URL, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if product_name and data:
                # Có thể tùy chỉnh format trả về cho từng field
                if field and field in data:
                    return data[field]
                # Nếu không có field cụ thể, trả về mô tả tổng hợp
                desc = data.get('description') or data.get('info')
                price = data.get('price')
                stock = data.get('inventory')
                brand = data.get('brand')
                result = f"Sản phẩm '{product_name}'"
                if brand:
                    result += f" (thương hiệu {brand})"
                if desc:
                    result += f"\nMô tả: {desc}"
                if price:
                    result += f"\nGiá: {price:,} VNĐ"
                if stock is not None:
                    result += f"\nTồn kho: {stock}"
                return result
            elif not product_name and isinstance(data, list):
                # Trả về danh mục sản phẩm
                names = [item.get('name', '') for item in data]
                names = [n for n in names if n]
                if names:
                    return "Danh mục sản phẩm nổi bật: " + ", ".join(names)
                else:
                    return "Không tìm thấy danh mục sản phẩm nào."
            else:
                return "Không tìm thấy thông tin sản phẩm phù hợp."
        else:
            return f"Lỗi truy vấn API sản phẩm: {resp.status_code}"
    except Exception as e:
        return f"Không kết nối được tới hệ thống sản phẩm. Vui lòng thử lại sau. ({e})"
