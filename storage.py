# storage.py
import json
import os
from datetime import datetime

class Storage:
    def __init__(self, path: str = 'data/storage.json'):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, default=str)

    def save(self, key: str, value):
        self.data[key] = value
        self._save()

    def load(self, key: str):
        return self.data.get(key, None)
