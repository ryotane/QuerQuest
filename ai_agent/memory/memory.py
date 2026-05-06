import json
import os
import time

LOG_FILE = "QueryQuest/memory/log.jsonl"
MAX_LOG = 100

class MemorySystem:
    def __init__(self, file_path="QueryQuest/memory/user_profile.json"):
        self.file_path = file_path
        self.profile = self._load_profile()

    def _default_profile(self):
        return {
            "familiarity": 1.0,
            "interests": [],
            "last_topic": "",
            "last_seen": time.time(),
            "mood": "neutral"
        }

    def _load_profile(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    data = json.load(f)

                # 不足キー補完
                default = self._default_profile()
                for k, v in default.items():
                    if k not in data:
                        data[k] = v

                return data

            except Exception:
                return self._default_profile()

        return self._default_profile()

    def _save(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            json.dump(self.profile, f, indent=4)

    # =========================
    # 🔥 NEW: ログ保存（追加）
    # =========================
    def save_log(self, query, response):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        entry = {
            "time": time.time(),
            "q": query,
            "a": response[:300]  # 長すぎ防止
        }

        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # 圧縮
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()

        if len(lines) > MAX_LOG:
            with open(LOG_FILE, "w") as f:
                f.writelines(lines[-MAX_LOG:])

    # =========================
    # 更新
    # =========================
    def update(self, text):
        now = time.time()

        last_seen = self.profile.get("last_seen", now)
        diff = now - last_seen

        if any(k in text for k in ["疲れた", "しんどい", "悩み"]):
            self.profile["familiarity"] += 0.5
            self.profile["mood"] = "tired"
        else:
            self.profile["familiarity"] += 0.1

        self.profile["familiarity"] = min(5.0, self.profile["familiarity"])

        keywords = ["京都", "Mac", "LLM", "RX11", "オーディオ", "ナレーション"]
        for k in keywords:
            if k in text and k not in self.profile["interests"]:
                self.profile["interests"].append(k)

        self.profile["last_seen"] = now
        self._save()

    # =========================
    # コンテキスト生成
    # =========================
    def get_context(self):
        f = self.profile["familiarity"]

        status = (
            "初対面" if f < 2 else
            "知人" if f < 3.5 else
            "相棒" if f < 4.5 else
            "親友"
        )

        diff = time.time() - self.profile.get("last_seen", time.time())

        if diff > 86400:
            time_msg = "久しぶりだね"
        elif diff > 3600:
            time_msg = "ちょっと時間空いたね"
        else:
            time_msg = "さっきぶりだね"

        mood = self.profile.get("mood", "neutral")

        return f"""
【関係性】{status}（親密度 {f:.1f}/5.0）
【時間】{time_msg}
【気分】{mood}
【興味】{', '.join(self.profile['interests'])}
"""