"""Flatten the ACC <HI1> work layer into work records (H6993 / H6989 S2).

One row per (work, ACC record). Built on the committed acc.jsonl parser
(parse_acc.py) for the cleaned parent body; the <HI1> sub-line structure is
read from acc.txt because acc.jsonl strips line markup.

Deterministic: the same acc.txt + acc.jsonl produce a byte-identical TSV.

Outputs (in the script directory):
  acc_works_flat.tsv     work_key, title, title_norm, author, school,
                         attribution_basis, hi1_count, acc_record_id,
                         source_line_span
  unattributed_hi1.tsv   every <HI1> line that could not become a work row,
                         with its reason (never a silent drop)
  ACC_HI1_FLATTEN_2026-10-18.md  distribution / coverage / 164-774 delta

Usage:
  python flatten_acc_hi1.py --acc-txt acc.txt --acc-jsonl acc.jsonl
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))

# --- SLP1 -> IAST (small, stdlib-only; parse_acc.py uses sanskrit_util, which
# is not a runtime dependency of this repo's CI) -----------------------------
SLP1_MAP = [
    ("E", "ai"), ("O", "au"), ("A", "ā"), ("I", "ī"), ("U", "ū"),
    ("F", "ṝ"), ("X", "ḹ"), ("f", "ṛ"), ("x", "ḷ"),
    ("K", "kh"), ("G", "gh"), ("C", "ch"), ("J", "jh"),
    ("W", "ṭh"), ("Q", "ḍh"), ("T", "th"), ("D", "dh"), ("P", "ph"), ("B", "bh"),
    ("N", "ṅ"), ("Y", "ñ"), ("R", "ṇ"), ("S", "ś"), ("z", "ṣ"),
    ("M", "ṃ"), ("H", "ḥ"),
    ("a", "a"), ("i", "i"), ("u", "u"), ("e", "e"), ("o", "o"),
    ("k", "k"), ("g", "g"), ("c", "c"), ("j", "j"), ("w", "ṭ"), ("q", "ḍ"),
    ("t", "t"), ("d", "d"), ("n", "n"), ("p", "p"), ("b", "b"), ("m", "m"),
    ("y", "y"), ("r", "r"), ("l", "l"), ("v", "v"), ("s", "s"), ("h", "h"),
]


def slp1_to_iast(text):
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        repl = None
        for k, v in SLP1_MAP:
            if text.startswith(k, i):
                repl = v
                i += len(k)
                break
        if repl is None:
            out.append(ch)
            i += 1
        else:
            out.append(repl)
    return "".join(out)


def fold(text):
    """ASCII fold for matching: diacritics and vowel length dropped."""
    text = unicodedata.normalize("NFD", text or "")
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = text.replace("ṃ", "m").replace("ḥ", "h")
    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_,;:/()[]'’\".":
            out.append(" ")
    text = re.sub(r"\s+", " ", "".join(out)).strip()
    return text


SLP1_HINT_RE = re.compile(r"[fxqwz]|[A-Z]")


def looks_slp1(text):
    """True when the string carries SLP1-only markers (internal capitals or
    the SLP1-only lowercase letters), as opposed to IAST with normal title
    capitalisation."""
    if not text:
        return False
    if re.search(r"[fxqwz]", text):
        return True
    for word in text.split():
        if re.search(r"[A-Z]", word[1:]):
            return True
    return False


def slp1_or_iast(text):
    text = (text or "").strip()
    return slp1_to_iast(text) if looks_slp1(text) else text


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", fold(text)).strip("-")
    return s or "untitled"


# --- markup (mirrors parse_acc.clean_body, sans sanskrit_util) ---------------
LBODY_RE = re.compile(r"\{\{Lbody=(\d+(?:\.\d+)?)\}\}")
DEVA_SLP1_RE = re.compile(r"\{#(.*?)#\}")
ITALIC_RE = re.compile(r"\{%(.*?)%\}")
BOLD_RE = re.compile(r"\{@(.*?)@\}")
UNREADABLE_RE = re.compile(r"\{\?\?\}")
PAGEBREAK_RE = re.compile(r"\[Page[^\]]*\]")
TAG_RE = re.compile(r"<[^>]+>")
HEADER_RE = re.compile(r"^<L>(?P<L>[\d.]+)<pc>(?P<pc>[^<]+)<k1>(?P<k1>[^<]+)<k2>(?P<k2>.*)$")


def clean_markup(raw):
    text = LBODY_RE.sub("", raw)
    text = DEVA_SLP1_RE.sub(lambda m: slp1_to_iast(m.group(1)), text)
    text = ITALIC_RE.sub(lambda m: m.group(1), text)
    text = BOLD_RE.sub(lambda m: m.group(1), text)
    text = UNREADABLE_RE.sub("[?]", text)
    text = PAGEBREAK_RE.sub("", text)
    text = TAG_RE.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lstrip("¦").strip()


SCHOOL_TERMS = [
    "vedanta", "vedānta", "nyaya", "nyāya", "mimamsa", "mīmāṃsā", "dharma",
    "dharmaśāstra", "jyotisha", "jyotiṣa", "vyakarana", "vyākaraṇa", "tantra",
    "shaiva", "śaiva", "vaishnava", "vaiṣṇava", "jaina", "bauddha", "buddhist",
    "samkhya", "sāṃkhya", "yoga", "kavya", "kāvya", "nataka", "nāṭaka",
    "alamkara", "alaṃkāra", "chandas", "shiksha", "śikṣā", "kalpa", "shrauta",
    "śrauta", "grihya", "gṛhya", "smriti", "smṛti", "purana", "purāṇa",
    "itihasa", "itihāsa", "ayurveda", "āyurveda", "shilpa", "śilpa", "artha",
    "arthashastra", "arthaśāstra", "kama", "kāma", "grammar", "poetics",
    "drama", "astronomy", "astrology", "medicine", "philosophy", "ritual",
]
SCHOOL_OUT = {
    "vedanta": "vedānta", "vedānta": "vedānta", "nyaya": "nyāya", "nyāya": "nyāya",
    "mimamsa": "mīmāṃsā", "mīmāṃsā": "mīmāṃsā", "dharma": "dharma",
    "dharmaśāstra": "dharma", "jyotisha": "jyotiṣa", "jyotiṣa": "jyotiṣa",
    "vyakarana": "vyākaraṇa", "vyākaraṇa": "vyākaraṇa", "tantra": "tantra",
    "shaiva": "śaiva", "śaiva": "śaiva", "vaishnava": "vaiṣṇava",
    "vaiṣṇava": "vaiṣṇava", "jaina": "jaina", "bauddha": "bauddha",
    "buddhist": "bauddha", "samkhya": "sāṃkhya", "sāṃkhya": "sāṃkhya",
    "yoga": "yoga", "kavya": "kāvya", "kāvya": "kāvya", "nataka": "nāṭaka",
    "nāṭaka": "nāṭaka", "alamkara": "alaṃkāra", "alaṃkāra": "alaṃkāra",
    "chandas": "chandas", "shiksha": "śikṣā", "śikṣā": "śikṣā", "kalpa": "kalpa",
    "shrauta": "śrauta", "śrauta": "śrauta", "grihya": "gṛhya", "gṛhya": "gṛhya",
    "smriti": "smṛti", "smṛti": "smṛti", "purana": "purāṇa", "purāṇa": "purāṇa",
    "itihasa": "itihāsa", "itihāsa": "itihāsa", "ayurveda": "āyurveda",
    "āyurveda": "āyurveda", "shilpa": "śilpa", "śilpa": "śilpa",
    "arthashastra": "arthaśāstra", "arthaśāstra": "arthaśāstra",
    "grammar": "vyākaraṇa", "poetics": "alaṃkāra", "drama": "nāṭaka",
    "astronomy": "jyotiṣa", "astrology": "jyotiṣa", "medicine": "āyurveda",
    "philosophy": "darśana", "ritual": "kalpa", "kama": "kāma",
    "alamk": "alaṃkāra", "alaṃk": "alaṃkāra", "jy": "jyotiṣa", "ved": "vedānta",
    "dh": "dharma", "archit": "śilpa", "gram": "vyākaraṇa", "nat": "nāṭaka",
    "kav": "kāvya",
}

PERSON_CUES = [
    "pupil of", "disciple of", "son of", "daughter of", "father of",
    "brother of", "guru of", "by ", "author", "commentator", "poet",
    "wrote", "flourished", "minister", "king", "general", "born",
]
PERSON_SUFFIXES = (
    "sarman", "śarman", "bhatta", "bhaṭṭa", "acarya", "ācārya", "suri", "sūri",
    "misra", "miśra", "dasa", "dāsa", "deva", "raja", "rāja", "varman", "gupta",
    "kavi", "pandita", "paṇḍita", "muni", "yati", "tirtha", "tīrtha", "aranya",
    "āraṇya", "puri", "purī", "sarasvati", "sarasvatī", "bharati", "bhāratī",
    "carya", "cārya", "upadhyaya", "upādhyāya", "cakravartin", "cakravarti",
)

CITATION_RE = re.compile(
    r"([A-ZĀĪŪŚṢṬḌṆ][\w.'’\-]*(?:\s+[A-ZĀĪŪŚṢṬḌṆ][\w.'’\-]*)*)\s+"
    r"(?:(?:p{1,2}|vol|no)\.\s*)?"
    r"(\d+(?:\^[ab]\d*)?(?:,\s*\d+(?:\^[ab]\d*)?)*)"
)
SUBJECT_SPLIT_RE = re.compile(r",\s*(?:a\s+)?([a-zA-Zāīūṛṃḥśṣṭḍṇṅñç]+)\.?\s*$", re.I)


def extract_title(segment, _nested=False):
    """Return (title, school) or (None, reason)."""
    raw = clean_markup(segment)
    if not raw:
        return None
    # strip leading commentary marker / numbering / bracket
    text = raw
    text = re.sub(r"^\s*(?:--+|[-–—])\s*", "", text)
    text = re.sub(r"^\s*\[?\s*\d+[.)]\s*", "", text)
    text = re.sub(r"^\s*\[", "", text).strip()
    if not text:
        return None
    # "C. <Title>" is a commentary work with its own title; "C. by/on ..." is
    # a commentary note on the preceding work (attached by the caller)
    if re.match(r"^CC\.", text):
        return None
    cm = re.match(r"^(?:a\s+)?C\.\s+(.*)$", text, re.I)
    if cm:
        rest = cm.group(1).strip()
        if not re.match(r"^(?:by|on|of|to|see|cf\.|comm\.|quot(?:ed|e))\b", rest, re.I) and \
           not CITATION_RE.match(rest) and not re.match(r"^[A-Za-z]+\.\s*[IVX\d]", rest) and \
           not re.match(r"^[A-Z][A-Za-z.'’\-]*(?:\s+[IVX]+)?\s*$", rest) and \
           not re.match(r"^[A-Z][\w.'’\-]*\s+(?:[IVX]+\b|\d)", rest):
            inner = extract_title(rest, _nested=True)
            if inner:
                return "C. " + inner[0], inner[1]
        return None
    if re.match(r"^(?:a\s+)?commentary\b", text, re.I) or \
       re.match(r"^(?:by|to|of|on|see|cf\.|comm\.|quot(?:ed|e))\b", text, re.I):
        return None
    if re.match(r"^[a-zçñ]", text):
        return None
    # title is up to the first sentence break whose remainder looks like a
    # citation; otherwise up to the first bare citation token
    title = None
    for m in re.finditer(r"\.\s+", text):
        head = text[:m.start()].strip()
        tail = text[m.end():].strip()
        if len(head) < 2:
            continue
        if re.match(r"^(?:See|Ed|Cf|Quoted|C\.|Comm|by\b|a\.|an\.|and\b|or\b)", tail, re.I) or \
           re.search(r"\d", tail) or CITATION_RE.match(tail):
            title = head
            break
    if title is None:
        m = CITATION_RE.search(text)
        if m and m.start() > 0:
            title = text[:m.start()].strip()
        else:
            # citation-shaped tail with no sentence break:
            # "Title S iglum 201^a" -> "Title"
            title = re.sub(
                r"\s+[A-ZĀĪŪŚṢṬḌṆ][\w.'’\-]*\s+\d+(?:\^[ab]\d*)?(?:,\s*\d+(?:\^[ab]\d*)?)*\.?$",
                "", text).strip() or text.strip()
    # cut alternate names / commentary mentions / citation tails
    title = re.split(r"\s+or\s+", title, maxsplit=1)[0].strip()
    title = re.split(r"\s+(?:and\s+)?its\s+C\.", title, maxsplit=1)[0].strip()
    title = re.split(r",\s*(?:[IVX]+\.?\s*)?\d", title, maxsplit=1)[0].strip()
    title = re.sub(r",\s*(?:Oudh|Ben|IO|B|K|L|Kh|NW|Oppert|Rice|Taylor|Burnell|Peters|Stein|Weber|MD|TD|IM|BORI|RASB)\b.*$", "", title, flags=re.I).strip()
    # split a trailing subject term
    school = ""
    sm = SUBJECT_SPLIT_RE.search(title)
    if sm and sm.group(1).lower() in SCHOOL_OUT:
        school = SCHOOL_OUT[sm.group(1).lower()]
        title = title[:sm.start()].strip()
    title = title.strip(" .,;:—-–")
    if len(fold(title)) < 2:
        return None
    return title, school


def detect_school(text):
    low = " " + (text or "").lower() + " "
    for term in sorted(SCHOOL_TERMS, key=len, reverse=True):
        if term in low:
            return SCHOOL_OUT.get(term, term)
    return ""


def person_author(record):
    """(author, basis) from the parent (pre-HI1) body."""
    body = record["parent_body"]
    low = body.lower()
    k2 = clean_markup(record["k2"]).strip()
    author = slp1_or_iast(k2) or slp1_to_iast(record["k1"]).strip()
    author = re.sub(r"\s+", " ", author).strip(" ,;.")
    if not body:
        # no prose: the headword is the filing authority; structural inference
        if any(fold(author).endswith(fold(s)) for s in PERSON_SUFFIXES):
            return author, "inferred"
        return author, "inferred" if record["hi_count"] else ""
    for cue in PERSON_CUES:
        if cue in low:
            return author, "printed"
    if any(fold(author).endswith(fold(s)) for s in PERSON_SUFFIXES):
        return author, "inferred"
    return "", ""


def parse_acc_txt(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    records = []
    cur = None
    for lineno, line in enumerate(lines, 1):
        if line.startswith("<L>"):
            m = HEADER_RE.match(line)
            cur = {
                "L": m.group("L") if m else None,
                "pc": m.group("pc") if m else "",
                "k1": m.group("k1") if m else "",
                "k2": m.group("k2") if m else "",
                "parent_lines": [],
                "segments": [],
                "lineno": lineno,
            }
            records.append(cur)
        elif line.startswith("<LEND>"):
            cur = None
        elif cur is not None:
            if line.startswith("<HI1>"):
                cur["segments"].append({"start": lineno, "end": lineno,
                                        "parts": [line[5:]]})
            elif cur["segments"]:
                cur["segments"][-1]["parts"].append(line)
                cur["segments"][-1]["end"] = lineno
            else:
                cur["parent_lines"].append(line)
    for rec in records:
        rec["parent_body"] = clean_markup(" ".join(rec["parent_lines"]))
        rec["hi_count"] = len(rec["segments"])
    return records


def load_acc_jsonl(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            out[r["acc_L"]] = r
    return out


def make_work_key(title_norm, author):
    key = "accw-" + slug(title_norm)[:48] + "-" + hashlib.sha1(title_norm.encode("utf-8")).hexdigest()[:8]
    # short/generic titles are disambiguated by the filing authority so
    # "Śrautasūtra" under two schools is not silently merged
    if len(title_norm.split()) <= 2 and author:
        key += "-" + hashlib.sha1(fold(author).encode("utf-8")).hexdigest()[:6]
    return key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--acc-txt", default=os.environ.get("ACC_TXT", "acc.txt"))
    ap.add_argument("--acc-jsonl", default=os.path.join(HERE, "acc.jsonl"))
    ap.add_argument("--out-dir", default=HERE)
    args = ap.parse_args()

    records = parse_acc_txt(args.acc_txt)
    jsonl = load_acc_jsonl(args.acc_jsonl)
    rows = []
    unattributed = []
    total_hi = 0
    records_with_hi = 0
    for rec in records:
        if not rec["segments"]:
            continue
        records_with_hi += 1
        total_hi += rec["hi_count"]
        author, author_basis = person_author(rec)
        works = defaultdict(list)
        current = None
        parent_title = slp1_or_iast(clean_markup(rec["k2"]).strip()) or \
            slp1_to_iast(rec["k1"]).strip()
        parent_title = re.sub(r"\s+", " ", parent_title).strip(" ,;.")
        for ordinal, seg in enumerate(rec["segments"], 1):
            raw = clean_markup(" ".join(seg["parts"]))
            got = extract_title(" ".join(seg["parts"]))
            if not got:
                # commentary note / continuation: attach to the preceding work
                # in the same filing; if there is none, the filing headword is
                # the base work (an ACC record is itself a work or an author).
                if current is None:
                    tn = fold(parent_title)
                    if len(tn) >= 2:
                        current = (tn, parent_title)
                        works[current] = []
                    else:
                        unattributed.append({
                            "acc_record_id": rec["L"],
                            "hi1_ordinal": ordinal,
                            "source_line_span": f"{seg['start']}-{seg['end']}",
                            "reason": "no title and no usable filing headword",
                            "raw_excerpt": raw[:240],
                        })
                        continue
                works[current].append(seg)
                continue
            title, title_school = got
            title_norm = fold(title)
            if len(title_norm) < 2:
                if current is None:
                    continue
                works[current].append(seg)
                continue
            current = (title_norm, title)
            works[current].append(seg)
            works[current][-1]["_school"] = title_school
        for (title_norm, title), segs in works.items():
            school = next((s.get("_school") for s in segs if s.get("_school")), "")
            if not school:
                school = detect_school(title + " " + rec["parent_body"])
            basis = author_basis
            if school and basis != "printed":
                basis = "printed"
            if not basis:
                basis = ""
            rows.append({
                "work_key": make_work_key(title_norm, author),
                "title": title,
                "title_norm": title_norm,
                "author": author,
                "school": school,
                "attribution_basis": basis,
                "hi1_count": len(segs),
                "acc_record_id": rec["L"],
                "source_line_span": ";".join(f"{s['start']}-{s['end']}" for s in segs),
            })

    rows.sort(key=lambda r: (r["work_key"], r["acc_record_id"]))
    unattributed.sort(key=lambda r: (r["acc_record_id"], r["hi1_ordinal"]))

    out = args.out_dir
    cols = ["work_key", "title", "title_norm", "author", "school",
            "attribution_basis", "hi1_count", "acc_record_id", "source_line_span"]
    with open(os.path.join(out, "acc_works_flat.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    ucols = ["acc_record_id", "hi1_ordinal", "source_line_span", "reason", "raw_excerpt"]
    with open(os.path.join(out, "unattributed_hi1.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ucols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(unattributed)

    sum_hi = sum(r["hi1_count"] for r in rows)
    print(f"records with <HI1>: {records_with_hi}")
    print(f"<HI1> lines: {total_hi}")
    print(f"work rows: {len(rows)}  sum(hi1_count): {sum_hi}  unattributed: {len(unattributed)}")
    print(f"reconciliation: {sum_hi} + {len(unattributed)} = {sum_hi + len(unattributed)} (expected {total_hi})")
    print(f"distinct acc_record_id in flat: {len({r['acc_record_id'] for r in rows})}")

    # distribution + coverage for the report
    per_work = Counter(r["work_key"] for r in rows)
    dist = Counter(per_work.values())
    basis = Counter(r["attribution_basis"] or "blank" for r in rows)
    print("records-per-work:", dict(sorted(dist.items())))
    print("rows by basis:", dict(basis))
    print("rows with author:", sum(1 for r in rows if r["author"]),
          "with school:", sum(1 for r in rows if r["school"]))
    with open(os.path.join(out, "flatten_stats.json"), "w", encoding="utf-8") as f:
        json.dump({
            "records_with_hi": records_with_hi,
            "hi1_lines": total_hi,
            "work_rows": len(rows),
            "sum_hi1_count": sum_hi,
            "unattributed": len(unattributed),
            "reconciled": sum_hi + len(unattributed),
            "distinct_acc_records": len({r["acc_record_id"] for r in rows}),
            "records_per_work": dict(sorted(dist.items())),
            "basis": dict(basis),
            "rows_with_author": sum(1 for r in rows if r["author"]),
            "rows_with_school": sum(1 for r in rows if r["school"]),
            "distinct_works": len(per_work),
        }, f, ensure_ascii=False, indent=1, sort_keys=True)
    assert sum_hi + len(unattributed) == total_hi, "HI1 reconciliation failed"


if __name__ == "__main__":
    main()
