import json
from pathlib import Path
from typing import Any


class JsonRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def load_collection(self, filename: str) -> list[dict[str, Any]]:
        path = (self.data_dir / filename).resolve()
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Expected {filename} to contain a JSON array")
        return data
