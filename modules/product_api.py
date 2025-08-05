import requests
import os
from functools import lru_cache

PRODUCT_API_URL = os.getenv("PRODUCT_API_URL", "https://unopim.daisan.asia/api/shopify/get-product-with-inventory")


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
            params['title'] = product_name
        if field:
            params['field'] = field
        if extra_params:
            params.update(extra_params)
        resp = requests.get(PRODUCT_API_URL, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # Trường hợp API trả về danh sách sản phẩm trong 'products'
            products = data.get('products') if isinstance(data, dict) else None
            if products and isinstance(products, list):
                # Tìm sản phẩm phù hợp nhất với product_name (ưu tiên match gần đúng)
                def match(p):
                    return product_name.lower() in p.get('title', '').lower()
                product = next((p for p in products if match(p)), products[0] if products else None)
                if product:
                    title = product.get('title', 'Không rõ tên sản phẩm')
                    image = product.get('image')
                    description = product.get('description', '').strip()
                    # Nếu description là HTML, lấy nội dung chính
                    if description and ('<' in description):
                        import re
                        description = re.sub('<[^<]+?>', '', description)
                        description = description.replace('\n', ' ').replace('  ', ' ').strip()
                    variants = product.get('variants', [])
                    price = None
                    stock_info = []
                    sku = None
                    if variants:
                        v = variants[0]
                        price = v.get('price')
                        sku = v.get('sku')
                        inventory = v.get('inventory', [])
                        for inv in inventory:
                            loc = inv.get('location_name')
                            qty = inv.get('available')
                            if loc and qty is not None:
                                stock_info.append(f"{qty} tại {loc}")
                    # Xử lý trả về đúng field nếu có
                    if field == "price":
                        return price or "Không có thông tin giá."
                    elif field == "inventory":
                        if stock_info:
                            return ", ".join(stock_info)
                        return "Không có thông tin tồn kho."
                    elif field == "info":
                        return description or "Không có mô tả sản phẩm."
                    # Nếu không truyền field, trả về tổng hợp
                    advantage = ''
                    if description:
                        for line in description.split('\n'):
                            if 'ưu điểm' in line.lower() or 'điểm nổi bật' in line.lower():
                                advantage = line.strip()
                    result = f"Sản phẩm: {title}"
                    if sku:
                        result += f" (Mã: {sku})"
                    if price:
                        result += f"\nGiá: {price} VNĐ"
                    if stock_info:
                        result += f"\nTồn kho: {', '.join(stock_info)}"
                    if image:
                        result += f"\nHình ảnh: {image}"
                    if description:
                        result += f"\nMô tả: {description}"
                    if advantage:
                        result += f"\nƯu điểm: {advantage}"
                    return result
                else:
                    return "Không tìm thấy thông tin sản phẩm phù hợp."
            elif product_name and isinstance(data, dict):
                # Trường hợp API trả về 1 sản phẩm duy nhất
                desc = data.get('description') or data.get('info')
                price = data.get('price')
                stock = data.get('inventory')
                brand = data.get('brand')
                if field == "price":
                    return price or "Không có thông tin giá."
                elif field == "inventory":
                    return stock or "Không có thông tin tồn kho."
                elif field == "info":
                    return desc or "Không có mô tả sản phẩm."
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
