"""H2375 helper: extract the nakzatra card prompt + schema for the Agent proof run.

Writes:
  pwg_ru/h2313/raw/nakzatra_prompt.txt   -- full production prompt (stdin for the call)
  pwg_ru/h2313/raw/nakzatra_schema.json  -- output_schema

Run from RussianTranslation/:
  python src/pilot/h2375_prompt_extract.py
"""
import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from headless_worker import build_prompt  # noqa: E402

MANIFEST_PATH = os.path.join(HERE, 'h1209_slice3.manifest.json')
OUT_DIR = os.path.normpath(os.path.join(HERE, '..', '..', 'pwg_ru', 'h2313', 'raw'))
KEY = 'nakzatra'

with open(MANIFEST_PATH, encoding='utf-8') as fh:
    manifest = json.load(fh)

prompt = build_prompt(manifest, [KEY])
schema = manifest.get('output_schema', {})
model = manifest.get('model', 'unknown')

os.makedirs(OUT_DIR, exist_ok=True)
prompt_path = os.path.join(OUT_DIR, 'nakzatra_prompt.txt')
schema_path = os.path.join(OUT_DIR, 'nakzatra_schema.json')

with open(prompt_path, 'w', encoding='utf-8') as fh:
    fh.write(prompt)
with open(schema_path, 'w', encoding='utf-8') as fh:
    json.dump(schema, fh, ensure_ascii=False, indent=2)

print('model         :', model)
print('prompt chars  :', len(prompt))
print('prompt head   :', repr(prompt[:120]))
print('schema keys   :', list(schema.keys()) if isinstance(schema, dict) else type(schema).__name__)
print('prompt ->', prompt_path)
print('schema ->', schema_path)
