class StorageAdapter:
    def __init__(self):
        self.memory = {}
    def save(self, key, value):
        self.memory[key] = value
    def load(self, key):
        return self.memory.get(key)
    def list_keys(self):
        return list(self.memory.keys())
