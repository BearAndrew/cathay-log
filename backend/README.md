建立虛擬環境
uv venv

初始化環境
uv init

進入虛擬環境
source .venv/bin/activate

安裝依賴套件
uv add mcp fastapi langchain-mcp-adapters langgraph langserve langchain-openai

或是安裝現有套件全部
uv sync

啟動 mcp server
cd mcp
python server.py

測試 mcp
uv run mcp dev server.py

啟動後端服務 fastapi
uvicorn app.main:app --reload --port 9000



測試API
curl -X POST http://localhost:9000/web-log/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "請幫我計算 5 + 5"}'



 curl -X OPTIONS https://cathay-log.onrender.com/api/infer \
  -H "Origin: https://thriving-alfajores-e1c9ee.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -i







============ 學習 ==============
langchain 
https://cloud.tencent.com/developer/article/2286924?areaSource=100001.5&utm_source=chatgpt.com