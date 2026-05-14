class MemoryManager:

    def __init__(self, memory, max_items=1000):
        self.memory = memory
        self.max_items = max_items

    def compress(self):

        if len(self.memory.store) <= self.max_items:
            return

        # 古いデータ削除
        overflow = len(self.memory.store) - self.max_items
        self.memory.store = self.memory.store[overflow:]