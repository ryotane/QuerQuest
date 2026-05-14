import queue
import sounddevice as sd
import vosk
import json
import os
import time
import threading

import pyttsx3  # fallback用
import requests

from ai_agent.hermes.orchestrator import Orchestrator

# =========================
# 設定
# =========================
MODEL_PATH = "/Volumes/Data SSD/local_ai_project/QueryQuest/vosk_model"
DEVICE_ID = 1
WAKE_WORD = "クエスト"
STOP_WORDS = ["ストップ", "止まって", "ちょっと待って"]

# =========================
# 初期化
# =========================
model = vosk.Model(MODEL_PATH)
orch = Orchestrator()

q = queue.Queue(maxsize=10)

# 音声状態
speaking = False
stop_signal = False

# fallback音声
engine = pyttsx3.init()


# =========================
# 音声入力
# =========================
def callback(indata, frames, time_, status):
    try:
        q.put_nowait(bytes(indata))
    except:
        try:
            q.get_nowait()
            q.put_nowait(bytes(indata))
        except:
            pass


# =========================
# 高品質TTS（Macなら say 使用）
# =========================
def speak_stream(text):

    global speaking, stop_signal

    speaking = True
    stop_signal = False

    # 文を分割（ストリーミング風）
    chunks = text.split("。")

    for chunk in chunks:

        if stop_signal:
            break

        chunk = chunk.strip()
        if not chunk:
            continue

        # Macネイティブ音声（自然）
        os.system(f'say "{chunk}"')

    speaking = False


# =========================
# 回答抽出
# =========================
def extract_answer(res):
    if isinstance(res, dict):
        return res.get("final") or res.get("result") or str(res)
    return str(res)


# =========================
# キュークリア
# =========================
def flush_queue():
    while not q.empty():
        try:
            q.get_nowait()
        except:
            break


# =========================
# 音声取得
# =========================
def listen_once(rec):

    result_text = ""
    silence = 0
    start = time.time()

    while True:
        if time.time() - start > 8:
            break

        try:
            data = q.get(timeout=1)
        except:
            silence += 1
            continue

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")

            if text:
                result_text += " " + text
                silence = 0
            else:
                silence += 1

        if silence > 3:
            break

    return result_text.strip()


# =========================
# 割り込み監視（最重要）
# =========================
def interrupt_listener(rec):

    global stop_signal, speaking

    while True:
        if not speaking:
            time.sleep(0.1)
            continue

        try:
            data = q.get(timeout=0.5)
        except:
            continue

        if rec.AcceptWaveform(data):
            text = json.loads(rec.Result()).get("text", "")

            if any(w in text for w in STOP_WORDS):
                print("🛑 割り込み検出")
                stop_signal = True
                speaking = False
                break


# =========================
# メイン
# =========================
def run():

    with sd.RawInputStream(
        device=DEVICE_ID,
        samplerate=16000,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        rec = vosk.KaldiRecognizer(model, 16000)

        print("🟢 Wake待機（ヘイ クエスト）")

        while True:
            try:
                data = q.get(timeout=1)
            except:
                continue

            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "")

                if text:
                    print("👂", text)

                    if WAKE_WORD in text.replace(" ", ""):

                        print("🚀 起動！")
                        os.system('say "はい、どうしました？"')

                        rec.Reset()
                        flush_queue()

                        command = listen_once(rec)

                        if not command:
                            continue

                        print("👤", command)

                        # 非同期処理
                        def worker():

                            res = orch.run(command)
                            answer = extract_answer(res)

                            print("🤖", answer)

                            # 割り込み監視スレッド
                            threading.Thread(
                                target=interrupt_listener,
                                args=(rec,),
                                daemon=True
                            ).start()

                            speak_stream(answer)

                            print("🟢 待機に戻る")

                        threading.Thread(target=worker, daemon=True).start()