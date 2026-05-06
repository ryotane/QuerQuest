import random


class GoalGenerator:

    def generate(self, last_result):

        # 簡易ゴール生成（後でLLM化可能）

        candidates = [
            "最新の技術トレンドを調べる",
            "過去の検索結果を整理する",
            "より詳細に分析する",
            "関連する情報を深掘りする"
        ]

        return random.choice(candidates)