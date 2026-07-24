#!/usr/bin/env python3
"""Definition-typology classifier (WS2.4 / ATLAS_FAIR micro-gap).

Classifies each csl-orig dictionary record's definition body into one of:

  synonym     — definition by synonym list (paryāya / comma-chain of short glosses)
  equivalent  — short translational equivalent (1 short gloss; no clause structure)
  encyclopedic— longer descriptive / paraphrastic / encyclopedic prose
  residual    — empty, pure cross-ref, grammar-only without gloss, non-classifiable

Classical axis: synonym-gloss vs equivalent vs encyclopedic (Wiegand / Svensén /
Landau microstructure typology), operationalised for CDSL digital text.

Outputs (beside this script, unless --out-dir):
  * definition_typology_per_dict.tsv   — per dict × class counts + shares
  * definition_typology_sample.tsv     — stratified sample for hand verification
  * definition_typology_records.tsv.gz — optional full per-record dump (--full)

Usage:
    python definition_typology_classifier.py [--csl-orig PATH] [--dicts mw,pwg,...]
    python definition_typology_classifier.py --verify SAMPLE.tsv

H1483. Run 24-07-2026 by Grok 4.5 (grok-4.5), Opus-lock override.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Core family for the published distribution (union-15 + WIL classical English).
# Codes match csl-orig/v02 directory names. PWK is ``pw`` in csl-orig naming
# for the shorter Petersburg; AP is ``ap90`` (1890) when ``ap`` absent of body.
DEFAULT_DICTS = (
    "mw",
    "pwg",
    "pw",
    "ap90",
    "cae",
    "wil",
    "sch",
    "md",
    "ccs",
    "gra",
    "skd",
    "vcp",
    "bhs",
    "bur",
    "vei",
)

# --- markup strip ------------------------------------------------------------

TAG_RE = re.compile(r"<[^>]+>")
BRACE_RE = re.compile(r"\{[#%@~!|]([^}]*)[#%@~!|]\}")
INFO_RE = re.compile(r"<info[^/]*/>")
MULTISPACE = re.compile(r"\s+")
PIPE_SPLIT = re.compile(r"¦")

# Cross-ref / residual bodies (pure; multi-sense "= X. 1〉 …" is NOT residual)
CROSSREF_RE = re.compile(
    r"^(?:"
    r"q\.?\s*v\.?|"
    r"s\.\s*u\.|"
    r"s\.\s*v\.|"
    r"cf\.|"
    r"vgl\.|"
    r"see\b.*|"
    r"siehe\b.*|"
    r"=\s*\S{1,40}\s*$|"  # pure equation only (short; no multi-sense continuation)
    r"idem\.?|"
    r"ib(?:id)?\.?|"
    r"Lbody=\S+"
    r")\s*$",
    re.I,
)
# "f. = other_lemma" / pure equation to another headword
EQN_HEAD_RE = re.compile(
    r"^(?:(?:m|f|n|mfn|adj|adv|ind)\.?\s*)?=\s*\S+",
    re.I,
)
PURE_GRAM_RE = re.compile(
    r"^(?:"
    r"(?:m|f|n|m\.n\.|mfn|adj|adv|ind|pron|prep|interj|part|v|vb|denom)\.?|"
    r"Pronominalstamm:?|"
    r"Stamm:?|"
    r"Wurzel:?|"
    r"root\.?"
    r")\s*$",
    re.I,
)
# Citation-only / locator-only residue
CITATION_ONLY_RE = re.compile(
    r"^(?:"
    r"[A-ZĀ-ŪṚṢŚ][A-Za-zĀ-ūṛṣś.]*\s+[\d.,;\s]+|"  # CARAKA 1,14 .
    r"in\s+\S+\s*\.?|"
    r"part=.*"
    r")$",
    re.I,
)

# Clause / encyclopedic signals (EN + DE).
# Note: short formulaic "N. of X" / "N. pr." are handled as equivalent below,
# so they are deliberately NOT in this set.
CLAUSE_RE = re.compile(
    r"(?:"
    r"\b(?:who|which|that|whose|where|when|whereby|wherein)\b|"
    r"\b(?:consisting of|belonging to|according to|corresponding to|"
    r"relating to|destined for|denoting|designating|applied to|said of|used for|"
    r"the act of|the state of|the quality of)\b|"
    r"\b(?:welcher|welche|welches|dessen|deren|"
    r"wobei|wodurch|worin|insofern|indem)\b|"
    r"\b(?:eine|einer|einem|einen|eines)\b.+\b(?:der|die|das)\b|"
    r"\b(?:genannt|bezeichnet|bedeutet|heißt|gesponnen|gewebt)\b|"
    r"\bevery day\b|\bday and night\b|"
    r"\ban einem und demselben\b"
    r")",
    re.I,
)
# Short onomastic / name-formula (still a translational equivalent, not prose)
NAME_FORMULA_RE = re.compile(
    r"^(?:(?:m|f|n|mfn|adj)\.?\s*)?"
    r"(?:"
    r"N\.?\s*of\b|"
    r"N\.?\s*pr\.|"
    r"name of\b|"
    r"Name (?:eines|einer|eines|pr\.)\b|"
    r"Bewohner von\b"
    r").{0,60}$",
    re.I,
)

# Synonym-list: 2+ short items separated by , ; or /
# After strip, items of ≤4 content tokens each.
SEP_SPLIT = re.compile(r"\s*[,;/]\s*|\s+—\s+|\s+-\s+")

# SKD/VCP paryāya / synonym-chain signals (IAST-ish roman + SLP1)
PARYAYA_RE = re.compile(
    r"(?:"
    r"paryy?Aya|"
    r"paryaya|"
    r"tulyArtha|"
    r"samAnArtha|"
    r"\biti\s+(?:medinI|tri|amara|haima|viSva)"
    r")",
    re.I,
)

# Tokenisation for content words (Latin + Devanagari ranges left as single blobs)
TOKEN_RE = re.compile(r"[A-Za-zĀāĪīŪūṚṛṜḹḶḷḹĒēŌōṂṃḤḥÑñṬṭḌḍṆṇŚśṢṣ\u0900-\u097F]+")


def strip_markup(raw: str) -> str:
    """Reduce a definition body to plain text for typology features."""
    s = INFO_RE.sub(" ", raw)
    s = BRACE_RE.sub(r" \1 ", s)
    s = TAG_RE.sub(" ", s)
    # drop residual brace markers
    s = re.sub(r"[{}#%@~!|]", " ", s)
    s = s.replace("¦", " ")
    s = MULTISPACE.sub(" ", s).strip()
    return s


def content_tokens(plain: str) -> list[str]:
    return TOKEN_RE.findall(plain)


def extract_records(path: Path):
    """Yield (L_id, k1, body) for each <L>…<LEND> record."""
    L_RE = re.compile(r"<L>([^<]*)")
    K1_RE = re.compile(r"<k1>([^<]*)")
    lid = None
    k1 = ""
    body_parts: list[str] = []
    in_rec = False

    with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
        for line in fh:
            if line.startswith("<L>"):
                if in_rec and lid is not None:
                    yield lid, k1, "\n".join(body_parts)
                m = L_RE.search(line)
                lid = m.group(1) if m else "?"
                km = K1_RE.search(line)
                k1 = km.group(1) if km else ""
                body_parts = []
                in_rec = True
                # body may continue on same line after header fields — rare
                continue
            if line.startswith("<LEND>"):
                if in_rec and lid is not None:
                    yield lid, k1, "\n".join(body_parts)
                lid = None
                k1 = ""
                body_parts = []
                in_rec = False
                continue
            if in_rec:
                # Skip pure letter-section headers
                if line.startswith("<H>"):
                    continue
                body_parts.append(line.rstrip("\n"))
    if in_rec and lid is not None:
        yield lid, k1, "\n".join(body_parts)


def body_after_pipe(raw: str) -> str:
    """Prefer the classical post-¦ definition field when present."""
    if "¦" in raw:
        parts = PIPE_SPLIT.split(raw, maxsplit=1)
        if len(parts) == 2:
            return parts[1]
    return raw


def n_tok_early(s: str) -> int:
    return len(content_tokens(s))


# Trailing citation / apparatus noise stripped before synonym-list heuristics.
_CITATION_TAIL_RE = re.compile(
    r"(?:"
    r",?\s*(?:part=|seq=|type=|n=)[^\s,;]*|"  # SCH apparatus crumbs
    r",?\s*\b(?:L|MBh|R|TS|TBr|AV|VS|MW|H|MED|TRIK|Amit|S|Mgs|"
    r"KAUŚ|VAITĀN|MAHĀVY|DHĀTUP|MṚCCH|MEGH|RĀJA-TAR)\.?\b"
    r"(?:\s*[\d.,;IVXivx/–-]+)*|"
    r",?\s*(?:[A-ZĀ-ŪṚṢŚ][A-Za-zĀ-ūṛṣś.]*\s+[\d.,;IVXivx/–\s]+)+"
    r")+\s*$",
    re.I,
)
# Leading POS / etym-parenthetical crumbs for gloss-core analysis
_POS_LEAD_RE = re.compile(
    r"^(?:(?:m|f|n|mfn|m\.n\.|adj|a|adv|ind|pron|prep|interj|part|v|vb|"
    r"puM|strI|klI|tri|pu0|na0|tri0)\.?\s+)+",
    re.I,
)
_ETYM_PAREN_RE = re.compile(r"\([^)]{0,80}\)")
# Sentence-ending periods only (ignore "m." / "f." / "N." / "pr." abbreviations)
_SENT_END_RE = re.compile(r"(?<![A-Za-zĀ-ū])\.(?=\s|$)")


def strip_apparatus(plain: str) -> str:
    """Drop trailing citation/apparatus crumbs and SCH part= noise."""
    s = re.sub(r"\bpart=[^\s,;]*", " ", plain)
    s = re.sub(r"\bseq=\d+", " ", s)
    s = re.sub(r"\btype=[^\s,;]*", " ", s)
    s = re.sub(r"\bn=\d+", " ", s)
    s = _CITATION_TAIL_RE.sub("", s)
    s = MULTISPACE.sub(" ", s).strip(" ,;.—-")
    return s


def sentence_period_count(plain: str) -> int:
    """Count likely sentence-ending periods, not POS abbreviations."""
    # remove single-letter / short abbreviations before counting
    s = re.sub(r"\b(?:[mfn]|mfn|adj|adv|ind|pr|N|cf|vgl|pl|sg|du)\.", " ", plain, flags=re.I)
    s = re.sub(r"\b[A-ZĀ-Ū]{1,4}\.", " ", s)  # work sigla like MBh.
    return len(_SENT_END_RE.findall(s))


def classify(plain: str) -> tuple[str, str]:
    """Return (class, reason) for stripped definition plain text.

    Priority: residual → synonym → equivalent → encyclopedic.
    """
    if not plain or not plain.strip():
        return "residual", "empty"

    compact = plain.strip(" .;:—-")
    if not compact:
        return "residual", "empty"

    numbered = bool(re.search(r"(?:^|[\s—-])(?:\d+[〉\)]|--\d+\b|—\s*\d)", plain))
    has_emdash_senses = plain.count("—") >= 1 or plain.count("–") >= 2

    if CROSSREF_RE.match(compact):
        return "residual", "crossref"

    # Equation only when body does not continue into multi-sense definition
    if EQN_HEAD_RE.match(compact):
        if numbered or has_emdash_senses or re.search(r"\b\d+〉", plain):
            return "encyclopedic", "eqn_then_senses"
        if n_tok_early(compact) <= 12:
            return "residual", "eqn_head"

    if PURE_GRAM_RE.match(compact):
        return "residual", "grammar_only"
    if CITATION_ONLY_RE.match(compact):
        return "residual", "citation_only"
    if re.match(r"^\d+\.?$", compact):
        return "residual", "empty_sense_num"

    # GRA/etc. stem/form locus without gloss (Stamm X: -form N〉 locus)
    if re.search(r"\bStamm\b", plain, re.I) and not re.search(
        r"\b(?:Adj|m|f|n)\.?\s+\S{3,}", plain, re.I
    ):
        if n_tok_early(plain) <= 12:
            return "residual", "stem_pointer"
    if re.match(r"^[-–—]\w", compact) and re.search(r"\d+〉", plain) and n_tok_early(plain) <= 10:
        return "residual", "form_locus_only"

    if re.search(r"\bLbody=\d+", plain):
        return "residual", "lbody_pointer"

    if n_tok_early(plain) <= 6 and re.search(
        r"\b(?:q\.v\.|s\.u\.|s\.v\.|siehe|see above|s\. above|see\b)\b",
        plain,
        re.I,
    ):
        return "residual", "crossref_short"

    # Quoted long definitions (VCP/SKD style) → encyclopedic early
    # Allow truncated excerpts ending in ellipsis after an opening quote.
    if (
        re.search(r'[“"«].{20,}[”"»]', plain)
        or re.search(r'[“"«].{12,}(?:…|\.\.\.)', plain)
        or re.search(r"ityukte|ityukta|ityāha|ukt[ea]\b", plain, re.I)
    ):
        return "encyclopedic", "quoted_def"

    # Clean apparatus for length / list features
    cleaned = strip_apparatus(plain)
    gloss_core = _POS_LEAD_RE.sub("", cleaned)
    gloss_core = _ETYM_PAREN_RE.sub(" ", gloss_core)
    gloss_core = MULTISPACE.sub(" ", gloss_core).strip(" ,;.—-")

    toks = content_tokens(cleaned)
    n_tok = len(toks)
    n_char = len(cleaned)
    n_sent = sentence_period_count(cleaned)

    # name-ID is equivalent even with a short location / "im Süden" phrase
    if re.search(
        r"\bN\.?\s*(?:of|pr\.)\b|\bname of\b|\bN\. pr\b|\bName (?:eines|einer|pr\.)\b",
        cleaned,
        re.I,
    ):
        if n_tok <= 22 and n_char <= 160 and not numbered:
            return "equivalent", "name_formula"

    # Explicit paryāya / iti-source synonym chains (SKD style).
    # Fire when a short body ends in "iti SOURCE" even if etym paren is present.
    if re.search(r"\biti\s+\S+", cleaned, re.I) and not numbered:
        after_paren = _ETYM_PAREN_RE.sub(" ", cleaned)
        after_paren = _POS_LEAD_RE.sub("", after_paren)
        after_paren = MULTISPACE.sub(" ", after_paren).strip(" ,;.—-")
        pre_iti = re.split(r"\biti\b", after_paren, maxsplit=1, flags=re.I)[0]
        pre_iti = MULTISPACE.sub(" ", pre_iti).strip(" ,;.—-")
        skt_bits = [
            i.strip()
            for i in re.split(r"\s*\.\s*|\s*,\s*", pre_iti)
            if i.strip()
            and not re.match(r"^(?:puM|strI|klI|tri|pu0|na0|tri0)$", i, re.I)
        ]
        skt_bits = [i for i in skt_bits if 1 <= len(content_tokens(i)) <= 5]
        if 1 <= len(skt_bits) <= 6 and len(content_tokens(pre_iti)) <= 14:
            return "synonym", f"iti_syn_chain_n={len(skt_bits)}"

    items = [i.strip() for i in SEP_SPLIT.split(gloss_core) if i.strip()]
    # Drop pure POS crumbs and lone "pl." / "sg."
    items = [
        i
        for i in items
        if not re.match(
            r"^(?:m|f|n|mfn|adj|a|ind|pl|sg|du|E)\.?$",
            i,
            re.I,
        )
    ]
    # Drop items that are only citations / apparatus remnants
    items = [i for i in items if not re.match(r"^(?:L|E)\.?$", i, re.I)]
    items = [i for i in items if len(content_tokens(i)) >= 1]

    if len(items) >= 2:
        item_tok_counts = [len(content_tokens(i)) for i in items]
        shortish = sum(1 for c in item_tok_counts if 1 <= c <= 6)
        # Reject if first item is a long phrase and rest is citation-like
        contentish = [
            i
            for i in items
            if not re.match(
                r"^(?:L|pl|sg|E\.?|ebend)\.?$|"
                r"^[A-ZĀ-Ū][A-Za-z.]*\s*[\d.,]*$",
                i,
                re.I,
            )
        ]
        if (
            not numbered
            and not has_emdash_senses
            and len(contentish) >= 2
            and shortish >= 2
            and shortish >= 0.55 * len(items)
            and n_tok <= 22
            and not any(CLAUSE_RE.search(i) for i in contentish)
            and not any(
                re.search(
                    r"\b(?:relating to|destined for|wishing|gesponnen|gewebt|"
                    r"a class of|every day|day and night|Mit \*)\b",
                    i,
                    re.I,
                )
                for i in contentish
            )
        ):
            # Single English NP + trailing junk often still splits to 2+;
            # require ≥2 items with ≥1 content token that look like glosses
            # of roughly similar length (synonym chain), not gloss+parenthetical.
            return "synonym", f"syn_list_n={len(contentish)}"

    # Prefix-sense microstructure (PW Mit * pra … — Mit * saM …)
    if re.search(r"\bMit\s+\*", cleaned) or (
        has_emdash_senses and n_tok >= 10
    ):
        return "encyclopedic", "prefix_or_multisense"

    # WIL-style "E. etymology" apparatus — classify on the gloss before E.
    if re.search(r"\bE\.\s", cleaned):
        pre_e = re.split(r"\bE\.\s", cleaned, maxsplit=1)[0].strip(" ,;.—-")
        pre_e = _POS_LEAD_RE.sub("", pre_e)
        pre_e = _ETYM_PAREN_RE.sub(" ", pre_e)
        pre_e = MULTISPACE.sub(" ", pre_e).strip(" ,;.—-")
        pe_items = [i.strip() for i in SEP_SPLIT.split(pre_e) if i.strip()]
        pe_items = [
            i
            for i in pe_items
            if not re.match(r"^(?:m|f|n|mfn|adj|a|ind)\.?$", i, re.I)
            and len(content_tokens(i)) >= 1
        ]
        if len(pe_items) >= 2 and all(len(content_tokens(i)) <= 6 for i in pe_items[:4]):
            return "synonym", f"wil_e_syn_n={len(pe_items)}"
        if 1 <= len(content_tokens(pre_e)) <= 14:
            return "equivalent", "wil_e_gloss"

    # Flat short / medium translational equivalent
    if (
        n_tok <= 14
        and n_char <= 120
        and not CLAUSE_RE.search(cleaned)
        and not numbered
        and n_sent <= 1
    ):
        return "equivalent", f"short_tok={n_tok}"

    if (
        n_tok <= 18
        and n_char <= 140
        and not CLAUSE_RE.search(cleaned)
        and not numbered
        and n_sent <= 1
        and not re.search(r"\b(?:Gegensatz|von\s+\w+\])", cleaned)
    ):
        return "equivalent", f"medium_flat_tok={n_tok}"

    if (
        numbered
        or has_emdash_senses
        or CLAUSE_RE.search(cleaned)
        or n_tok >= 16
        or n_char >= 140
        or n_sent >= 2
    ):
        return "encyclopedic", f"desc_tok={n_tok}_char={n_char}"

    return "residual", f"fallback_tok={n_tok}"


CLASSES = ("synonym", "equivalent", "encyclopedic", "residual")


def classify_dict(path: Path, dict_code: str, sample_per_class: int, rng: random.Random):
    """Return (counts, samples_by_class, n_records, full_rows_optional)."""
    counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    reservoirs: dict[str, list] = {c: [] for c in CLASSES}
    n = 0

    for lid, k1, body in extract_records(path):
        n += 1
        raw_def = body_after_pipe(body)
        plain = strip_markup(raw_def)
        label, reason = classify(plain)
        counts[label] += 1
        reason_counts[f"{label}:{reason.split('=')[0]}"] += 1

        # reservoir sample
        bucket = reservoirs[label]
        if len(bucket) < sample_per_class:
            bucket.append((dict_code, lid, k1, label, reason, plain[:240]))
        else:
            # reservoir sampling
            j = rng.randint(0, counts[label] - 1)
            if j < sample_per_class:
                bucket[j] = (dict_code, lid, k1, label, reason, plain[:240])

    return counts, reservoirs, n, reason_counts


def write_distribution(path: Path, rows: list[dict]):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "dict\tentries\tsynonym\tequivalent\tencyclopedic\tresidual\t"
            "synonym_pct\tequivalent_pct\tencyclopedic_pct\tresidual_pct\n"
        )
        for r in rows:
            e = r["entries"] or 1
            fh.write(
                f"{r['dict']}\t{r['entries']}\t"
                f"{r['synonym']}\t{r['equivalent']}\t{r['encyclopedic']}\t{r['residual']}\t"
                f"{100.0 * r['synonym'] / e:.2f}\t"
                f"{100.0 * r['equivalent'] / e:.2f}\t"
                f"{100.0 * r['encyclopedic'] / e:.2f}\t"
                f"{100.0 * r['residual'] / e:.2f}\n"
            )


def write_sample(path: Path, samples: list[tuple]):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "dict\tl_id\tk1\tpredicted\treason\tplain_excerpt\t"
            "gold\tnotes\n"
        )
        for row in samples:
            # escape tabs/newlines in excerpt
            excerpt = row[5].replace("\t", " ").replace("\n", " ").replace("\r", "")
            fh.write(
                f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\t{excerpt}\t\t\n"
            )


def verify_sample(path: Path) -> None:
    """Score a gold-filled sample TSV (gold column filled)."""
    total = 0
    correct = 0
    by_pred: Counter[str] = Counter()
    by_gold: Counter[str] = Counter()
    conf: Counter[tuple[str, str]] = Counter()
    missing = 0
    with open(path, "r", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        # expected columns
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7:
                continue
            pred = parts[3].strip()
            gold = parts[6].strip().lower()
            if not gold:
                missing += 1
                continue
            if gold not in CLASSES:
                print(f"WARN unknown gold label: {gold!r}", file=sys.stderr)
                continue
            total += 1
            by_pred[pred] += 1
            by_gold[gold] += 1
            conf[(pred, gold)] += 1
            if pred == gold:
                correct += 1
    print(f"gold-filled rows: {total} (unfilled: {missing})")
    if total == 0:
        print("No gold labels found — fill the 'gold' column and re-run --verify.")
        return
    print(f"accuracy: {correct}/{total} = {100.0 * correct / total:.1f}%")
    print("confusion (pred → gold):")
    for (p, g), c in sorted(conf.items()):
        mark = "OK" if p == g else "xx"
        print(f"  [{mark}] {p:12s} → {g:12s}  {c}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--csl-orig",
        default=str(Path(__file__).resolve().parents[2] / "csl-orig" / "v02"),
        help="path to local csl-orig/v02",
    )
    ap.add_argument(
        "--dicts",
        default=",".join(DEFAULT_DICTS),
        help="comma-separated dict codes (csl-orig dir names)",
    )
    ap.add_argument(
        "--out-dir",
        default=str(Path(__file__).resolve().parent),
        help="output directory",
    )
    ap.add_argument(
        "--sample-per-class",
        type=int,
        default=8,
        help="reservoir sample size per class per dict",
    )
    ap.add_argument(
        "--seed",
        type=int,
        default=1483,
        help="RNG seed for stratified sample",
    )
    ap.add_argument(
        "--verify",
        default="",
        help="path to gold-filled sample TSV; print precision and exit",
    )
    args = ap.parse_args()

    if args.verify:
        verify_sample(Path(args.verify))
        return

    root = Path(args.csl_orig)
    if not root.is_dir():
        sys.exit(f"csl-orig/v02 not found at {root}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)

    dist_rows = []
    all_samples: list[tuple] = []
    reason_global: Counter[str] = Counter()

    for code in [c.strip() for c in args.dicts.split(",") if c.strip()]:
        path = root / code / f"{code}.txt"
        if not path.is_file():
            print(f"SKIP {code}: missing {path}", file=sys.stderr)
            continue
        counts, reservoirs, n, reasons = classify_dict(
            path, code, args.sample_per_class, rng
        )
        reason_global.update(reasons)
        row = {
            "dict": code,
            "entries": n,
            "synonym": counts["synonym"],
            "equivalent": counts["equivalent"],
            "encyclopedic": counts["encyclopedic"],
            "residual": counts["residual"],
        }
        dist_rows.append(row)
        e = n or 1
        print(
            f"{code}: n={n}  "
            f"syn={100*counts['synonym']/e:.1f}%  "
            f"eqv={100*counts['equivalent']/e:.1f}%  "
            f"enc={100*counts['encyclopedic']/e:.1f}%  "
            f"res={100*counts['residual']/e:.1f}%"
        )
        for c in CLASSES:
            all_samples.extend(reservoirs[c])

    # stable sample order: dict, class, k1
    all_samples.sort(key=lambda r: (r[0], CLASSES.index(r[3]) if r[3] in CLASSES else 9, r[2]))

    dist_path = out_dir / "definition_typology_per_dict.tsv"
    sample_path = out_dir / "definition_typology_sample.tsv"
    write_distribution(dist_path, dist_rows)
    write_sample(sample_path, all_samples)

    # fingerprint of inputs for the report
    fp_parts = []
    for code in [c.strip() for c in args.dicts.split(",") if c.strip()]:
        p = root / code / f"{code}.txt"
        if p.is_file():
            h = hashlib.sha1()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            fp_parts.append(f"{code}:{h.hexdigest()[:12]}")

    meta_path = out_dir / "definition_typology_run_meta.tsv"
    with open(meta_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("key\tvalue\n")
        fh.write(f"seed\t{args.seed}\n")
        fh.write(f"dicts\t{args.dicts}\n")
        fh.write(f"csl_orig\t{root}\n")
        fh.write(f"n_dicts_ok\t{len(dist_rows)}\n")
        fh.write(f"sample_rows\t{len(all_samples)}\n")
        fh.write(f"input_sha1_12\t{';'.join(fp_parts)}\n")

    print(f"wrote {dist_path}")
    print(f"wrote {sample_path} ({len(all_samples)} rows)")
    print(f"wrote {meta_path}")
    print("top reasons:")
    for k, v in reason_global.most_common(12):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
