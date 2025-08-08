# 📁 File: modules/chatbot.py

import os
from dotenv import load_dotenv

from modules.agent import agent_executor
from modules.langchain_timing_callback import TimingCallbackHandler

# Biến toàn cục để kiểm tra trạng thái khởi tạo
is_initialized = False

def init_chatbot():
    """
    Khởi tạo các thành phần cần thiết cho chatbot hoạt động.
    Trong kiến trúc Agent, việc này chủ yếu là load biến môi trường
    và khởi tạo Vector Store cho các công cụ sử dụng.
    Agent và LLM sẽ được khởi tạo lazy khi cần.
    """
    global is_initialized
    if is_initialized:
        print("🤖 Chatbot đã được khởi tạo trước đó.")
        return

    print("🔥 Khởi tạo hệ thống Chatbot Agent...")
    
    # 1. Load biến môi trường (quan trọng nhất là GOOGLE_API_KEY)
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ LỖI: GOOGLE_API_KEY không được tìm thấy. Vui lòng kiểm tra file .env")
        is_initialized = False
        return
    print("✅ Biến môi trường đã được tải.")

    # Vector Store không cần khởi tạo ở đây nữa.
    # Các tools sẽ tự truy cập API hoặc nguồn dữ liệu khi cần.

    is_initialized = True
    print("🎉 Chatbot Agent đã sẵn sàng!")


def ask_question(question: str, session_id: str):
    global context_mgr
    """
    Hàm xử lý câu hỏi chính.
    Chuyển tiếp câu hỏi trực tiếp đến AI Agent để xử lý.
    """
    if not is_initialized:
        return {
            "answer": "Xin lỗi, hệ thống chưa được khởi tạo thành công. Vui lòng kiểm tra lại cấu hình.",
            "type": "error_not_initialized"
        }
    # Đảm bảo context_mgr luôn tồn tại trước khi xử lý
    if 'context_mgr' not in globals() or context_mgr is None or getattr(context_mgr, 'session_id', None) != session_id:
        from modules.context_manager import SmartContextManager
        from modules.agent import llm
        context_mgr = SmartContextManager(session_id, llm)

    # Xử lý greeting SIÊU NHANH (không qua agent)
    from modules.intent_service import classify_intent
    from modules.entity_linking import resolve_product_reference
    import re
    q_lower = question.lower().strip()

    # 1. Phân loại intent bằng service
    intent, matched_kw = classify_intent(question)

    # 2. Nếu greeting
    if intent == "greeting":
        answer = "Xin chào bạn 👋 Tôi là trợ lý ảo của DaiBoss. Bạn cần hỗ trợ gì hôm nay?"
        context_mgr.remember(intent="greeting", question=question, bot_message=answer)
        context_mgr.update_summary()
        return {"answer": answer, "type": "greeting"}

    # 3. Nếu intent xác nhận nhanh
    if intent == "confirm":
        last_ctx = context_mgr.recall() if hasattr(context_mgr, 'recall') else {}
        last_intent = last_ctx.get('last_intent') if last_ctx else None
        last_product = last_ctx.get('last_product') if last_ctx else None
        if last_intent in ["inventory_query", "product_price", "product_info"] and last_product:
            from modules.tools import check_product_inventory, get_product_price, get_product_info
            if last_intent == "inventory_query":
                answer = check_product_inventory(last_product)
            elif last_intent == "product_price":
                answer = get_product_price(last_product)
            elif last_intent == "product_info":
                answer = get_product_info(last_product)
            else:
                answer = f"Tôi đã ghi nhận xác nhận của bạn về sản phẩm: {last_product}. Bạn cần hỏi gì thêm không?"
            context_mgr.remember(intent=last_intent, question=question, bot_message=answer, product=last_product)
            context_mgr.update_summary()
            return {"answer": answer, "type": last_intent or "confirmation"}
        else:
            answer = "Bạn xác nhận đúng rồi, vui lòng nói rõ hơn bạn muốn hỏi về sản phẩm hoặc vấn đề gì nhé."
            context_mgr.remember(intent="confirmation", question=question, bot_message=answer)
            context_mgr.update_summary()
            return {"answer": answer, "type": "confirmation"}

    # 4. Nếu intent liên quan sản phẩm (inventory_query, product_price, product_info...)
    if intent in ["inventory_query", "product_price", "product_info"]:
        prod_name = None
        product_info = None
        # 4.1. Thử resolve entity tham chiếu qua service
        print("[DEBUG] ENTITY LINKING INPUT:", question, "| product_history:", context_mgr.product_history)
        ref_product = resolve_product_reference(question, context_mgr.product_history)
        print("[DEBUG] ENTITY LINKING OUTPUT:", ref_product)
        if ref_product:
            prod_name = ref_product.get('name')
            product_info = ref_product.get('product_info')
        else:
            print("[DEBUG] Không resolve được entity tham chiếu từ câu hỏi này!")
        # 4.2. Nếu không, extract tên sản phẩm từ câu hỏi (ưu tiên dùng extract_entities nếu không match từ khóa cứng)
        if not prod_name:
            for t in ["gạch", "xi măng", "sắt", "sơn", "keo", "thiết bị", "lavabo", "bồn cầu", "gạch terrazzo", "kt", "y6503_s"]:
                if t in q_lower:
                    prod_name = question
                    break
        if not prod_name:
            try:
                from modules.entities import extract_entities
                ents = extract_entities(question)
                if 'product' in ents and ents['product']:
                    prod_name = ents['product'][0]
            except Exception as e:
                print("[DEBUG] extract_entities error:", e)
        # 4.3. Nếu vẫn không có, lấy sản phẩm gần nhất
        if not prod_name:
            last_product = context_mgr.get_last_product()
            if last_product:
                prod_name = last_product.get('name')
                product_info = last_product.get('product_info')
        # 4.4. Nếu vẫn không có, hỏi lại user
        if not prod_name:
            print("[DEBUG] Không xác định được prod_name. product_history:", context_mgr.product_history)
            answer = "Dạ xin lỗi quý khách, tôi chưa rõ quý khách muốn kiểm tra sản phẩm nào. Vui lòng cho tôi biết tên sản phẩm ạ."
            context_mgr.remember(intent=intent, question=question, bot_message=answer)
            context_mgr.update_summary()
            return {"answer": answer, "type": intent}
        # 4.5. Nếu đã có product_info thì không cần gọi lại API, còn không thì lấy mới
        if not product_info:
            from modules.tools import get_product_info
            product_info = get_product_info(prod_name)
        # Luôn lưu vào product_history để tracking multi-turn, ưu tiên lấy title từ API, nếu không có thì lấy tên sản phẩm từ câu hỏi user
        def extract_title_from_api_response(api_response):
            import json
            if not api_response:
                return None
            try:
                if isinstance(api_response, str):
                    data = json.loads(api_response)
                else:
                    data = api_response
                # Ưu tiên match_type=exact
                if isinstance(data, dict) and data.get("products"):
                    if data.get("match_type") == "exact" and len(data["products"]) == 1:
                        return data["products"][0].get("title")
                    # fallback: lấy title đầu tiên
                    return data["products"][0].get("title")
            except Exception as e:
                print("[DEBUG] extract_title_from_api_response error:", e)
            return None

        api_title = extract_title_from_api_response(product_info)
        if api_title:
            save_name = api_title
            product_source = "api"
        else:
            # Nếu không có title từ API, luôn lưu đúng giá trị truyền vào biến prod_name (tức là params['q'] khi gọi API)
            save_name = prod_name
            product_source = "user_query"
        context_mgr.remember(intent=intent, question=question, bot_message=None, product=save_name, product_info=product_info, product_source=product_source)
        context_mgr.update_summary()

        # Gọi tool phù hợp và trả lời chuyên nghiệp, hấp dẫn, cá nhân hóa
        user_name = "quý khách"  # Có thể lấy từ session nếu muốn cá nhân hóa hơn
        if intent == "inventory_query":
            from modules.tools import check_product_inventory
            inventory = check_product_inventory(prod_name)
            answer = f"{user_name} thân mến, sản phẩm {prod_name} hiện còn {inventory} trong kho. Bạn muốn đặt mua số lượng bao nhiêu, hay cần tư vấn thêm về ưu đãi, vận chuyển không ạ? DaiBoss luôn sẵn sàng hỗ trợ!"
        elif intent == "product_price":
            from modules.tools import get_product_price
            price = get_product_price(prod_name)
            answer = f"Giá bán ưu đãi của sản phẩm hiện tại là {price} VNĐ. Sản phẩm này đang được nhiều khách hàng lựa chọn tại DaiBoss! Bạn có muốn nhận báo giá chi tiết, đặt hàng ngay hoặc tư vấn thêm về chương trình khuyến mãi không ạ?"
        elif intent == "product_info":
            from modules.tools import get_product_info
            info = get_product_info(prod_name)
            answer = f"Dưới đây là thông tin chi tiết về {prod_name}: {info} Nếu {user_name} cần biết thêm về giá, tồn kho hoặc chính sách giao hàng, hãy nhắn cho DaiBoss nhé!"
        else:
            answer = "Xin lỗi, tôi chưa hỗ trợ intent này."
        # Luôn lưu đúng sản phẩm vừa hỏi vào history, không ghi đè nhầm sản phẩm trước
        context_mgr.remember(intent=intent, question=question, bot_message=answer, product=prod_name, product_info=product_info)
        context_mgr.update_summary()
        return {"answer": answer, "type": intent}
    # fallback
    # Nếu không xác định được intent, chuyển sang agent reasoning hoặc fallback chuyên nghiệp

    import pprint
    try:
        print(f"\n{'='*20} NEW USER QUESTION {'='*20}")
        print(f"[USER QUESTION]: {question}")
        # Sử dụng agent_executor đã có memory để xử lý
        # session_id sẽ được dùng để quản lý memory sau này
        callback = TimingCallbackHandler()
        # Chỉ truyền 3-5 lượt chat gần nhất vào chat_history để agent xử lý nhanh hơn
        # Nếu context_mgr có hàm lấy lịch sử ngắn, hãy sử dụng
        chat_hist = None
        if hasattr(context_mgr, 'memory') and hasattr(context_mgr.memory, 'buffer'):
            # Lấy 3-7 lượt chat gần nhất (nếu có)
            if isinstance(context_mgr.memory.buffer, list):
                chat_hist = context_mgr.memory.buffer[-7:]
            else:
                chat_hist = context_mgr.memory.buffer

        # Gọi agent_executor để xử lý câu hỏi
        response = agent_executor.invoke(
            {"input": question, "chat_history": chat_hist},
            config={"configurable": {"session_id": session_id}},
            callbacks=[callback]
        )

        # Xử lý kết quả từ agent
        answer = response.get("output", "Xin lỗi, tôi chưa có câu trả lời cho vấn đề này.")
        
        # Log reasoning sâu từng bước & lưu structured product_info nếu có
        last_product_info = None
        last_product_name = None
        
        # Xử lý intermediate steps nếu có
        if 'intermediate_steps' in response and response['intermediate_steps']:
            print("[AGENT REASONING STEPS]:")
            for idx, step in enumerate(response['intermediate_steps']):
                action, observation = step
                print(f"  Step {idx+1}:")
                print(f"    [Action]: {action}")
                print(f"    [Observation]: {observation}")
                
                # Xử lý observation để trích xuất thông tin sản phẩm
                try:
                    obs_data = observation
                    if isinstance(observation, str):
                        import json
                        if '{' in observation and '}' in observation:
                            obs_data = json.loads(observation)
                    
                    # Nếu observation chứa thông tin sản phẩm
                    if isinstance(obs_data, dict):
                        if obs_data.get('title'):
                            last_product_info = obs_data
                            last_product_name = obs_data['title']
                        # Xử lý trường hợp có products array
                        elif obs_data.get('products') and isinstance(obs_data['products'], list) and len(obs_data['products']) > 0:
                            last_product_info = obs_data['products'][0]
                            last_product_name = obs_data['products'][0].get('title')
                except Exception as e:
                    print(f"[DEBUG] Lỗi khi xử lý observation: {e}")

        # Log agent scratchpad nếu có
        if 'agent_scratchpad' in response and response['agent_scratchpad']:
            print("[AGENT SCRATCHPAD]:")
            print(response['agent_scratchpad'])

        # Lưu thông tin sản phẩm nếu có
        if last_product_info and last_product_name:
            context_mgr.remember(
                intent="product_info", 
                question=question, 
                bot_message=answer, 
                product=last_product_name, 
                product_info=last_product_info
            )
        else:
            # Nếu không có thông tin sản phẩm, vẫn lưu lịch sử
            context_mgr.remember(
                intent=intent or "unknown",
                question=question,
                bot_message=answer,
                product=question  # Sử dụng câu hỏi làm tên sản phẩm tạm thời
            )
        context_mgr.update_summary()

        # Xử lý gợi ý sản phẩm nếu là intent product_suggestion
        if intent == "product_suggestion":
            print(f"[DEBUG] Xử lý riêng cho product_suggestion")
            try:
                from modules.tools import recommend_products
                suggestions = recommend_products(question)
                return {
                    "answer": suggestions, 
                    "type": "product_suggestion"
                }
            except Exception as e:
                print(f"[DEBUG] recommend_products error: {e}")
                return {
                    "answer": "Bạn có thể tham khảo thêm các sản phẩm nổi bật khác tại cửa hàng!",
                    "type": "product_suggestion"
                }

        # Trả về kết quả bình thường nếu không phải product_suggestion
        return {
            "answer": answer,
            "type": "agent_based"
        }

    except Exception as e:
        print(f"❌ Lỗi trong quá trình Agent thực thi: {e}")
        return {
            "answer": "Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại sau.",
            "type": "error_agent_execution"
        }
    # Fallback
    fallback = "Xin lỗi, tôi chưa rõ ý bạn hỏi. Tôi là trợ lý ảo chuyên tư vấn sản phẩm và dịch vụ của DaiBoss. Bạn có thể hỏi về sản phẩm, giá, chính sách đổi trả, bảo hành, giao hàng, hoặc các ưu đãi hiện có."
    context_mgr.remember(intent="khac", question=question, bot_message=fallback)
    context_mgr.update_summary()
    return {"answer": fallback, "type": "fallback_ai"}