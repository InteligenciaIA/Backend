from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'academic-rag-backend'
    data_dir: Path = Path('data')
    documents_dir: Path = Path('data/documents')
    records_csv_path: Path = Path('data/records/records.csv')
    chroma_dir: Path = Path('data/chroma')
    collection_name: str = 'academic_material'
    embedding_model: str = Field(default='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    chunk_size: int = 700
    chunk_overlap: int = 120
    top_k: int = 4
    similarity_threshold: float = 0.15
    ollama_base_url: str = 'http://localhost:11434'
    ollama_model: str = 'llama3.1:8b'
    use_llm: bool = True


settings = Settings()
