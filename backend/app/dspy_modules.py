# dspy_modules.py
import dspy
from dspy import InputField, OutputField

class IntentCheckSignature(dspy.Signature):
    question = InputField(desc="使用者輸入的問題")
    intent = OutputField(desc="使用者意圖，log 或 general")

class ResponseSignature(dspy.Signature):
    chat_history = InputField(desc="最近的對話紀錄")
    tool_output = InputField(desc="伺服器日誌工具回傳結果")
    answer = OutputField(desc="""
        若使用者是在詢問伺服器日誌，請根據工具輸出進行回答，並提供詳細建議與log詳細資訊統計表格。
        若不是伺服器日誌相關問題，請給出一般性自然回答。
        回答必須清楚、有條理、包含技術細節（如有），並避免過度簡化。""")

# 模組
class IntentChecker(dspy.Predict):
    def __init__(self):
        super().__init__(IntentCheckSignature)

class ResponseGenerator(dspy.Predict):
    def __init__(self):
        super().__init__(ResponseSignature)

# 初始化 DSPy 使用 Gemini
from app.config import GOOGLE_API_KEY

lm = dspy.LM('gemini/gemini-2.0-flash', api_key=GOOGLE_API_KEY)
dspy.configure(lm=lm)