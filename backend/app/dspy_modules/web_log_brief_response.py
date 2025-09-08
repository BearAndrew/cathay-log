import dspy
from dspy import InputField, OutputField

class WebLogBriefResponseSignature(dspy.Signature):
    chat_history = InputField(desc="最近的對話紀錄")
    tool_output = InputField(desc="伺服器日誌工具回傳結果")
    answer = OutputField(desc="""
        請根據工具輸出進行回答，並提供詳細建議。
        只整理各狀態碼出現次數統計結果，並顯示呼叫最多的一個IP與最多的一個資源。
        若只有單一IP或單一資源則不顯示該項統計。
        統計結果以表格呈現，表頭不能換行，td內多個內容要加上換行符號。""")

class WebLogBriefResponseGenerator(dspy.Predict):
    def __init__(self):
        super().__init__(WebLogBriefResponseSignature)
