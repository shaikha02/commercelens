from collections.abc import Mapping
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any


class JsonRepository:
    """Loads local JSON fixture collections and caches them for the process lifetime."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._collection_cache: dict[str, tuple[Mapping[str, Any], ...]] = {}

    def load_collection(self, filename: str) -> tuple[Mapping[str, Any], ...]:
        if filename in self._collection_cache:
            return self._collection_cache[filename]

        path = (self.data_dir / filename).resolve()
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Expected {filename} to contain a JSON array")
        collection = tuple(MappingProxyType(item) for item in data)
        self._collection_cache[filename] = collection
        return collection
