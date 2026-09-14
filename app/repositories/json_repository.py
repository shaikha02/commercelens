import json
from pathlib import Path
from typing import Any


class JsonRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._collection_cache: dict[str, list[dict[str, Any]]] = {}

    def load_collection(self, filename: str) -> list[dict[str, Any]]:
        if filename in self._collection_cache:
            return self._collection_cache[filename]

        path = (self.data_dir / filename).resolve()
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Expected {filename} to contain a JSON array")
        self._collection_cache[filename] = data
        return data
