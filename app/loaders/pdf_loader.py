from pathlib import Path
from pypdf import PdfReader


def load_pdf_pages(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    pages: list[dict] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ''
        text = text.strip()
        if not text:
            continue
        pages.append(
            {
                'text': text,
                'metadata': {
                    'tipo_fuente': 'documento',
                    'archivo': pdf_path.name,
                    'pagina': index,
                    'identificador': f'{pdf_path.stem}-p{index}',
                },
            }
        )
    return pages
