from __future__ import annotations

import time
from pathlib import Path

from app.config import settings
from app.embeddings.embedder import Embedder
from app.llm.ollama_client import OllamaClient, fallback_answer
from app.loaders.pdf_loader import load_pdf_pages
from app.loaders.record_loader import load_records_as_documents
from app.processing.chunker import SimpleChunker
from app.processing.text_cleaner import clean_text
from app.vectorstore.chroma_store import ChromaVectorStore

NO_EVIDENCE = 'No tengo evidencia suficiente en los documentos recuperados.'


class RAGService:
    def __init__(
        self,
        embedding_model: str | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.embedding_model = embedding_model or settings.embedding_model
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.embedder = Embedder(self.embedding_model)
        self.vector_store = ChromaVectorStore(
            persist_directory=str(settings.chroma_dir),
            collection_name=collection_name or settings.collection_name,
        )
        self.chunker = SimpleChunker(self.chunk_size, self.chunk_overlap)
        self.llm = OllamaClient(settings.ollama_base_url, settings.ollama_model)

    def build_index(self, documents_dir: Path | None = None, records_csv: Path | None = None, reset: bool = True) -> dict:
        docs_dir = documents_dir or settings.documents_dir
        records_path = records_csv or settings.records_csv_path

        raw_documents: list[dict] = []
        for pdf_path in sorted(docs_dir.glob('*.pdf')):
            raw_documents.extend(load_pdf_pages(pdf_path))
        raw_documents.extend(load_records_as_documents(records_path))

        prepared_documents = [
            {'text': clean_text(doc['text']), 'metadata': doc['metadata']}
            for doc in raw_documents
            if clean_text(doc['text'])
        ]

        chunks = self.chunker.split_many(prepared_documents)
        if reset:
            self.vector_store.reset()

        if not chunks:
            return {'documents': 0, 'chunks': 0, 'collection_count': self.vector_store.count()}

        ids = [chunk.chunk_id for chunk in chunks]
        texts = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        embeddings = self.embedder.encode_texts(texts)
        self.vector_store.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

        return {
            'documents': len(prepared_documents),
            'chunks': len(chunks),
            'collection_count': self.vector_store.count(),
        }

    def retrieve(self, question: str, top_k: int | None = None) -> list[dict]:
        chosen_k = top_k or settings.top_k
        query_embedding = self.embedder.encode_query(question)
        result = self.vector_store.query(query_embedding, chosen_k)

        docs = result.get('documents', [[]])[0]
        metadatas = result.get('metadatas', [[]])[0]
        distances = result.get('distances', [[]])[0]
        ids = result.get('ids', [[]])[0]

        chunks: list[dict] = []
        for doc, meta, distance, chunk_id in zip(docs, metadatas, distances, ids):
            score = 1 - float(distance)
            if score < settings.similarity_threshold:
                continue
            chunks.append({'id': chunk_id, 'texto': doc, 'metadata': meta, 'score': round(score, 4)})
        chunks.sort(key=lambda item: item['score'], reverse=True)
        return chunks

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = []
        for index, chunk in enumerate(chunks, start=1):
            meta = chunk['metadata']
            source_line = (
                f"[{index}] tipo={meta.get('tipo_fuente')} | archivo={meta.get('archivo')} | "
                f"pagina={meta.get('pagina')} | identificador={meta.get('identificador')}"
            )
            context.append(f'{source_line}\n{chunk["texto"]}')

        context_text = '\n\n'.join(context)
        return f'''Eres un asistente académico para cursos.
Responde únicamente con base en el contexto recuperado.
Si no hay evidencia suficiente, responde exactamente: {NO_EVIDENCE}
Resume de forma clara y luego lista las fuentes realmente usadas.

Contexto recuperado:
{context_text}

Pregunta:
{question}
'''

    def answer_question(self, question: str, top_k: int | None = None) -> dict:
        started_at = time.perf_counter()
        retrieved = self.retrieve(question, top_k=top_k)
        retrieval_seconds = round(time.perf_counter() - started_at, 4)

        if not retrieved:
            return {
                'respuesta': NO_EVIDENCE,
                'fragmentos': [],
                'fuentes': [],
                'debug': {'retrieval_seconds': retrieval_seconds, 'generation_seconds': 0, 'top_k': top_k or settings.top_k},
            }

        prompt = self.build_prompt(question, retrieved)
        generation_started = time.perf_counter()
        if settings.use_llm:
            try:
                answer = self.llm.generate(prompt)
            except Exception:
                answer = fallback_answer(retrieved)
        else:
            answer = fallback_answer(retrieved)
        generation_seconds = round(time.perf_counter() - generation_started, 4)

        fuentes = []
        for chunk in retrieved:
            meta = chunk['metadata']
            fuentes.append(
                {
                    'tipo': meta.get('tipo_fuente', 'desconocido'),
                    'identificador': meta.get('identificador', chunk['id']),
                    'archivo': meta.get('archivo'),
                    'pagina': meta.get('pagina'),
                    'chunk_id': chunk['id'],
                }
            )

        fragmentos = [
            {'texto': chunk['texto'], 'score': chunk['score'], 'metadata': chunk['metadata']}
            for chunk in retrieved
        ]

        return {
            'respuesta': answer.strip() if answer.strip() else NO_EVIDENCE,
            'fragmentos': fragmentos,
            'fuentes': fuentes,
            'debug': {
                'retrieval_seconds': retrieval_seconds,
                'generation_seconds': generation_seconds,
                'top_k': top_k or settings.top_k,
                'embedding_model': self.embedding_model,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap,
            },
        }
