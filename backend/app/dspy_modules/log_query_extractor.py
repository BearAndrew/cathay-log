import dspy
from dspy import InputField, OutputField

class LogQuerySignature(dspy.Signature):
    question = InputField(desc="使用者輸入的問題")
    start_time = OutputField(desc="使用者要求的開始時間，若沒有則為空，格式 dd/Mon/yyyy:HH:MM:SS")
    end_time = OutputField(desc="使用者要求的結束時間，若沒有則為空，格式 dd/Mon/yyyy:HH:MM:SS")
    status_code = OutputField(desc=(
        "HTTP 狀態碼的正規表達式，用於篩選日誌狀態碼，例如："
        "'404' 表示只包含 404，"
        "'^2\\\\d\\\\d$' 表示只包含 2xx，"
        "'^(?!404$)\\\\d{3}$' 表示排除 404，"
        "'^(?!2\\\\d\\\\d$)\\\\d{3}$' 表示排除 2xx。"
        "若沒有則為空，表示不限制狀態碼。"
    ))
    http_method = OutputField(desc="使用者要求的HTTP方法，若沒有則為空")
    source_ip = OutputField(desc="使用者要求的來源IP，若沒有則為空")

class LogQueryExtractor(dspy.Predict):
    def __init__(self):
        super().__init__(LogQuerySignature)
