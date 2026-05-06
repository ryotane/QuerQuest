# ai_agent/rag/auto_ingest.py

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ai_agent.memory.vector_memory import get_memory


class RAGIngestHandler(FileSystemEventHandler):

    def __init__(self):
        self.memory = get_memory()

    def ingest(self, path):

        try:
            if not os.path.exists(path):
                return

            if path.endswith(".txt") or path.endswith(".md"):

                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()

                if text.strip():
                    print(f"📥 取り込み: {path}")
                    self.memory.add(text, {"source": path})

        except Exception as e:
            print("❌ ingest error:", e)

    def on_created(self, event):
        if not event.is_directory:
            self.ingest(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.ingest(event.src_path)


def preload(folder):

    memory = get_memory()

    print("📚 初期ロード開始")

    for root, _, files in os.walk(folder):
        for f in files:
            path = os.path.join(root, f)
            if path.endswith(".txt") or path.endswith(".md"):
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        text = file.read()
                        if text.strip():
                            memory.add(text, {"source": path})
                            print(f"📥 preload: {path}")
                except:
                    pass

    print("✅ 初期ロード完了")


def start_rag_watcher(folder="rag_data"):

    os.makedirs(folder, exist_ok=True)

    # 🔥 preload
    preload(folder)

    handler = RAGIngestHandler()

    observer = Observer()
    observer.schedule(handler, folder, recursive=True)
    observer.start()

    print(f"👀 RAG監視開始: {folder}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()