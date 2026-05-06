from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from ai_agent.hermes.orchestrator import Orchestrator
from ai_agent.llm.lmstudio import LMStudioClient
from ai_agent.rag.pdf_rag import PDFRag
import time
import uuid
import json
import tempfile
import os

app = FastAPI()
orch = Orchestrator()
llm = LMStudioClient()
pdf_rag = PDFRag()

IGNORE_PREFIXES = [
    "### Task:",
    "### Instructions:",
    "Generate a",
    "Create a",
    "Analyze the",
    "Based on the conversation",
    "Suggest ",
    "Your task is",
]


@app.get("/v1/models")
def models():
    return {
        "object": "list",
        "data": [{"id": "queryquest", "object": "model", "owned_by": "local"}]
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "queryquest"}


class ChatRequest(BaseModel):
    model: str = "queryquest"
    messages: list
    stream: bool = False


@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    # ユーザーメッセージだけ抽出
    user_messages = [m for m in req.messages if m.get("role") == "user"]
    if not user_messages:
        return _empty_response()

    user_msg = user_messages[-1]["content"]

    # WebUI内部プロンプトを無視
    for prefix in IGNORE_PREFIXES:
        if user_msg.strip().startswith(prefix):
            return _empty_response()

    # 会話履歴（最後のユーザーメッセージを除く）
    history = [
        m for m in req.messages
        if m.get("role") in ("user", "assistant")
    ][:-1]

    # ストリーミング対応
    if req.stream:
        return StreamingResponse(
            _stream_response(user_msg, history),
            media_type="text/event-stream"
        )

    # 通常レスポンス
    result = orch.run(user_msg, history=history)
    answer = result.get("final", "")

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "queryquest",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": answer},
            "finish_reason": "stop"
        }]
    }


async def _stream_response(user_msg: str, history: list):
    """SSEストリーミングレスポンス"""
    # Orchestratorで前処理（Web検索・RAG）
    result = orch.run(user_msg, history=history)
    answer = result.get("final", "")

    # 既に完成した回答をストリーミング形式で返す
    # （LM StudioのストリーミングはLMStudioClient.chat_streamで対応）
    chunk_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"

    # 文字ごとに少しずつ送る（本来はLLMのストリーミングを使う）
    words = answer.split(" ")
    for i, word in enumerate(words):
        chunk = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "queryquest",
            "choices": [{
                "index": 0,
                "delta": {"content": word + (" " if i < len(words)-1 else "")},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk)}\n\n"

    # 終了シグナル
    final_chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": "queryquest",
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/v1/rag/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """PDFをアップロードしてRAGに追加"""
    if not file.filename.endswith(".pdf"):
        return {"ok": False, "error": "PDFファイルのみ対応"}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = pdf_rag.load_pdf(tmp_path)
        return result
    finally:
        os.unlink(tmp_path)


@app.get("/v1/rag/status")
def rag_status():
    """RAGの状態確認"""
    return {
        "ok": True,
        "total_chunks": len(pdf_rag.texts),
        "has_index": pdf_rag.index is not None
    }


@app.delete("/v1/rag/clear")
def rag_clear():
    """RAGデータを全削除"""
    pdf_rag.clear()
    return {"ok": True, "message": "RAGデータを削除しました"}


def _empty_response():
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "queryquest",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": ""},
            "finish_reason": "stop"
        }]
    }
