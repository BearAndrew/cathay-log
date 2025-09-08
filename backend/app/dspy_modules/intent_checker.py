import dspy
from dspy import InputField, OutputField


class Classification(dspy.Signature):
    """將使用者訊息分類到其中一個意圖標籤。
    輸出應該只有預測的類別，作為單一的意圖標籤。"""
    question = dspy.InputField(desc="""使用者訊息""")
    intent_labels = dspy.InputField(desc="""代表使用者意圖的標籤列表""")
    intent = dspy.OutputField(desc="""最符合使用者意圖的標籤，只要包含標籤字串""")
    intent_desc= dspy.InputField(
        desc="""額外描述信息，用於輔助判斷使用者意圖。例如，提示意圖的背景或上下文。""",
    )

class IntentChecker(dspy.Predict):
    def __init__(self):
        super().__init__(Classification)
