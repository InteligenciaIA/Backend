# Backend RAG académico - Persona A

Este repositorio contiene la parte de **Backend + RAG** del proyecto del curso. Está pensado para un asistente académico que responde preguntas usando PDFs y registros convertidos a texto.

## Qué resuelve
- Lee documentos PDF del curso.
- Convierte registros CSV a texto para tratarlos como otra fuente.
- Aplica limpieza, chunking, embeddings e indexación.
- Guarda los vectores en Chroma.
- Recupera contexto relevante con top-k.
- Construye el prompt y genera una respuesta.
- Devuelve una salida lista para el frontend:

```python
{
    "respuesta": "...",
    "fragmentos": [...],
    "fuentes": [...],
    "debug": {...}
}
```

## Estructura

```text
app/
  api/main.py
  config.py
  schemas.py
  loaders/
  processing/
  embeddings/
  vectorstore/
  llm/
  services/
scripts/
data/
```

## Requisitos
- Python 3.11 o superior
- Git
- Opcional: Ollama para generación local

## Instalación

```bash
python -m venv .venv
```

### Windows
```bash
.venv\Scripts\activate
```

### Linux / macOS
```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
copy .env.example .env
```

En Linux o macOS usa:

```bash
cp .env.example .env
```

## Dónde poner tus archivos
- PDFs del curso en `data/documents/`
- Registros tipo base de datos en `data/records/records.csv`

Puedes usar el archivo de ejemplo `data/records/sample_records.csv` como guía.

## Indexar documentos

```bash
python -m scripts.index_documents
```

## Levantar API

```bash
uvicorn app.api.main:app --reload
```

## Probar pregunta

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"¿Qué debe devolver el backend?"}'
```

## Integración con tus compañeros

### Contrato para frontend
Endpoint:

```http
POST /ask
```

Entrada:

```json
{
  "question": "¿Qué es chunking?",
  "top_k": 4
}
```

Salida:

```json
{
  "respuesta": "...",
  "fragmentos": [
    {
      "texto": "...",
      "score": 0.87,
      "metadata": {
        "tipo_fuente": "documento",
        "archivo": "tema1.pdf",
        "pagina": 5,
        "identificador": "tema1-p5",
        "chunk_id": "tema1-p5-c1",
        "chunk_number": 1
      }
    }
  ],
  "fuentes": [
    {
      "tipo": "documento",
      "identificador": "tema1-p5",
      "archivo": "tema1.pdf",
      "pagina": 5,
      "chunk_id": "tema1-p5-c1"
    }
  ],
  "debug": {
    "retrieval_seconds": 0.12,
    "generation_seconds": 1.30,
    "top_k": 4,
    "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "chunk_size": 700,
    "chunk_overlap": 120
  }
}
```

### Qué debe hacer Persona B
- Mostrar `respuesta`
- Mostrar `fragmentos`
- Mostrar `fuentes`
- Mostrar mensaje cuando la respuesta sea: `No tengo evidencia suficiente en los documentos recuperados.`

### Qué debe hacer Persona C
- Tomar `debug` y `fragmentos` para medir calidad
- Comparar chunk sizes, top-k y modelos
- Usar `scripts/run_experiments.py`

## GitHub recomendado

### Primera subida
```bash
git init
git add .
git commit -m "feat: backend RAG base"
```

Luego crea un repositorio vacío en GitHub y ejecuta:

```bash
git remote add origin TU_URL_DEL_REPO
git branch -M main
git push -u origin main
```

### Trabajo diario
```bash
git checkout -b feature/chunking
# haces cambios
git add .
git commit -m "feat: improve chunking metadata"
git push -u origin feature/chunking
```

## Ramas sugeridas
- `main` -> estable
- `dev` -> integración
- `feature/backend-rag`
- `feature/api`
- `feature/experiments`

## Experimentos obligatorios
El script `scripts/run_experiments.py` te deja comparar:
- 2 tamaños de chunk
- 2 valores de k
- 2 modelos de embeddings

## Siguiente paso recomendado
1. Colocar 30 a 50 documentos reales.
2. Indexarlos.
3. Probar 15 a 20 preguntas reales.
4. Compartir el endpoint `/ask` con el frontend.
5. Pasar resultados de experimentos a tu compañero de evaluación.
