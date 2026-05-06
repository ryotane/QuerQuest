class DebateAgent:

    def debate(self, question, results):

        # 超軽量版（本格版は後でLLM多重化）

        pro = f"[PRO] {question}は有効なタスク"
        con = f"[CON] 実行結果は不完全かもしれない"

        verdict = "approve" if len(results) > 0 else "retry"

        return {
            "pro": pro,
            "con": con,
            "verdict": verdict
        }

# 既存クラスのインスタンスキャッシュ（オプション）
_instance = None
def _get_instance():
    global _instance
    if _instance is None:
        _instance = YourExistingClass()
    return _instance