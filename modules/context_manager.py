# ============================= #
# 📂 File: modules/context_manager.py
# ============================= #

from langchain.memory import ConversationSummaryBufferMemory
from modules.storage import load_summary_from_db, save_summary_to_db

class SmartContextManager:
    def __init__(self, session_id, llm):
        self.session_id = session_id
        self.llm = llm
        self.memory = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=700,
            memory_key="chat_history",
            return_messages=True
        )
        self.summary = ""
        self.last_product = None
        self.last_intent = None
        self.last_bot_message = None
        # Multi-entity: lưu danh sách sản phẩm đã nhắc tới trong hội thoại
        self.product_history = []  # list of dict: {name, product_info, turn, intent}
        self.turn_counter = 0

    def add_product_to_history(self, product_name, product_info=None, intent=None):
        self.turn_counter += 1
        # Nếu sản phẩm đã có trong history, cập nhật lại thông tin mới nhất
        for p in self.product_history:
            if p['name'] == product_name:
                p['product_info'] = product_info or p['product_info']
                p['intent'] = intent or p['intent']
                p['turn'] = self.turn_counter
                return
        # Nếu chưa có, thêm mới
        self.product_history.append({
            'name': product_name,
            'product_info': product_info,
            'intent': intent,
            'turn': self.turn_counter
        })

    def get_last_product(self):
        if self.product_history:
            return sorted(self.product_history, key=lambda x: -x['turn'])[0]
        return None

    def get_product_by_reference(self, ref):
        # ref: "trên", "nó", "sp trên"...
        # Nếu ref là "trên", lấy sản phẩm vừa nhắc trước đó (không phải cuối cùng)
        if len(self.product_history) >= 2 and (ref in ["trên", "sp trên", "sản phẩm trên"]):
            return sorted(self.product_history, key=lambda x: -x['turn'])[1]
        # Nếu ref là "nó", "đó", "này"... lấy sản phẩm gần nhất
        if self.product_history:
            return sorted(self.product_history, key=lambda x: -x['turn'])[0]
        return None

    def get_all_products_in_history(self):
        return sorted(self.product_history, key=lambda x: -x['turn'])

    def remember(self, **kwargs):
        # ... giữ nguyên logic cũ ...
        if 'intent' in kwargs:
            self.last_intent = kwargs['intent']
        if 'question' in kwargs:
            self.last_question = kwargs['question']
        if 'bot_message' in kwargs:
            self.last_bot_message = kwargs['bot_message']
        if 'product' in kwargs:
            self.last_product = kwargs['product']
        if 'product_info' in kwargs:
            self.last_product_info = kwargs['product_info']
        # Multi-entity: nếu có product, lưu vào history
        if 'product' in kwargs:
            self.add_product_to_history(kwargs['product'], kwargs.get('product_info'), kwargs.get('intent'))

    def recall(self):
        # ... giữ nguyên logic cũ ...
        return {
            'last_intent': getattr(self, 'last_intent', None),
            'last_product': getattr(self, 'last_product', None),
            'last_product_info': getattr(self, 'last_product_info', None),
            'last_question': getattr(self, 'last_question', None),
            'last_bot_message': getattr(self, 'last_bot_message', None),
            'product_history': getattr(self, 'product_history', []),
        }

    def update_summary(self):
        save_summary_to_db(self.session_id, self.memory.buffer)