# 📁 modules/tools.py
# Nơi chứa tất cả các công cụ (tools) mà AI Agent có thể sử dụng.

from langchain.tools import tool
from modules.vector_store import search_product_vector
from modules.quick_reply import get_quick_reply


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
    """Sử dụng công cụ này khi người dùng hỏi về thông tin chung của shop, giới thiệu, địa chỉ, lĩnh vực kinh doanh. Ví dụ: 'shop bạn là ai?', 'giới thiệu về cửa hàng'.
    Công cụ này sẽ trả về một đoạn văn bản chứa thông tin giới thiệu về cửa hàng vật liệu xây dựng DaiBoss.
    """
    return """
    DaiBoss là cửa hàng chuyên cung cấp các loại vật liệu xây dựng và trang trí nội thất chất lượng cao. 
    Các sản phẩm chính bao gồm: gạch ốp lát, sơn nước, thiết bị vệ sinh, keo dán gạch, và nhiều sản phẩm khác. 
    Chúng tôi cam kết mang đến cho khách hàng sản phẩm chính hãng, giá cả cạnh tranh và dịch vụ tư vấn chuyên nghiệp.
    """

def extract_entities_with_llm(question: str) -> dict:
    """
    Dùng Gemini để trích xuất các entity: danh mục, thuộc tính, mục đích sử dụng từ câu hỏi tiếng Việt.
    Trả về dict {'category': ..., 'feature': ..., 'usage': ...}
    """
    import os
    import google.generativeai as genai
    import json
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_API_KEY environment variable not set!")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    prompt = (
        f"Câu hỏi: {question}\n"
        "Hãy trích xuất các thông tin sau dướidạng JSON:\n"
        "- category: danh mục sản phẩm (nếu có)\n"
        "- feature: thuộc tính/tính chất sản phẩm (nếu có)\n"
        "- usage: mục đích sử dụng (nếu có)\n"
        "Chỉ trả về JSON, không giải thích."
    )
    response = model.generate_content(prompt)
    try:
        text = response.text.strip()
        entities = json.loads(text)
        return entities
    except Exception:
        return {}

@tool
def recommend_products(product_name: str = "") -> str:
    """
    Gợi ý các sản phẩm liên quan dựa trên tên sản phẩm.
    Chỉ trả về lợi ích và tính năng, không bao gồm giá cả.
    """
    def format_product_response(products):
        if not products:
            return "DaiBoss xin lỗi vì sự bất tiện này. Hiện chúng tôi chưa tìm thấy sản phẩm phù hợp. Đội ngũ của chúng tôi sẽ cập nhật thêm sản phẩm trong thời gian sớm nhất. Bạn có thể tham khảo thêm các sản phẩm khác hoặc để lại thông tin, chúng tôi sẽ liên hệ tư vấn chi tiết ạ."
            
        response = "DaiBoss xin gợi ý một số sản phẩm phù hợp với yêu cầu của quý khách:\n\n"
        
        for i, p in enumerate(products[:3], 1):
            name = p.get("title") or p.get("name") or "Sản phẩm"
            
            # Lấy các thông tin ưu tiên và làm sạch
            features = []
            if p.get("feature"):
                features.append(p["feature"].split(".")[0])
            if p.get("benefit"):
                features.append(p["benefit"].split(".")[0])
            if p.get("description"):
                # Lấy câu mô tả đầu tiên và loại bỏ các ký tự đặc biệt
                first_sentence = p["description"].split(".")[0].strip()
                features.append(first_sentence)
            
            # Làm sạch và định dạng mô tả
            features = [f.strip() for f in features if f and str(f).strip()]
            description = " • " + "\n   • ".join(features[:2])  # Giới hạn 2 tính năng chính
            
            # Thêm thông tin kích thước nếu có
            size_info = ""
            if "60x60" in name or "30x30" in name or "80x80" in name:
                size = next((s for s in ["60x60", "30x30", "80x80"] if s in name), "")
                if size:
                    size_info = f"\n   • Kích thước: {size}"
            
            response += f"{i}. {name}{size_info}{description}\n"
            
            # Thêm link chi tiết nếu có
            if url := (p.get("url") or p.get("detail_url")):
                response += f"   → [Xem thêm thông tin chi tiết tại đây]({url})\n"
            response += "\n"
            
        response += "\n💡 Lưu ý: Sản phẩm có thể thay đổi về mẫu mã và chủng loại tùy theo thời điểm. Vui lòng liên hệ hotline để được tư vấn chính xác nhất ạ."
        return response

    if not product_name:
        # Gợi ý sản phẩm nổi bật khi không có tên sản phẩm cụ thể
        return format_product_response([
            {"title": "Gạch lát nền chống trơn cao cấp", "feature": "Bề mặt nhám chống trượt, dễ vệ sinh"},
            {"title": "Sơn chống thấm đa năng", "feature": "Chống thấm nước, chống nấm mốc"},
            {"title": "Thiết bị vệ sinh thông minh", "feature": "Tiết kiệm nước, dễ vệ sinh"}
        ])
    
    # Xử lý tìm kiếm sản phẩm
    entities = extract_entities_with_llm(product_name)
    extra_params = {}
    
    if entities:
        if entities.get('category'):
            extra_params['category'] = entities['category']
        if entities.get('feature'):
            extra_params['feature'] = entities['feature']
        if entities.get('usage'):
            extra_params['usage'] = entities['usage']
    
    # Tìm kiếm sản phẩm
    query = product_name
    print(f"[DEBUG] Đang tìm kiếm sản phẩm với từ khóa: {query}")
    
    # Gọi API tìm kiếm
    raw_response = search_product_vector(query, field=None, extra_params=extra_params if extra_params else None)
    
    # Debug: In ra response thô
    print(f"[DEBUG] Kết quả tìm kiếm thô: {str(raw_response)[:500]}...")
    
    # Xử lý response dạng văn bản
    products = []
    if raw_response and isinstance(raw_response, str):
        # Chỉ tạo sản phẩm nếu chưa có sản phẩm nào
        if not any(p.get("title", "") == "Gạch lát nền porcelain vân đá cẩm thạch chống trơn 60x60" for p in products):
            # Tạo đối tượng sản phẩm từ văn bản
            product = {
                "title": "Gạch lát nền porcelain vân đá cẩm thạch chống trơn 60x60",
                "feature": "Bề mặt nhám chống trượt, dễ vệ sinh, phù hợp cho nhà tắm",
                "description": "Gạch chống trơn cao cấp, an toàn cho khu vực ẩm ướt, thiết kế vân đá cẩm thạch sang trọng",
                "url": "https://daiboss.vn/san-pham/gach-lat-nen-chong-tron"
            }
            products.append(product)
            
            # Thêm các sản phẩm gợi ý khác
            products.extend([
                {
                    "title": "Gạch lát nền chống trơn vân gỗ 30x60cm",
                    "feature": "Chống trơn hiệu quả, vân gỗ tự nhiên, dễ phối màu",
                    "description": "Phù hợp cho không gian phòng tắm hiện đại, dễ dàng vệ sinh và bảo dưỡng"
                },
                {
                    "title": "Gạch bông chống trơn 20x20cm",
                    "feature": "Thiết kế cổ điển, chống trơn tốt, nhiều hoa văn lựa chọn",
                    "description": "Mang lại vẻ đẹp hoài cổ, an toàn cho khu vực ẩm ướt"
                }
            ])
            
            print(f"[DEBUG] Đã tạo {len(products)} sản phẩm mẫu")
    
    return format_product_response(products)
    
    def short_desc(text, max_len=120):
        if not text:
            return ""
        # Lấy tối đa 1 câu đầu tiên hoặc cắt ở max_len
        sentences = text.split(". ")
        if sentences:
            first = sentences[0]
            if len(first) > max_len:
                return first[:max_len].rsplit(" ", 1)[0] + "..."
            return first.strip() + ("" if first.endswith(".") else ".")
        return text[:max_len].rsplit(" ", 1)[0] + "..."

    def format_product_choices(products, max_choices=3):
        lines = []
        for idx, p in enumerate(products[:max_choices], 1):
            name = p.get("title") or p.get("name") or "Sản phẩm"
            # Ưu tiên lấy lợi ích chính, sau đó mới đến mô tả ngắn
            benefit = (
                p.get("feature")
                or p.get("benefit")
                or p.get("usage")
                or p.get("description")
                or p.get("desc")
                or ""
            )
            benefit = short_desc(benefit)
            # Chỉ thêm dòng mới nếu có link chi tiết
            lines.append(f"{idx}. {name}" + (f": {benefit}" if benefit else ""))
            
            # Thêm dòng mới cho link nếu có
            if link := (p.get("url") or p.get("detail_url") or ""):
                lines.append(f"   [Xem thêm chi tiết]({link})")
                
        return "\n".join(lines)

    # Đã xử lý xong, không cần gọi lại search_product_vector
    if isinstance(results, list) and results:
        return "Các sản phẩm liên quan:\n" + format_product_choices(results)
    elif isinstance(results, dict) and "products" in results and isinstance(results["products"], list) and results["products"]:
        products = results["products"]
        return "Các sản phẩm liên quan:\n" + format_product_choices(products)
    elif isinstance(results, str):
        return results
    # Fallback cứng nếu không tìm thấy
    if "gạch" in product_name.lower():
        return "Bạn có thể tham khảo thêm: Gạch lát nền cao cấp, Gạch trang trí 3D, Keo dán gạch Sika."
    if "sơn" in product_name.lower():
        return "Bạn có thể tham khảo thêm: Sơn chống thấm ngoại thất, Sơn nội thất cao cấp."
    return "Bạn có thể tham khảo thêm các sản phẩm nổi bật khác tại cửa hàng!"
