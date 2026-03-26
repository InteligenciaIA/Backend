from typing import Any, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3)
    top_k: Optional[int] = None


class ChunkResult(BaseModel):
    texto: str
    score: float
    metadata: dict[str, Any]


class SourceItem(BaseModel):
    tipo: str
    identificador: str
    archivo: Optional[str] = None
    pagina: Optional[int] = None
    chunk_id: str


class AskResponse(BaseModel):
    respuesta: str
    fragmentos: list[ChunkResult]
    fuentes: list[SourceItem]
    debug: dict[str, Any]
