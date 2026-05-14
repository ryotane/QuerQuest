#!/bin/bash

echo "🚀 QueryQuest 起動中..."

# =========================
# 🔥 安定化
# =========================
export PYTHONUNBUFFERED=1

# =========================
# 🔥 パス設定（あなたの環境用）
# =========================
BASE="/Volumes/Data SSD/local_ai_project"

SEARXNG_DIR="$BASE/searxng"
QUERYQUEST_DIR="$BASE/QueryQuest"
WEBUI_DIR="$BASE/open-webui"

PORT_API=8100
PORT_WEBUI=3000
PORT_SEARX=8888

# =========================
# 🔥 クリーンアップ
# =========================
echo "🧹 クリーンアップ..."

pkill -f uvicorn 2>/dev/null
pkill -f searx 2>/dev/null
pkill -f webui 2>/dev/null

sleep 2

# =========================
# 🔍 SearXNG 起動
# =========================
echo "🌐 SearXNG 起動..."

cd "$SEARXNG_DIR" || { echo "❌ SearXNGフォルダ見つからない"; exit 1; }

# 仮想環境
if [ -d "venv" ]; then
  source venv/bin/activate
else
  echo "❌ searxng venv が無い"
  exit 1
fi

# 必須依存（不足時だけ入る）
pip install whitenoise >/dev/null 2>&1

export SEARXNG_SETTINGS_PATH="$SEARXNG_DIR/settings.yml"

python searx/webapp.py --port $PORT_SEARX &
SEARX_PID=$!

sleep 3

# =========================
# 🧠 QueryQuest API 起動
# =========================
echo "🧠 AI API 起動..."

cd "$QUERYQUEST_DIR" || { echo "❌ QueryQuestフォルダ見つからない"; exit 1; }

if [ -d "ai-env" ]; then
  source ai-env/bin/activate
else
  echo "❌ ai-env が無い"
  exit 1
fi

# 🔥 これが超重要（importエラー対策）
export PYTHONPATH=$(pwd)

uvicorn ai_agent.main:app --port $PORT_API &
API_PID=$!

sleep 3

# =========================
# 💻 Open WebUI 起動
# =========================
echo "💻 WebUI 起動..."

cd "$WEBUI_DIR" || { echo "❌ WebUIフォルダ見つからない"; exit 1; }

# run.shがあるかチェック
if [ -f "./run.sh" ]; then
  ./run.sh &
else
  # Node版 fallback
  if command -v npm >/dev/null 2>&1; then
    npm install >/dev/null 2>&1
    PORT=$PORT_WEBUI npm run dev &
  else
    echo "❌ Node/npm が無い"
  fi
fi

WEBUI_PID=$!

sleep 5

# =========================
# 🎉 完了表示
# =========================
echo ""
echo "=============================="
echo "✅ 起動完了"
echo "=============================="
echo "🌐 WebUI:   http://localhost:$PORT_WEBUI"
echo "🧠 API:     http://localhost:$PORT_API/docs"
echo "🔍 SearXNG: http://localhost:$PORT_SEARX"
echo "=============================="

# =========================
# 🛑 終了処理
# =========================
trap "echo '🛑 停止中...'; kill $SEARX_PID $API_PID $WEBUI_PID 2>/dev/null; exit" INT

wait