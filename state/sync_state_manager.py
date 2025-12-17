import json
import os
import tempfile
from datetime import datetime, timezone

class SyncStateManager:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._init_file()

    def _init_file(self):
        self._write({
            "products": {},
            "orders": {}
        })

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        fd, temp_path = tempfile.mkstemp()
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_path, self.path)

    def get(self, domain, system):
        data = self._read()
        ts = data.get(domain, {}).get(f"{system}_last_sync")
        return datetime.fromisoformat(ts) if ts else None

    def update(self, domain, system, dt):
        data = self._read()
        data.setdefault(domain, {})[f"{system}_last_sync"] = dt.astimezone(timezone.utc).isoformat()
        self._write(data)
