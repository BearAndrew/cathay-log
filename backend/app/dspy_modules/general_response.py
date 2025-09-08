import dspy
from dspy import InputField, OutputField


class GeneralResponseSignature(dspy.Signature):
    question = InputField(desc="使用者輸入的問題")
    answer = OutputField(desc="根據使用者問題給出的簡短回答")

class GeneralResponseGenerator(dspy.Predict):
    def __init__(self):
        super().__init__(GeneralResponseSignature)
