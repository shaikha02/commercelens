from typing import Any

from pydantic import BaseModel


class LineageNode(BaseModel):
    id: str
    type: str
    label: str
    status: str
    metadata: dict[str, Any] = {}


class LineageEdge(BaseModel):
    source: str
    target: str
    type: str


class LineageGraph(BaseModel):
    invoice_id: str
    nodes: list[LineageNode]
    edges: list[LineageEdge]
