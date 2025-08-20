import os
class StorageAdapter:
    def __init__(self):
        self.mode = "local"
        self.memory = {}
        self.supabase_url = os.environ.get("SUPABASE_URL","")
        self.supabase_key = os.environ.get("SUPABASE_KEY","")
        if self.supabase_url and self.supabase_key:
            self.mode = "supabase"
    def save(self, key, value):
        self.memory[key] = value
    def load(self, key):
        return self.memory.get(key)
    def list_keys(self):
        return list(self.memory.keys())
