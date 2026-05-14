import queue
import sounddevice as sd
import vosk
import json
import pyttsx3
import os

from ai_agent.hermes.orchestrator import Orchestrator

MODEL_PATH = "/Volumes/Data SSD/local_ai_project/QueryQuest/vosk_model"

if not os.path.exists(MODEL_PATH):
    raise RuntimeError("Voskモデルが見つかりません")

model = vosk.Model(MODEL_PATH)
engine = pyttsx3.init()
orch = Orchestrator()

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def run():
    
    with sd.RawInputStream(
        device=1, 
        samplerate=16000,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        rec = vosk.KaldiRecognizer(model, 16000)
        
        print("🎤 Listening...")
        
        while True:
            data = q.get()
            
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                
                text = result.get("text")
                
                if text:
                    print("👤", text)
                    
                    res = orch.run(text)
                    
                    answer = res.get("final", "")
                    
                    print("🤖", answer)
                    
                    engine.say(answer)
                    engine.runAndWait()