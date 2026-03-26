from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    metadata: dict


class SimpleChunker:
    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError('chunk_overlap debe ser menor que chunk_size')
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_document(self, text: str, metadata: dict) -> list[TextChunk]:
        chunks: list[TextChunk] = []
        start = 0
        chunk_number = 1
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = f"{metadata['identificador']}-c{chunk_number}"
                chunks.append(
                    TextChunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        metadata={**metadata, 'chunk_id': chunk_id, 'chunk_number': chunk_number},
                    )
                )
            if end == len(text):
                break
            start = max(0, end - self.chunk_overlap)
            chunk_number += 1
        return chunks

    def split_many(self, documents: list[dict]) -> list[TextChunk]:
        output: list[TextChunk] = []
        for doc in documents:
            output.extend(self.split_document(doc['text'], doc['metadata']))
        return output
