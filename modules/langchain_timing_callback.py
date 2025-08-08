from langchain.callbacks.base import BaseCallbackHandler
import time

# ANSI color codes for terminal
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

def _shorten(text, maxlen=200):
    if isinstance(text, str) and len(text) > maxlen:
        return text[:maxlen] + "..."
    if isinstance(text, list) and len(text) > 0:
        return _shorten(text[0], maxlen)
    return text

def print_section(title, color=CYAN):
    print(f"{color}{BOLD}\n{'='*10} {title} {'='*10}{RESET}")

class TimingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        print_section("TimingCallbackHandler INIT", GREEN)
        self.reset()
    def reset(self):
        print(f"{YELLOW}[RESET]{RESET} TimingCallbackHandler reset")
        self.llm_start = None
        self.llm_end = None
        self.tool_start = None
        self.tool_end = None
    def on_llm_start(self, serialized, prompts, **kwargs):
        print_section("LLM START", CYAN)
        self.llm_start = time.time()
        short_prompt = _shorten(prompts, 300)
        print(f"{CYAN}[⏱️] Bắt đầu gọi LLM với prompt:{RESET}\n{short_prompt}")
    def on_llm_end(self, response, **kwargs):
        self.llm_end = time.time()
        print(f"{GREEN}[⏱️] Kết thúc LLM, thời gian: {self.llm_end - self.llm_start:.2f}s{RESET}")
    def on_tool_start(self, serialized, input_str, **kwargs):
        print_section("TOOL START", YELLOW)
        self.tool_start = time.time()
        tool_name = serialized.get('name', '')
        short_input = _shorten(input_str, 200)
        print(f"{YELLOW}[🛠️] Bắt đầu gọi tool: {tool_name}, input: {short_input}{RESET}")
    def on_tool_end(self, output, **kwargs):
        self.tool_end = time.time()
        print(f"{GREEN}[🛠️] Kết thúc tool, thời gian: {self.tool_end - self.tool_start:.2f}s{RESET}")
        short_output = _shorten(output, 200)
        print(f"{CYAN}[🛠️] Output tool: {short_output}{RESET}")
