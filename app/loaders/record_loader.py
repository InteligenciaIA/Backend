import csv
from pathlib import Path


def row_to_text(row: dict) -> str:
    ordered_pairs = [f'{key}: {value}' for key, value in row.items() if value not in (None, '')]
    return '\n'.join(ordered_pairs)



def load_records_as_documents(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []

    rows: list[dict] = []
    with csv_path.open('r', encoding='utf-8-sig', newline='') as file:
        reader = csv.DictReader(file)
        for row_number, row in enumerate(reader, start=1):
            identifier = row.get('id') or row.get('ticket_id') or row.get('codigo') or f'fila-{row_number}'
            rows.append(
                {
                    'text': row_to_text(row),
                    'metadata': {
                        'tipo_fuente': 'base_de_datos',
                        'archivo': csv_path.name,
                        'pagina': None,
                        'identificador': str(identifier),
                    },
                }
            )
    return rows
