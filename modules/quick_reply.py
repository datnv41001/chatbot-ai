# modules/quick_reply.py
# ✅ Quick Reply Handler - mapping intent → predefined answers

INTENT_QUICK_REPLIES = {
    "giao_hang": """Chào bạn! Tại DaiBoss, chúng tôi giao hàng toàn quốc từ 1 đến 3 ngày làm việc, tùy khu vực. 
Chúng tôi cam kết mang đến dịch vụ nhanh chóng và đáng tin cậy nhất!""",

    "doi_tra": """Chào bạn! Tại DaiBoss, chúng tôi luôn đặt sự hài lòng của khách hàng lên hàng đầu. 
Bạn có thể đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng nếu sản phẩm còn nguyên tem và chưa qua sử dụng.""",

    "gio_lam_viec": """Chào bạn! DaiBoss hoạt động từ 8h00 đến 21h00 hàng ngày, kể cả cuối tuần để phục vụ khách hàng tốt nhất. 
Bạn có thể ghé thăm cửa hàng bất cứ lúc nào trong khung giờ này nhé!""",

    "bao_hanh": """Chào bạn! Tất cả sản phẩm chính hãng tại DaiBoss đều được bảo hành theo chính sách của nhà sản xuất, tối thiểu 12 tháng. 
Chúng tôi cam kết mang đến những sản phẩm chất lượng nhất!""",

    "thanh_toan": """Chào bạn! Tại DaiBoss, chúng tôi hỗ trợ nhiều hình thức thanh toán tiện lợi: 
tiền mặt khi nhận hàng, chuyển khoản ngân hàng, hoặc qua các ví điện tử. Bạn có thể chọn hình thức phù hợp nhất!""",

    "khuyen_mai": """Chào bạn! DaiBoss thường xuyên có các chương trình khuyến mãi hấp dẫn và giảm giá đặc biệt. 
Bạn có thể theo dõi fanpage hoặc website của chúng tôi để cập nhật những ưu đãi mới nhất nhé!""",

    "lien_he": """Chào bạn! Đội ngũ DaiBoss luôn sẵn sàng hỗ trợ bạn 24/7. 
Bạn có thể liên hệ qua:
- 📞 Hotline: 0123456789
- 📧 Email: daiboss@example.com
- 💬 Facebook: DaiBoss Official
Chúng tôi rất vui được phục vụ bạn!""",

    "kiem_kho": "Bạn muốn kiểm tra sản phẩm nào còn hàng? Vui lòng cung cấp tên hoặc loại sản phẩm."

}


def get_quick_reply(intent: str) -> str:
    """
    Trả về câu trả lời nhanh cho các intent phổ biến.
    Nếu không có thì trả về chuỗi mặc định.
    """
    return INTENT_QUICK_REPLIES.get(
        intent,
        "Xin lỗi, hiện tại tôi chưa có thông tin sẵn cho câu hỏi này. Bạn vui lòng cung cấp thêm chi tiết nhé!"
    )
