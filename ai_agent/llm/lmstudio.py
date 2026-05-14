from openai import OpenAI


class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234/v1", model=None):
        self.client = OpenAI(base_url=base_url, api_key="lm-studio")
        self.model = model or self._detect_model()

    # =========================
    # 🔍 モデル自動取得
    # =========================
    def _detect_model(self):
        try:
            models = self.client.models.list()
            return models.data[0].id
        except Exception:
            return "unknown-model"

    # =========================
    # 🧠 Chat（完全互換）
    # =========================
    def chat(self, messages, temperature=0.6):

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
        except Exception as e:
            return f"[LLM ERROR] {e}"

        # =========================
        # 🔥 完全互換パーサ
        # =========================
        return self._extract_content(response)

    # =========================
    # 🧠 レスポンス抽出（ここが核）
    # =========================
    def _extract_content(self, response):

        # --- ① OpenAI標準 ---
        try:
            return response.choices[0].message.content
        except Exception:
            pass

        # --- ② dict形式 ---
        try:
            return response["choices"][0]["message"]["content"]
        except Exception:
            pass

        # --- ③ Mistral / 一部モデル ---
        try:
            if "message" in response:
                return response["message"]["content"]
        except Exception:
            pass

        # --- ④ content直 ---
        try:
            if "content" in response:
                return response["content"]
        except Exception:
            pass

        # --- ⑤ fallback ---
        return str(response)