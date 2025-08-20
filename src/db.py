import os
from typing import Optional, Any, Dict

class StorageAdapter:
    """
    MVP: in-memory adapter with optional Supabase placeholders for future use.
    """
    def __init__(self):
        self.mode = "local"
        self.memory: Dict[str, Any] = {}
        self.supabase_url = os.environ.get("SUPABASE_URL") or ""
        self.supabase_key = os.environ.get("SUPABASE_KEY") or ""
        if self.supabase_url and self.supabase_key:
            # In a real app, initialize supabase client here.
            self.mode = "supabase"

    def save(self, key: str, value: Any):
        if self.mode == "local":
            self.memory[key] = value
        else:
            # TODO: write to Supabase
            self.memory[key] = value

    def load(self, key: str) -> Optional[Any]:
        return self.memory.get(key)

    def list_keys(self):
        return list(self.memory.keys())
