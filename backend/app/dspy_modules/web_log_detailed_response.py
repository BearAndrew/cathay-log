import dspy
from dspy import InputField, OutputField

class WebLogDetailedResponseSignature(dspy.Signature):
    chat_history = InputField(desc="最近的對話紀錄")
    tool_output = InputField(desc="伺服器日誌工具回傳結果")
    answer = OutputField(desc="""
        請根據工具輸出進行回答，並提供詳細建議。
        統計結果以表格呈現，表頭不能換行，td內多個內容要加上換行符號。
        不同統計內容要分開成多張表格。
        若針對單一IP則不用顯示IP統計表格。
        若針對單一資源則不用顯示資源統計表格。""")

class WebLogDetailedResponseGenerator(dspy.Predict):
    def __init__(self):
        super().__init__(WebLogDetailedResponseSignature)
