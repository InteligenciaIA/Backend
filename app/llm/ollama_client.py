from __future__ import annotations

import requests


class OllamaClient:
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip('/')
        self.model = model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f'{self.base_url}/api/generate',
            json={'model': self.model, 'prompt': prompt, 'stream': False},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get('response', '').strip()


def fallback_answer(context_blocks: list[dict]) -> str:
    if not context_blocks:
        return 'No tengo evidencia suficiente en los documentos recuperados.'
    strongest = context_blocks[0]['texto']
    return f'Respuesta basada en el fragmento más relevante:\n\n{strongest[:700]}'
