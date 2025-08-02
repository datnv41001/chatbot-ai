# ============================= #
# 📂 File: modules/context_manager.py
# ============================= #

from langchain.memory import ConversationSummaryBufferMemory
from modules.storage import load_summary_from_db, save_summary_to_db

class SmartContextManager:
    def __init__(self, session_id: str, llm):
        self.session_id = session_id
        self.llm = llm
        self.memory = self._init_memory()
        self.ctx = {
            "last_product": None,
            "last_intent": None,
            "last_question": None,
            "last_bot_message": None
        }

    def _init_memory(self):
        summary = load_summary_from_db(self.session_id)
        memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            memory_key="chat_history",
            return_messages=True,
            max_token_limit=1000
        )
        if summary:
            memory.buffer = summary
        return memory

    def remember(self, intent=None, product=None, question=None, bot_message=None):
        if intent:
            self.ctx["last_intent"] = intent
        if product:
            self.ctx["last_product"] = product
        if question:
            self.ctx["last_question"] = question
        if bot_message:
            self.ctx["last_bot_message"] = bot_message

    def recall(self):
        return self.ctx

    def update_summary(self):
        save_summary_to_db(self.session_id, self.memory.buffer)