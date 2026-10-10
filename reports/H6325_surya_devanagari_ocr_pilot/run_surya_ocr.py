#!/usr/bin/env python3
"""H6325 surya OCR runner — datalab-to/surya (Surya 2) over the specimen plates.
Writes outputs/surya/<id>.txt (one line per text block) + raw JSON next to it.
Usage: run_surya_ocr.py <plates_dir> <out_dir> [--keep-server]
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

plates_dir = Path(sys.argv[1])
out_dir = Path(sys.argv[2]) / "surya"
out_dir.mkdir(parents=True, exist_ok=True)
raw_dir = out_dir / "raw_json"
raw_dir.mkdir(exist_ok=True)

keep = "--keep-server" in sys.argv
paths = [p for p in (plates_dir / "plates.txt").read_text(encoding="utf-8").splitlines() if p.strip()]

surya_bin = str(Path(sys.executable).parent / "surya_ocr")
# Surya 2 CLI: one INPUT_PATH (dir or file); language auto-detected, no --languages flag (v0.20+ schema)
cmd = [
    surya_bin, str(plates_dir),
    "--output_dir", str(raw_dir),
]
if keep:
    cmd.append("--keep_server")
print("RUN:", " ".join(cmd), flush=True)
subprocess.run(cmd, check=True)

# Flatten results JSON -> per-plate txt.
# Surya 2 writes ONE results.json keyed by file stem: {stem: [ {blocks:[{html,...}]}, ... ]}
res_files = sorted(raw_dir.rglob("results.json"))
per_plate = {}
for jf in res_files:
    data = json.loads(jf.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        for stem, docs in data.items():
            parts = []
            for doc in docs if isinstance(docs, list) else [docs]:
                for block in sorted(doc.get("blocks", []), key=lambda b: b.get("reading_order", 0)):
                    html = block.get("html", "")
                    text = ""
                    in_tag = False
                    for ch in html:
                        if ch == "<":
                            in_tag = True
                        elif ch == ">":
                            in_tag = False
                        elif not in_tag:
                            text += ch
                    text = text.strip()
                    if text:
                        parts.append(text)
            per_plate[stem] = parts
for p in paths:
    plate_id = Path(p).stem
    txt_parts = per_plate.get(plate_id, [])
    (out_dir / f"{plate_id}.txt").write_text("\n".join(txt_parts) + "\n", encoding="utf-8")
    print(f"surya: {plate_id} -> {len(txt_parts)} blocks", flush=True)
print("surya complete")
