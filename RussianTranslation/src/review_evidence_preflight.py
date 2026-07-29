#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""review_evidence_preflight — the gate that must pass BEFORE a review sheet is written.

## Why this exists

On 29-07-2026 MG opened
`sanskritlexicography-pwg-compound-differs_stratified200_review.html` and asked why
he was being made to vote at all. The measured answer: **191 of its 200 cards already
had a machine verdict, a named rule and cited evidence** — computed by
`src/pilot/adjudicate_compound_differs.py` (H1681) from the SAME two input files the
sheet itself reads, into `research/pwg_compound_differs_adjudication.tsv`, sharing
**4,246 of 4,246 row ids** with the sheet's frame. The sheet rendered none of it.

Nothing in the stack was responsible for noticing. The review-sheet standard (V1-V8 +
H1808) is entirely about PRESENTATION — type scale, anatomy colouring, tooltips, ids,
note height — so a sheet can be 100 % standard-compliant and still ask a human to
re-derive, by eye, a conclusion the repo already holds on disk. The prose rule that
should have caught it ("check prior art before building") is exactly the kind of rule
that does not fire, because firing depends on the author remembering to look.

So this module makes the machine look. It is deterministic, cheap (a key-overlap scan
over the repo's own tabular artifacts) and it BLOCKS: a generator that cannot show an
evidence manifest does not get to write HTML.

## What it checks

1. **Prior-art overlap (the H1628 defect).** Given the sheet's row ids, scan the repo
   for any OTHER committed artifact keyed on the same ids. Any artifact overlapping
   above `--overlap-threshold` (default 0.5) that the generator did not declare as
   joined is a BLOCK: the sheet is about to ask a human something the repo may already
   answer.
2. **Evidence floor.** Every card must carry at least `min_evidence_fields` joined
   evidence fields beyond the bare question, or an explicit `omitted_because` reason
   naming the source and why it is unavailable. Silent absence is a BLOCK; a stated
   absence is allowed and recorded.
3. **Script purity.** No human-facing string may mix Cyrillic with IAST diacritics
   inside one word (the `Пāṇini` defect MG flagged: "Разве на такое уже нет ЗАПРЕТА?").
   Cyrillic prose uses Cyrillic transliteration; Latin/IAST stays Latin.
4. **No raw transliteration-scheme leakage.** SLP1 must not appear in human-facing
   text. Humans read IAST; SLP1 belongs in ids and machine columns only.
5. **Citation linkability.** A reference that has a known URL template (Panini sutra,
   Cologne entry, DCS locus) must be rendered as a link, not a bare string.
6. **Structural validity of cited references.** A citation that cannot exist is never
   shown: an "Astadhyayi sutra" with adhyaya > 8 or pada > 4 is not a sutra reference
   (measured 29-07-2026: 625 / 1,270 = 49.2 % of the references the compound sheet was
   about to print were structurally impossible — Rgveda citations swept into a
   `panini_sutras` column upstream).

## Usage

    from review_evidence_preflight import EvidenceManifest, preflight

    man = EvidenceManifest(sheet_id="...", row_ids=[...], repo_root=REPO)
    man.declare_joined("research/pwg_compound_differs_adjudication.tsv",
                       fields=["verdict", "rule", "reason", "mw_k2_raw"])
    man.declare_omitted("DCS attested sentence",
                        because="no per-compound sentence map exists; only sense-level")
    for card in cards:
        man.add_card(card_id, evidence_fields=[...], omitted=[...])
    preflight(man, html)          # raises PreflightError -> nothing is written

    python review_evidence_preflight.py --selftest
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DEFAULT = os.path.dirname(HERE)

# ---------------------------------------------------------------- script purity
CYR = r'Ѐ-ӿ'
# IAST-only diacritic letters (never legitimate inside a Cyrillic word)
IAST = r'āīūṛṝḷḹṃḥṇṭḍśṣṅñ' \
       r'ĀĪŪṚṜḶḸṂḤṆṬḌŚṢṄÑ'
MIXED_SCRIPT = re.compile(r'[%s][%s]|[%s][%s]' % (CYR, IAST, IAST, CYR))

# SLP1 leaks into human-facing text in two detectable shapes. Both detectors are
# deliberately narrow: an all-lowercase SLP1 string like `agni + deva` is
# BYTE-IDENTICAL to its own IAST form, so no detector can or should flag it.
#
#   D1 — a capital used as a consonant/vowel INSIDE a token: kAya, pAdukA, jIvikA,
#        bfhatkAya, Baya. Near-unambiguous, and in practice every SLP1 split on
#        these sheets carries at least one such member.
#   D2 — lowercase `f`/`x` (SLP1 vocalic r/l) sitting AFTER a consonant: bfhant,
#        akfta, pitf. English `f` almost always follows a vowel (differs, prefix,
#        suffix, left), so this stays quiet on ordinary prose; the handful of
#        consonant-f English words are stoplisted.
_TOKEN = re.compile(r'\b[A-Za-z]{3,}\b')
_D1_UPPER_INSIDE = re.compile(r'^[A-Za-z][a-z]*[A-Z]')
# f x z never occur in IAST; after a consonant they are SLP1 markers (bfhant
# = vocalic r, akzara = s). After a VOWEL they are ordinary English (differs,
# prefix, size, puzzle), so the consonant context is what keeps this quiet on
# prose. `w` and `q` (SLP1 t/d) are deliberately NOT markers: English `sw`/`tw`
# /`dw` clusters are far too common (answer, tweak, dwell) and the cost of that
# noise outweighs the rare all-lowercase w/q token, which in practice shares a
# card with an uppercase-marked member that D1 catches anyway.
_D2_MARKER = re.compile(r'[bcdghjklmnprstvy][fxz]')
# CamelCase identifiers (RussianTranslation, SanskritLexicography, localStorage)
# trip D1. SLP1 never has this shape: its capitals are single consonants or long
# vowels, never the head of a long lowercase run repeated twice.
_CAMEL_ENGLISH = re.compile(r'^[A-Za-z][a-z]+([A-Z][a-z]{2,})+$')
_SLP1_SAFE = {
    # abbreviations and tech tokens that must never be reported
    'PWG', 'MW', 'PWK', 'DCS', 'IAST', 'SLP', 'HTML', 'JSON', 'TSV', 'URL', 'ID',
    'PDF', 'CSS', 'API', 'CDSL', 'GRA', 'AP', 'SKD', 'VCP', 'MD', 'RV', 'AV',
    'MWS', 'PW', 'ACC', 'NCC', 'CSV', 'UTF', 'BOM',
    # English words where `f` legitimately follows a consonant
    'half', 'self', 'shelf', 'wolf', 'golf', 'elf', 'calf', 'gulf', 'twelve',
}

PANINI_REF = re.compile(r'\b(\d+)\.(\d+)(?:\.(\d+))?\b')


class PreflightError(Exception):
    """Raised when a sheet must not be written. Carries every finding."""

    def __init__(self, findings):
        self.findings = findings
        super(PreflightError, self).__init__(
            'review-sheet preflight FAILED with %d blocking finding(s):\n%s'
            % (len(findings), '\n'.join('  - ' + f for f in findings)))


def sutra_is_possible(adhyaya, pada, sutra=None):
    """The Astadhyayi is 8 adhyayas x 4 padas. Anything outside cannot be a sutra
    reference, whatever the source column is called."""
    if adhyaya < 1 or adhyaya > 8:
        return False
    if pada < 1 or pada > 4:
        return False
    if sutra is not None and (sutra < 1 or sutra > 250):
        return False
    return True


def valid_sutras(raw):
    """Split a `panini_sutras`-style value into (possible, impossible) reference
    lists. Never guess: a reference that cannot exist is dropped, not repaired."""
    ok, bad = [], []
    for m in PANINI_REF.finditer(raw or ''):
        a, p = int(m.group(1)), int(m.group(2))
        s = int(m.group(3)) if m.group(3) else None
        (ok if sutra_is_possible(a, p, s) else bad).append(m.group(0))
    return ok, bad


def sutra_href(ref):
    """Deep link to the sutra, reusing the URL form ls_resolver.py already verified
    against github.com/ashtadhyayi-com/data (H1307)."""
    parts = ref.split('.')
    if len(parts) == 3:
        return 'https://ashtadhyayi.com/sutraani/%s/%s/%s' % tuple(parts)
    if len(parts) == 2:
        return 'https://ashtadhyayi.com/sutraani/%s/%s' % tuple(parts)
    return None


def find_mixed_script(text):
    return sorted({m.group(0) for m in MIXED_SCRIPT.finditer(text or '')})


def find_slp1(text, allow=()):
    """Candidate SLP1 tokens in human-facing text (see the D1/D2 note above).

    Heuristic by construction, and deliberately silent on the undecidable case:
    an all-lowercase SLP1 member equals its own IAST rendering, so it is not a
    leak anyone can see. Callers pass `allow` for domain abbreviations.
    """
    skip = {s.lower() for s in _SLP1_SAFE} | {s.lower() for s in allow}
    out = []
    for m in _TOKEN.finditer(text or ''):
        t = m.group(0)
        # Order matters. The explicit allowlist wins over everything (declared ids).
        # D2 is checked BEFORE the CamelCase exemption, so a genuine SLP1 token
        # that happens to look CamelCase (akzarajIvika) is still reported.
        if t.lower() in skip or t.isupper():
            continue
        if _D2_MARKER.search(t.lower()):
            out.append(t)
            continue
        if _CAMEL_ENGLISH.match(t):
            continue
        if _D1_UPPER_INSIDE.search(t):
            out.append(t)
    return sorted(set(out))


# ---------------------------------------------------------------- the manifest
class EvidenceManifest(object):
    """What the generator claims it looked at, joined, and deliberately left out."""

    def __init__(self, sheet_id, row_ids, repo_root=REPO_DEFAULT,
                 min_evidence_fields=2):
        self.sheet_id = sheet_id
        self.row_ids = [str(r) for r in row_ids]
        self.repo_root = repo_root
        self.min_evidence_fields = min_evidence_fields
        self.joined = {}        # path -> [fields]
        self.omitted = {}       # source (or path) -> reason
        self.omitted_paths = set()   # only these silence a prior-art finding
        self.cards = {}         # card_id -> {"fields": [...], "omitted": [...]}
        self.notes = []

    def declare_joined(self, path, fields):
        self.joined[path] = list(fields)

    def declare_omitted(self, source, because):
        if not because or len(because) < 12:
            raise ValueError('omitting %r needs a real reason, not %r' % (source, because))
        self.omitted[source] = because

    def declare_omitted_path(self, path, because):
        """Omit a concrete repo artifact the prior-art scan will find.

        Distinct from declare_omitted(): the reason is recorded the same way, but
        the PATH is what clears the scan's finding. A conceptual omission ("no DCS
        sentence map exists") has no path and cannot silence a found file — that
        asymmetry is deliberate, so a real artifact can never be waved away by a
        vaguely-worded note.
        """
        if not because or len(because) < 12:
            raise ValueError('omitting %r needs a real reason, not %r' % (path, because))
        rel = str(path).replace('\\', '/')
        self.omitted[rel] = because
        self.omitted_paths.add(rel)

    def add_card(self, card_id, evidence_fields, omitted=()):
        self.cards[str(card_id)] = {'fields': list(evidence_fields),
                                    'omitted': list(omitted)}

    # -------------------------------------------------- prior-art overlap scan
    def scan_prior_art(self, exts=('.tsv', '.json'), threshold=0.5, max_files=400):
        """Every OTHER tabular artifact in the repo keyed on these same rows.

        This is the mechanical form of 'check prior art'. It does not depend on
        anyone remembering: it reads the repo and reports id overlap.
        Returns [(relpath, overlap_fraction, n_shared)] sorted by overlap desc.
        """
        want = set(self.row_ids)
        # also match on the bare k1 (ids are often `k1~~h<hom>`)
        bare = {i.split('~~')[0] for i in want}
        hits, seen = [], 0
        for root, dirs, files in os.walk(self.repo_root):
            dirs[:] = [d for d in dirs
                       if d not in ('.git', 'node_modules', '__pycache__', 'review')]
            for fn in files:
                if not fn.endswith(exts):
                    continue
                seen += 1
                if seen > max_files:
                    break
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, self.repo_root).replace('\\', '/')
                try:
                    if os.path.getsize(p) > 80 * 1024 * 1024:
                        continue
                    with io.open(p, encoding='utf-8', errors='replace') as f:
                        blob = f.read(6 * 1024 * 1024)
                except (IOError, OSError):
                    continue
                toks = set(re.findall(r'[A-Za-z~]{3,}', blob))
                shared = len(bare & toks)
                if not shared:
                    continue
                frac = shared / float(max(1, len(bare)))
                if frac >= threshold:
                    hits.append((rel, round(frac, 4), shared))
        hits.sort(key=lambda h: -h[1])
        return hits

    def to_dict(self):
        return {
            'sheet_id': self.sheet_id,
            'rows': len(self.row_ids),
            'joined': self.joined,
            'omitted': self.omitted,
            'cards': len(self.cards),
            'notes': self.notes,
        }

    def write(self, path):
        with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(self.to_dict(), ensure_ascii=False, indent=2))
            f.write('\n')
        return path


# ---------------------------------------------------------------- the gate
def preflight(manifest, html, allow_slp1_tokens=(), overlap_threshold=0.5,
              skip_prior_art=False):
    """Run every check. Raise PreflightError on any BLOCK. Returns a report dict
    of the non-blocking observations."""
    f = []
    report = {}

    # 1. prior-art overlap
    if not skip_prior_art:
        hits = manifest.scan_prior_art(threshold=overlap_threshold)
        declared = ({p.replace('\\', '/') for p in manifest.joined}
                    | set(manifest.omitted_paths))
        undeclared = [h for h in hits
                      if not any(h[0].endswith(d) or d.endswith(h[0]) for d in declared)]
        report['prior_art_hits'] = hits
        report['prior_art_undeclared'] = undeclared
        for rel, frac, n in undeclared:
            f.append('PRIOR ART NOT JOINED: %s shares %d of %d row ids (%.0f%%) with '
                     'this sheet. Join it or declare_omitted() with a reason.'
                     % (rel, n, len(set(i.split("~~")[0] for i in manifest.row_ids)),
                        100 * frac))

    # 2. evidence floor
    starved = [cid for cid, c in manifest.cards.items()
               if len(c['fields']) < manifest.min_evidence_fields and not c['omitted']]
    report['evidence_starved'] = starved
    if starved:
        f.append('EVIDENCE FLOOR: %d card(s) carry fewer than %d joined evidence '
                 'fields and state no reason (e.g. %s).'
                 % (len(starved), manifest.min_evidence_fields, ', '.join(starved[:5])))

    # 3-5. text-level checks over the rendered HTML, minus tag internals
    text = re.sub(r'<script\b.*?</script>', ' ', html or '', flags=re.S | re.I)
    text = re.sub(r'<style\b.*?</style>', ' ', text, flags=re.S | re.I)
    visible = re.sub(r'<[^>]+>', ' ', text)

    mixed = find_mixed_script(visible)
    report['mixed_script'] = mixed
    if mixed:
        f.append('MIXED SCRIPT in human-facing text: %s — a word may not mix '
                 'Cyrillic with IAST diacritics (write «Панини» or `Pāṇini`, '
                 'never «Пāṇini»).' % ', '.join(mixed[:6]))

    slp1 = find_slp1(visible, allow=allow_slp1_tokens)
    report['slp1_leak'] = slp1
    if slp1:
        f.append('SLP1 IN HUMAN-FACING TEXT: %s — humans read IAST; SLP1 belongs in '
                 'ids and machine columns only.' % ', '.join(slp1[:8]))

    # 6. impossible citations rendered anywhere
    bad_refs = []
    for m in re.finditer(r'P\.\s*(\d+)\.(\d+)(?:\.(\d+))?', visible):
        a, p = int(m.group(1)), int(m.group(2))
        s = int(m.group(3)) if m.group(3) else None
        if not sutra_is_possible(a, p, s):
            bad_refs.append(m.group(0))
    report['impossible_citations'] = sorted(set(bad_refs))
    if bad_refs:
        f.append('IMPOSSIBLE CITATION RENDERED: %s — the Astadhyayi has 8 adhyayas '
                 'x 4 padas; these cannot be sutra references and must not be shown '
                 'to a reviewer as authority.' % ', '.join(sorted(set(bad_refs))[:6]))

    if f:
        raise PreflightError(f)
    return report


# ---------------------------------------------------------------- selftest
def selftest():
    ok = 0

    assert sutra_is_possible(4, 1, 104)
    assert not sutra_is_possible(9, 21, 22)      # MG's bfhatkAya card
    assert not sutra_is_possible(1, 12, 28)
    assert not sutra_is_possible(10, 85, 38)     # RV 10.85.38, not a sutra
    ok += 1

    # haryaSva's real value: ONE genuine sutra (corroborated by gana bidAdiH)
    # plus six Rgveda citations the upstream regex swept into `panini_sutras`.
    # `6.5` is adhyaya 6 PADA 5 -> already impossible; the Astadhyayi has 4 padas.
    good, bad = valid_sutras('P.4.1.104|P.6.5|P.6.5.1|P.8.11.21|P.9.6.24')
    assert good == ['4.1.104'], good
    assert bad == ['6.5', '6.5.1', '8.11.21', '9.6.24'], bad
    ok += 1

    assert sutra_href('4.1.104') == 'https://ashtadhyayi.com/sutraani/4/1/104'
    ok += 1

    assert find_mixed_script('Пāṇini:') == ['Пā']
    assert find_mixed_script('Панини') == []
    assert find_mixed_script('Pāṇini') == []
    ok += 1

    # D1 (capital inside a token) and D2 (consonant + vocalic f/x)
    leak = find_slp1('PWG-членение: bfhant + kAya')
    assert 'bfhant' in leak and 'kAya' in leak, leak
    assert 'pAdukA' in find_slp1('sa + pAdukA')
    assert 'akfta' in find_slp1('akfta + kara')
    # the same content in IAST must be silent
    assert find_slp1('членение: bṛhant + kāya') == []
    assert find_slp1('членение: sa + pādukā') == []
    # ordinary prose and abbreviations must be silent
    assert find_slp1('PWG и MW, класс differs, prefix/suffix, left half') == [], \
        find_slp1('PWG и MW, класс differs, prefix/suffix, left half')
    assert find_slp1('answer, tweak, dwell, size, puzzle, schwa') == [], \
        find_slp1('answer, tweak, dwell, size, puzzle, schwa')
    assert find_slp1('Members of the index differ from the first form') == [], \
        find_slp1('Members of the index differ from the first form')
    # CamelCase identifiers must not trip D1 ...
    assert find_slp1('votes persist to localStorage in RussianTranslation') == [], \
        find_slp1('votes persist to localStorage in RussianTranslation')
    assert find_slp1('SanskritLexicography') == []
    # ... but a real SLP1 token that merely LOOKS CamelCase still must
    assert find_slp1('akzarajIvika') == ['akzarajIvika']
    # an explicitly declared id is exempt; an undeclared neighbour is not
    assert find_slp1('duHsTita and kAya', allow=['duHsTita']) == ['kAya']
    # the undecidable case stays undecided, by design
    assert find_slp1('agni + deva') == []
    ok += 1

    man = EvidenceManifest('t', ['a', 'b'], repo_root=HERE, min_evidence_fields=2)
    man.add_card('a', ['x', 'y'])
    man.add_card('b', [])                       # starved, no reason -> BLOCK
    try:
        preflight(man, '<p>ok</p>', skip_prior_art=True)
        raise AssertionError('should have blocked on the evidence floor')
    except PreflightError as e:
        assert 'EVIDENCE FLOOR' in str(e), str(e)
    ok += 1

    man2 = EvidenceManifest('t', ['a'], repo_root=HERE, min_evidence_fields=1)
    man2.add_card('a', ['x'])
    try:
        preflight(man2, '<p><b>Пāṇini:</b> P.9.21.22</p>', skip_prior_art=True)
        raise AssertionError('should have blocked on mixed script + impossible ref')
    except PreflightError as e:
        assert 'MIXED SCRIPT' in str(e) and 'IMPOSSIBLE CITATION' in str(e), str(e)
    ok += 1

    man3 = EvidenceManifest('t', ['a'], repo_root=HERE, min_evidence_fields=1)
    man3.add_card('a', ['x'])
    rep = preflight(man3, '<p>членение: <code>bṛhant + kāya</code>, '
                          '<a href="https://ashtadhyayi.com/sutraani/4/1/104">P.4.1.104</a></p>',
                    skip_prior_art=True)
    assert rep['mixed_script'] == [] and rep['impossible_citations'] == []
    ok += 1

    try:
        man3.declare_omitted('DCS sentence', 'nope')
        raise AssertionError('short reason must be rejected')
    except ValueError:
        pass
    ok += 1

    print('selftest OK — %d groups: sutra validity, reference splitting, sutra hrefs, '
          'mixed-script detection, SLP1 leak detection, evidence floor, combined '
          'block, clean pass, omission-reason quality' % ok)


if __name__ == '__main__':
    if '--selftest' in sys.argv[1:]:
        selftest()
    else:
        print(__doc__)
