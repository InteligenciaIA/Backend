import csv
from itertools import product
from pathlib import Path

from app.config import settings
from app.services.rag_service import RAGService

QUESTIONS = [
    {
        'question': '¿Cuál es el problema principal del material?',
        'expected_terms': ['estudiantes', 'material', 'PDFs'],
    },
    {
        'question': '¿Qué hace el chunking en un sistema RAG?',
        'expected_terms': ['dividir', 'documentos', 'partes'],
    },
]

CHUNK_CONFIGS = [(500, 100), (800, 150)]
TOP_K_VALUES = [3, 5]
EMBEDDING_MODELS = [
    'sentence-transformers/all-MiniLM-L6-v2',
    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
]


def simple_hit_rate(chunks: list[dict], expected_terms: list[str]) -> float:
    joined = ' '.join(chunk['texto'].lower() for chunk in chunks)
    hits = sum(1 for term in expected_terms if term.lower() in joined)
    return round(hits / max(len(expected_terms), 1), 4)


if __name__ == '__main__':
    output_path = Path('experiments_results.csv')
    rows = []

    for (chunk_size, overlap), top_k, embedding_model in product(CHUNK_CONFIGS, TOP_K_VALUES, EMBEDDING_MODELS):
        service = RAGService(
            embedding_model=embedding_model,
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            collection_name=f'exp_{chunk_size}_{top_k}_{embedding_model.split("/")[-1].replace(":", "_")}',
        )
        service.build_index(reset=True)

        for item in QUESTIONS:
            chunks = service.retrieve(item['question'], top_k=top_k)
            rows.append(
                {
                    'question': item['question'],
                    'chunk_size': chunk_size,
                    'chunk_overlap': overlap,
                    'top_k': top_k,
                    'embedding_model': embedding_model,
                    'hit_rate': simple_hit_rate(chunks, item['expected_terms']),
                    'retrieved_chunks': len(chunks),
                }
            )

    with output_path.open('w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f'Experimentos guardados en {output_path.resolve()}')
