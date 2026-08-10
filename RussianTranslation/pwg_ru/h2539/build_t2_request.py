"""Build the H2539 Ticket 2 request prompt from the FROZEN v1.144.28 canary fixture.

The prompt is generated (not hand-typed) so the inlined skeleton/portrait and the
provenance hashes are read from the fixture itself and cannot drift from the
schema constants the recorder validates against.
Run: python pwg_ru/h2539/build_t2_request.py
"""
import hashlib
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = Path(__file__).resolve().parent
CANARY = HERE.parent / 'h994' / 'canary'
RAW = CANARY / 'dq_canary_puregloss~~h0_zz_pw.raw.txt'
PORTRAIT = CANARY / 'dq_canary_puregloss~~h0_zz_pw.portrait.json'
OUT = HERE / 'evidence' / 't2_request.json'

raw_bytes = RAW.read_bytes()
portrait_bytes = PORTRAIT.read_bytes()
raw_sha = hashlib.sha256(raw_bytes).hexdigest()
portrait_sha = hashlib.sha256(portrait_bytes).hexdigest()

skeleton = raw_bytes.decode('utf-8')
portrait = portrait_bytes.decode('utf-8')

# Cross-check against the frozen manifest so a fixture/manifest divergence is
# caught here rather than after the last reservation is spent.
manifest = json.loads(
    (CANARY / 'dq_canary_puregloss~~h0_zz_pw.manifest.v2.json').read_text(encoding='utf-8'))
declared = manifest['meta']['input_hashes']['dq_canary_puregloss~~h0_zz_pw']
assert declared['raw_sha256'] == raw_sha, (declared['raw_sha256'], raw_sha)
assert declared['portrait_sha256'] == portrait_sha, (
    declared['portrait_sha256'], portrait_sha)

PROMPT = """You are producing the Russian scholarly entry for ONE PWG headword card \
(Petersburg Sanskrit Dictionary, Böhtlingk-Roth 1855-75).

Return a single JSON object as your ONLY output. No prose, no explanation, no \
markdown fences, no commentary before or after — only the JSON object itself.

=== INPUT CARD (translate EXACTLY what is inlined; do not open files, do not call \
tools, do not supply senses from memory) ===

key1: dq_canary_puregloss

--- masked German skeleton ---
{skeleton}
--- portrait ---
{portrait}

=== TASK ===

The card has THREE senses. Render EVERY sense, in source order, as its own sense \
object. Do not drop, merge, reorder, or add a sense.

For each sense:
- "tag": the sense number as printed — "1", "2", "3".
- "german": reproduce that sense's German skeleton line EXACTLY as given above, \
including the {{%…%}} gloss delimiters verbatim. Do not strip, clean, or trim the markup.
- "russian": the Russian rendering in scholarly-philological register. Russian \
(Cyrillic) only — no German, English, or Latin words, no {{Tn}} placeholders, no \
transliterated Sanskrit. Never write the letter ё (write е instead).
- "equivalence_type": "equivalent" for a 1-2 word equivalent, "explanatory" for a \
descriptive gloss.
- "source_type": "lexicographic" (this card carries no text citation).
- "government": [] — the German states no case-government marker, so invent none.

=== REQUIRED OUTPUT SHAPE ===

{{
  "schema_marker": "pwg_ru.canary_final.v1",
  "provenance": {{
    "provenance_class": "synthetic_control",
    "route": "router-cheap-agent",
    "model": "claude-opus-5",
    "raw_sha256": "{raw_sha}",
    "portrait_sha256": "{portrait_sha}",
    "source_senses": 3,
    "promotable": false
  }},
  "cards": [
    {{
      "key1": "dq_canary_puregloss",
      "iast": "",
      "notes": "",
      "records": [
        {{
          "h": "0",
          "grammar": "",
          "senses": [
            {{ "tag": "1", "german": "<sense 1 skeleton verbatim>", "russian": "<Russian>", \
"equivalence_type": "<equivalent|explanatory>", "source_type": "lexicographic", "government": [] }},
            {{ "tag": "2", "german": "<sense 2 skeleton verbatim>", "russian": "<Russian>", \
"equivalence_type": "<equivalent|explanatory>", "source_type": "lexicographic", "government": [] }},
            {{ "tag": "3", "german": "<sense 3 skeleton verbatim>", "russian": "<Russian>", \
"equivalence_type": "<equivalent|explanatory>", "source_type": "lexicographic", "government": [] }}
          ]
        }}
      ]
    }}
  ]
}}

Every field above is REQUIRED and no additional field is permitted at any level. \
Copy the provenance values exactly as shown — they are fixed constants, not \
values for you to compute or change. Exactly one card, exactly one record, \
exactly three senses.""".format(
    skeleton=skeleton.rstrip('\n'),
    portrait=portrait.rstrip('\n'),
    raw_sha=raw_sha,
    portrait_sha=portrait_sha,
)

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, 'w', encoding='utf-8', newline='\n') as handle:
    json.dump({'prompt': PROMPT}, handle, ensure_ascii=False, indent=2, sort_keys=True)
    handle.write('\n')

print('raw_sha256      =', raw_sha)
print('portrait_sha256 =', portrait_sha)
print('manifest cross-check: OK')
print('wrote', OUT.relative_to(HERE.parents[1]))
print('prompt chars =', len(PROMPT))
