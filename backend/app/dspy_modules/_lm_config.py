import dspy
from app.config import GOOGLE_API_KEY

# 設一個 flag，避免重複初始化
_dspy_initialized = False

def init_dspy():
    global _dspy_initialized
    if _dspy_initialized:
        return  # 已初始化，直接跳過

    # 初始化 Gemini 模型
    lm = dspy.LM(
        'gemini/gemini-2.0-flash',
        api_key=GOOGLE_API_KEY,
        max_tokens=8000,
        temperature=1
    )
    dspy.configure(lm=lm)
    _dspy_initialized = True
