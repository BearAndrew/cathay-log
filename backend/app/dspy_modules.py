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
        若使用者是在詢問伺服器日誌，請根據工具輸出進行回答，並提供詳細建議。
        若不是伺服器日誌相關問題，請給出一般性自然回答。
        回答必須清楚、有條理、包含技術細節（如有），並避免過度簡化。
        將工具輸出的統計結果以表格呈現，表頭不能換行，td內多個內容要加上換行符號
        不同統計內容要分開成多張表格""")

class LogQuerySignature(dspy.Signature):
    question = InputField(desc="使用者輸入的問題")
    start_time = OutputField(desc="使用者要求的開始時間，若沒有則為空，格式 dd/Mon/yyyy:HH:MM:SS")
    end_time = OutputField(desc="使用者要求的結束時間，若沒有則為空，格式 dd/Mon/yyyy:HH:MM:SS")
    status_code = OutputField(desc="使用者要求的狀態碼，若沒有則為 404，格式為HTTP狀態碼")
    http_method = OutputField(desc="使用者要求的HTTP方法，若沒有則為空")
    source_ip = OutputField(desc="使用者要求的來源IP，若沒有則為空")

# 模組
class IntentChecker(dspy.Predict):
    def __init__(self):
        super().__init__(IntentCheckSignature)

class ResponseGenerator(dspy.Predict):
    def __init__(self):
        super().__init__(ResponseSignature)
        
class LogQueryExtractor(dspy.Predict):
    def __init__(self):
        super().__init__(LogQuerySignature)


# 初始化 DSPy 使用 Gemini
from app.config import GOOGLE_API_KEY

lm = dspy.LM('gemini/gemini-2.0-flash', api_key=GOOGLE_API_KEY, max_tokens=8000, temperature=1)
dspy.configure(lm=lm)