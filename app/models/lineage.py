from typing import Any

from pydantic import BaseModel, Field


class LineageNode(BaseModel):
    id: str
    type: str
    label: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LineageEdge(BaseModel):
    source: str
    target: str
    type: str


class LineageGraph(BaseModel):
    invoice_id: str
    nodes: list[LineageNode]
    edges: list[LineageEdge]
