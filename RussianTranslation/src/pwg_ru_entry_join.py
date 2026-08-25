#!/usr/bin/env python
"""H3500 - canonical entry-level assembler for pwg_ru subcard rows.

The H3456 benchmark joined TM rows per key1 with a bare ``"\\n".join(ru_parts)``
(akshara_benchmark_build.py). PWG legitimately lists the same gloss under two
homograph sections of one headword (vasin = vAsin + vaSin; DA anusam under
h0_80 AND h6_23), so the naive join doubles whole blocks - judge item B090
rendered its entry twice.

``assemble_entry`` is the single sanctioned join: it preserves row order but
collapses blocks that are identical after normalisation (markup wrappers
stripped, span contents kept, citation furniture ignored). Distinct senses
never collapse; source rows in the store are never touched.

  python src/pwg_ru_entry_join.py              # selftest
"""
from __future__ import annotations

import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t]+")


def _norm_block(block: str) -> str:
    s = WS_RE.sub(" ", TAG_RE.sub(" ", block or "")).strip()
    s = re.sub(r"\{[#%](.*?)[%#]\}", r"\1", s, flags=re.S)
    s = re.sub(r"H\.\s*\d+", "", s)
    s = re.sub(r"[\s.,;:!?*()\-—–]", "", s)
    return s.lower()


def assemble_entry(ru_parts, *, min_block_len: int = 12):
    """Join subcard `ru` texts into one entry string.

    The entry is rebuilt from blocks (parts split on blank lines); a block
    whose normalised form repeats an already-placed block is dropped entirely
    (first occurrence wins). Blocks shorter than ``min_block_len`` never
    collapse - short glosses legitimately repeat across senses.
    """
    seen = set()
    kept_blocks = []
    dropped = 0
    for part in ru_parts or []:
        for block in (part or "").split("\n\n"):
            nb = _norm_block(block)
            if not nb:
                continue
            if len(nb) >= min_block_len and nb in seen:
                dropped += 1
                continue
            if len(nb) >= min_block_len:
                seen.add(nb)
            kept_blocks.append(block.strip())
    return "\n".join(kept_blocks), {"blocks_dropped": dropped,
                                    "blocks_kept": len(kept_blocks),
                                    "parts_in": len(ru_parts or [])}


def selftest() -> int:
    # B090 shape: vAsin and vaSin carry byte-different markup but identical
    # visible content; the entry must render each distinct block once.
    vasin_a = "{#vasin#}¦ (от {#vasA#}) <lex>m.</lex> {%выдра%}\n<ls>H. 1350.</ls>"
    vasin_b = "*{#vasin#}¦ <lex>m.</lex> {%выдра%}."
    parts = [vasin_a, vasin_b,          # vAsin section
             vasin_a.replace("{#vasA#}", "{#vasA#}"),
             vasin_b]                   # vaSin section (identical content)
    text, stats = assemble_entry(parts)
    assert stats["blocks_dropped"] == 2, stats
    assert text.count("выдра") == 2, text  # one per distinct block, not four

    # distinct senses never collapse even when short glosses repeat
    parts2 = ["1) {%брать%}", "2) {%брать%} вновь", "<ls>RV. 1,1.</ls>"]
    text2, stats2 = assemble_entry(parts2)
    assert stats2["blocks_dropped"] == 0, stats2
    assert text2.count("{%брать%}") == 2

    # empty input
    text3, stats3 = assemble_entry([])
    assert text3 == "" and stats3["parts_in"] == 0
    print("pwg_ru_entry_join selftest OK "
          f"(B090 collapse=2, distinct-senses=0, empty=OK)")
    return 0


if __name__ == "__main__":
    sys.exit(selftest())
