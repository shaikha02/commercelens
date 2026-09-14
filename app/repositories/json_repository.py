from collections.abc import Mapping
import json
from json import JSONDecodeError
from pathlib import Path
from threading import Lock
from types import MappingProxyType
from typing import Any


class JsonRepository:
    """Loads local JSON fixture collections and caches them for the process lifetime."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._collection_cache: dict[str, tuple[Mapping[str, Any], ...]] = {}
        self._cache_lock = Lock()

    def load_collection(self, filename: str) -> tuple[Mapping[str, Any], ...]:
        if filename in self._collection_cache:
            return self._collection_cache[filename]

        with self._cache_lock:
            if filename in self._collection_cache:
                return self._collection_cache[filename]

            path = (self.data_dir / filename).resolve()
            try:
                with path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
            except FileNotFoundError as exc:
                raise ValueError(f"Fixture file not found: {filename}") from exc
            except JSONDecodeError as exc:
                raise ValueError(f"Fixture file contains invalid JSON: {filename}") from exc
            if not isinstance(data, list):
                raise ValueError(f"Expected {filename} to contain a JSON array")
            collection = []
            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"Expected {filename}[{index}] to contain a JSON object")
                collection.append(MappingProxyType(item))
            self._collection_cache[filename] = tuple(collection)
            return self._collection_cache[filename]
