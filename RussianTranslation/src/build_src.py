#!/usr/bin/env python
"""Build the pwg_ru corpus-gate dictionary sources from SamudraManthanam.

Reads the digitized Sanskrit->Russian dictionaries that ship inside the
SamudraManthanam parallel-corpus tool (sibling repo) and writes one normalized,
SLP1-keyed JSONL per source into this directory.

These outputs are DATA and are .gitignored (some sources are modern/copyright);
this script + README are the committed, regenerable contract.

Usage:  python build_src.py [path-to-SamudraManthanam]
Output: koch.jsonl kow.jsonl kna.jsonl fri.jsonl smirnov.jsonl
        each line = {"source","slp1","iast","gloss"}
"""
import json, os, sys, re, unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

DEFAULT_SM = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'SamudraManthanam'))
SM = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SM
JSONL = os.path.join(SM, "web", "corpus_builder", "jsonl")
OUT = os.path.dirname(os.path.abspath(__file__))

# source slug in SamudraManthanam  ->  our gate code
SOURCES = [
    ("kochergina",      "koch"),     # Кочергина 1987 (modern, primary independent)
    ("kossovich",       "kow"),      # Коссович 1854 (KOW, WIL-seeded human PWG->RU reference)
    ("knauer",          "kna"),      # Кнауэр 1908 (KNA, independent)
    ("frish",           "fri"),      # Фриш 1956 (FRI, independent)
    ("slovar-smirnova", "smirnov"),  # Смирнов Симфонический словарь (independent)
]

# IAST -> SLP1 (used only when the source has no slp1 key of its own).
_DIGRAPH = [("kh","K"),("gh","G"),("ch","C"),("jh","J"),("ṭh","W"),("ḍh","Q"),
            ("th","T"),("dh","D"),("ph","P"),("bh","B")]
_SINGLE = [("ā","A"),("ī","I"),("ū","U"),("ṝ","F"),("ṛ","f"),("ḹ","X"),("ḷ","x"),
           ("ṅ","N"),("ñ","Y"),("ṭ","w"),("ḍ","q"),("ṇ","R"),
           ("ś","S"),("ṣ","z"),("ḥ","H"),("ṃ","M"),("ṁ","M")]

def iast_to_slp1(s):
    if not s:
        return ""
    s = s.strip().strip("/").strip().strip("-").strip()
    s = re.sub(r"[̀-̏॑-॔]", "", s)  # drop combining accents
    for a, b in _DIGRAPH:
        s = s.replace(a, b)
    for a, b in _SINGLE:
        s = s.replace(a, b)
    return s

# --- key hygiene ---------------------------------------------------------
# A handful of upstream SamudraManthanam records carry a join key that is not a
# Sanskrit word: a stray scan number/paren leaked into Kochergina's slp1 field
# ('(nu', '11', '5)'), Cyrillic<->Latin mojibake in some Frish rows ('ргаdA',
# 'араnI', ...), a multi-form Frish field whose uppercase 'Ī' never mapped
# ('Īdfkza/ /IdfS/...'), and a Russian see-also row in Smirnov ('РЕЧЬ ... см. ↑').
# All of these are detectable as a non-ASCII-letter initial after key
# normalization — a Sanskrit headword never starts that way. When we hit one we
# try to recover the real key from the record's first *pure-Devanagari* headword
# form (the most reliable field); if that fails the row is corrupt/non-Sanskrit
# and is dropped. This keeps legitimate entries (incl. those with the anusvara
# variant 'ṁ' or IAST diacritics mid-word) untouched — only the initial is tested.
_DEV_V = {'अ':'a','आ':'A','इ':'i','ई':'I','उ':'u','ऊ':'U','ऋ':'f','ॠ':'F',
          'ऌ':'x','ॡ':'X','ए':'e','ऐ':'E','ओ':'o','औ':'O'}
_DEV_M = {'ा':'A','ि':'i','ी':'I','ु':'u','ू':'U','ृ':'f','ॄ':'F','ॢ':'x',
          'ॣ':'X','े':'e','ै':'E','ो':'o','ौ':'O'}
_DEV_C = {'क':'k','ख':'K','ग':'g','घ':'G','ङ':'N','च':'c','छ':'C','ज':'j',
          'झ':'J','ञ':'Y','ट':'w','ठ':'W','ड':'q','ढ':'Q','ण':'R','त':'t',
          'थ':'T','द':'d','ध':'D','न':'n','प':'p','फ':'P','ब':'b','भ':'B',
          'म':'m','य':'y','र':'r','ल':'l','व':'v','श':'S','ष':'z','स':'s',
          'ह':'h','ळ':'L'}
_DEV_SIGN = {'ं':'M','ः':'H','ँ':'M','ऽ':"'"}
_DEV_VIRAMA = '्'

def dev_to_slp1(s):
    """Minimal Devanagari->SLP1 (consonant carries inherent 'a' unless a virama
    or matra follows). Used only to recover a corrupt join key."""
    out = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch in _DEV_C:
            out.append(_DEV_C[ch]); i += 1
            if i < n and s[i] == _DEV_VIRAMA:
                i += 1
            elif i < n and s[i] in _DEV_M:
                out.append(_DEV_M[s[i]]); i += 1
            elif i < n and s[i] in _DEV_SIGN and s[i] != 'ऽ':
                out.append('a' + _DEV_SIGN[s[i]]); i += 1
            else:
                out.append('a')
        elif ch in _DEV_V:
            out.append(_DEV_V[ch]); i += 1
        elif ch in _DEV_SIGN:
            out.append(_DEV_SIGN[ch]); i += 1
        elif ch in _DEV_M:
            out.append(_DEV_M[ch]); i += 1
        else:
            out.append(ch); i += 1
    return ''.join(out)

def _norm_key(s):
    """Mirror corpus_gate.form_key just enough to test the leading character."""
    if not s:
        return ''
    s = unicodedata.normalize('NFC', s.strip())
    s = re.sub(r'[̀-ͯ]', '', s)
    s = s.replace('/', '').replace('\\', '').replace('|', '').replace(' ', '')
    return s.strip('-')

def bad_initial(slp1):
    k = _norm_key(slp1)
    return (not k) or (k[0].lower() not in 'abcdefghijklmnopqrstuvwxyz')

def recover_key(text):
    """First pure-Devanagari headword form -> SLP1, else '' (corrupt/non-Sanskrit)."""
    head = (text or '').split('\t')[0].strip('/ ').strip()
    tok = next((t for t in re.split(r'[\s/]+', head) if t), '')
    if tok and all('ऀ' <= c <= 'ॿ' for c in tok):
        return dev_to_slp1(tok)
    return ''

def field(text, i):
    parts = (text or "").split("\t")
    return parts[i].strip().strip("/").strip() if len(parts) > i else ""

def gloss_after(text, n):
    parts = (text or "").split("\t")
    return " ".join(p.strip() for p in parts[n:]).strip()

def extract(slug, code):
    path = os.path.join(JSONL, slug + ".jsonl")
    out_path = os.path.join(OUT, code + ".jsonl")
    n_in = n_out = n_nokey = n_fixed = n_dropped = 0
    with open(path, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8", newline="") as o:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get("deleted"):
                continue
            n_in += 1
            slp1 = (e.get("slp1") or "").strip()
            iast = ((e.get("forms") or {}).get("iast") or "").strip()
            text = e.get("text") or ""
            if code in ("fri", "smirnov"):
                # tab-structured: dev / iast / (hk) / cyrillic / gloss...
                iast = iast or field(text, 1)
                gloss = gloss_after(text, 4) or gloss_after(text, 1)
            else:
                gloss = text
            if not slp1 and iast:
                slp1 = iast_to_slp1(iast)
            if not slp1:
                n_nokey += 1
                continue
            # Drop/repair join keys whose normalized initial is not a Sanskrit
            # letter (scan-number/paren leak, Cyrillic mojibake, Russian see-also).
            if bad_initial(slp1):
                rec = recover_key(text)
                if rec and not bad_initial(rec):
                    slp1, n_fixed = rec, n_fixed + 1
                else:
                    n_dropped += 1
                    continue
            o.write(json.dumps({"source": code, "slp1": slp1, "iast": iast,
                                "gloss": gloss}, ensure_ascii=False) + "\n")
            n_out += 1
    print(f"{code:8s} <- {slug:18s} in={n_in:6d} out={n_out:6d} "
          f"no-key={n_nokey} key-fixed={n_fixed} key-dropped={n_dropped}")
    return n_out

if __name__ == "__main__":
    if not os.path.isdir(JSONL):
        sys.exit(f"SamudraManthanam jsonl dir not found: {JSONL}")
    total = sum(extract(slug, code) for slug, code in SOURCES)
    print(f"TOTAL keyed entries: {total}")
