class LoopController:

    def __init__(self, max_steps=5):
        self.max_steps = max_steps

    def should_continue(self, step, reflection):

        # 最大ステップ
        if step >= self.max_steps:
            return False

        # 失敗続きで停止
        if reflection["status"] == "fail":
            return False

        return True