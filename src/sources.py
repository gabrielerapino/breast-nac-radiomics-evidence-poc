"""Offline primary-source ingestion with identity and integrity checks."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + '\n'

@lru_cache(maxsize=16)
def soup(file):
    return BeautifulSoup((ROOT / 'sources' / file).read_text(), 'html.parser')

def paragraph(evidence):
    if 'paragraph' not in evidence:
        row=table(evidence['file'],evidence['table'])[evidence['row']]
        return ' | '.join(row) if evidence['column'] is None else row[evidence['column']]
    return soup(evidence['file']).find_all('p')[evidence['paragraph']].get_text(' ', strip=True)

def table(file, number):
    node = soup(file).find_all('table')[number-1]
    return [[c.get_text(' ', strip=True) for c in r.find_all(['th','td'], recursive=False)] for r in node.find_all('tr')]

def ingest():
    records = load_json(ROOT / 'inputs' / 'reviewed_studies.json')
    manifest = load_json(ROOT / 'inputs' / 'source_manifest.json')
    for entry in manifest:
        data = (ROOT / 'sources' / entry['file']).read_bytes()
        if digest(data) != entry['sha256']:
            raise ValueError('Source integrity failure: ' + entry['file'])
    if len(records) != 4 or len({r['study_id'] for r in records}) != 4:
        raise ValueError('Expected four unique primary studies')
    for record in records:
        file = record['study_id'] + '.html'
        text = soup(file).get_text(' ', strip=True)
        if record['doi'] not in text or len(text) < 10000 or not soup(file).find_all('table'):
            raise ValueError('Source identity/full-text check failed: ' + file)
        for field in record['fields'].values():
            ev = field['evidence']
            if digest(paragraph(ev).encode()) != ev['sha256']:
                raise ValueError('Paragraph integrity failure: ' + file)
    return records

def source_location(record, ev):
    if 'paragraph' in ev:
        return f"{record['source_url']} | {ev['section']} | sources/{ev['file']} paragraph {ev['paragraph']}"
    return f"{record['source_url']} | Table {ev['table']} | sources/{ev['file']} row {ev['row']} column {ev['column']}"
