#!/bin/bash
# 講義建立工具 啟動腳本
# 雙擊執行，或在終端機輸入：bash start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8765

# 檢查伺服器是否已在執行
if lsof -ti:$PORT > /dev/null 2>&1; then
  echo "伺服器已在執行（port $PORT）"
else
  echo "啟動伺服器…"
  cd "$SCRIPT_DIR"
  python3 server.py &
  sleep 1
  echo "伺服器已啟動"
fi

# 開啟瀏覽器
open "http://localhost:$PORT"
