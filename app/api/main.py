from fastapi import FastAPI, HTTPException

from app.config import settings
from app.schemas import AskRequest, AskResponse
from app.services.rag_service import RAGService

app = FastAPI(title=settings.app_name)
rag_service = RAGService()


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'collection_count': rag_service.vector_store.count()}


@app.post('/ask', response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    if rag_service.vector_store.count() == 0:
        raise HTTPException(status_code=400, detail='La base vectorial está vacía. Ejecuta primero el script de indexación.')
    result = rag_service.answer_question(request.question, top_k=request.top_k)
    return AskResponse(**result)
