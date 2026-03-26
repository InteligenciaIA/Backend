from app.services.rag_service import RAGService


if __name__ == '__main__':
    service = RAGService()
    result = service.build_index(reset=True)
    print('Indexación completada:')
    print(result)
