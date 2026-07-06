#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""synth_de_first.py — Deliverable 3 comparison pilot of H180 (SYNTHESIS_PILOT_10.md).

Arm B of the bake-off: SYNTHESIZE-GERMAN-FIRST. For 10 maximally-diverse
headwords, assemble ALL layers' German (`de`) into one input, then (as a
separate, tagged model step) synthesize ONE coherent German entry and translate
THAT to Russian — to test whether synthesize-first ever beats the free
after-translation remix (Arm A, build_reglue.py).

This script does the **deterministic, zero-cost half** now: it assembles each
headword's per-layer German and writes the two model prompts + a manifest.
The actual generation is an **isolated, pilot-only model run** (NOT the
production translate pipeline) driven by the Claude Workflow tool — the repo has
no Python HTTP client and Arm B must not touch production. Every Arm-B
generation MUST be stamped with model tier + exact version
([[feedback_state_model_tier]]); the manifest records the intended model ids.

Arm B is a CALIBRATION PROBE ONLY. Running it does not commit the corpus to
synthesize-first, and it must not mutate the canonical layered store.

Inputs  : src/pwg_ru_translated.jsonl
Outputs : pwg_ru/reglue/synth_inputs/<key1>.de.txt      (assembled German, all layers)
          pwg_ru/reglue/synth_inputs/<key1>.prompts.json (synthesize + translate prompts)
          pwg_ru/reglue/synth_inputs/MANIFEST.tsv        (10-word bake-off manifest)

Run: python src/synth_de_first.py
"""
import sys, os, io, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
STORE = os.path.join(HERE, "pwg_ru_translated.jsonl")
OUTDIR = os.path.join(ROOT, "pwg_ru", "reglue", "synth_inputs")

# The 10 words (SYNTHESIS_PILOT_10.md) — span the full 1->5 layer range.
PILOT10 = ["dah", "As", "car", "siD", "viS", "Ap", "DA", "Cid", "gA", "Sam"]

# Intended Arm-B models (tier + exact version — never a bare tier).
SYNTH_MODEL = ("Opus 4.8", "claude-opus-4-8")      # coherent German synthesis
TRANS_MODEL = ("Sonnet 5", "claude-sonnet-5")      # matches production translate tier

LAYER_ORDER = ["pwg", "pw", "sch", "pwkvn", "nws"]

SYNTH_PROMPT = (
    "Du bist Lexikograph des Petersburger Wörterbuchs. Unten stehen ALLE "
    "Schicht-Fragmente (PWG-Skelett + Ergänzungen PW/SCH/PWKVN/NWS) zu EINEM "
    "Stichwort. Verschmilz sie zu EINEM kohärenten deutschen Eintrag: PWG bleibt "
    "das Gerüst, Ergänzungen an ihre passende Bedeutung einsortieren, "
    "Widersprüche (z.B. PW streicht/korrigiert PWG) explizit vermerken, nichts "
    "erfinden, jede Bedeutung und jeden Beleg (<ls>) erhalten. Gib nur den "
    "fusionierten deutschen Eintrag zurück."
)
TRANS_PROMPT = (
    "Übersetze den folgenden fusionierten deutschen Wörterbucheintrag ins "
    "Russische. Sanskrit ({#…#}/{%…%}), Grammatik-Abkürzungen (<lex>) und "
    "Quellen (<ls>) unverändert lassen; nur die deutsche Prosa übersetzen."
)


def homonym_of(subcard):
    m = re.search(r"~~(h\d+)", subcard or "")
    return m.group(1) if m else "h0"


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    by_key = collections.defaultdict(list)
    with io.open(STORE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                d = json.loads(line)
                if d["key1"] in PILOT10:
                    by_key[d["key1"]].append(d)

    manifest = []
    for key1 in PILOT10:
        recs = by_key.get(key1, [])
        layers = sorted({d.get("layer") for d in recs},
                        key=lambda L: LAYER_ORDER.index(L) if L in LAYER_ORDER else 9)
        # assemble German by layer, in fixed layer order
        blocks = []
        for L in LAYER_ORDER:
            frags = [d for d in recs if d.get("layer") == L]
            if not frags:
                continue
            blocks.append(f"=== LAYER {L.upper()} ({len(frags)} Fragmente) ===")
            for d in sorted(frags, key=lambda x: (homonym_of(x["subcard"]), str(x.get("sense_tag")))):
                st = d.get("sense_tag")
                blocks.append(f"[{homonym_of(d['subcard'])} · {st}] {d.get('de','')}")
        de_text = "\n".join(blocks)

        with io.open(os.path.join(OUTDIR, f"{key1}.de.txt"), "w", encoding="utf-8") as fh:
            fh.write(de_text + "\n")
        prompts = {
            "key1": key1,
            "layers": layers,
            "n_subcards": len(recs),
            "synthesize": {"model_tier": SYNTH_MODEL[0], "model_version": SYNTH_MODEL[1],
                           "system": SYNTH_PROMPT, "input_file": f"{key1}.de.txt"},
            "translate": {"model_tier": TRANS_MODEL[0], "model_version": TRANS_MODEL[1],
                          "system": TRANS_PROMPT, "input": "<synthesized German from step 1>"},
        }
        with io.open(os.path.join(OUTDIR, f"{key1}.prompts.json"), "w", encoding="utf-8") as fh:
            json.dump(prompts, fh, ensure_ascii=False, indent=1)

        manifest.append((key1, len(layers), len(recs), "+".join(layers)))
        print(f"  {key1:6s} layers={len(layers)} subcards={len(recs):4d} ({'+'.join(layers)})")

    with io.open(os.path.join(OUTDIR, "MANIFEST.tsv"), "w", encoding="utf-8") as fh:
        fh.write("key1\tn_layers\tn_subcards\tlayers\tsynth_model\ttranslate_model\n")
        for key1, nl, ns, ls in manifest:
            fh.write(f"{key1}\t{nl}\t{ns}\t{ls}\t{SYNTH_MODEL[1]}\t{TRANS_MODEL[1]}\n")

    print(f"\nassembled Arm-B inputs for {len(manifest)}/10 words (deterministic, zero-cost).")
    print(f"wrote {OUTDIR}\\*.de.txt, *.prompts.json, MANIFEST.tsv")
    print("NEXT (tagged model run, isolated): synthesize German (Opus 4.8) -> translate "
          "(Sonnet 5) per word, then score both arms on the six axes in SYNTHESIS_PILOT_10.md.")


if __name__ == "__main__":
    main()
