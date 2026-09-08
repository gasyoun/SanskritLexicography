# -*- coding: utf-8 -*-
r"""Build the `DHĀTUP. x,y` -> Palsule concordance (H1333).

WHY THIS SHAPE. H1333's §Prerequisites asked whether MG's supplied XLS carries a
Böhtlingk coordinate per row. Inspected 07-09-2026: it does NOT. The file is
Palsule's *artha* (meaning) index — 8171 rows of `<artha> : ⎷<root> <pada>` with a
Palsule page (`P166`…) — keyed on the ROOT, never on a gaṇa,serial pair. So the
branch-2 path applies, but with a better join key than the (gaṇa, dhātu) one the
handoff sketched:

  PWG is itself Böhtlingk. A `<ls>DHĀTUP. x,y</ls>` citation stands inside the
  article OF THE ROOT it numbers, and that article's `<k1>` key IS the dhātu in
  SLP1. So the (x,y) -> root half of the crosswalk is *read off Böhtlingk's own
  text*, not guessed by a normalizing join — no ablaut normalization needed, and
  the H328 negative result (a naive it-stripped join matched 454/930) does not
  bind this half.

Only the second half — root -> Palsule row — is a join, and it is a join on the
root's citation form in two independent transliterations (SLP1 headword vs the
XLS's IAST `Корень` column), which is exactly what `_norm()` below reconciles.

AMBIGUITY FILTER (load-bearing). A coordinate is kept only when every PWG article
citing it agrees on the root. A DHĀTUP. coordinate quoted inside a *noun* article
would otherwise contribute a false root; the disagreement filter drops those
coordinates entirely rather than picking a winner. Conflicts are counted and
reported, never silently resolved.

GRANULARITY — READ THIS BEFORE TRUSTING A RECORD. A record is keyed by coordinate but
its CONTENT is the union of every XLS row whose root string normalizes to the same
spelling. Palsule's artha index is keyed on the root, not on a gaṇa,serial pair, so it
cannot distinguish the homonyms Böhtlingk numbers separately: `DHĀTUP. 26,91` is the
divādi `snih`, but its record carries the arthas of every `snih` in Palsule (divādi and
curādi alike). The record therefore answers "what does Palsule record for this root
spelling", NOT "what does Palsule record at exactly this coordinate". `artha_agreement`
below measures how often the right artha is in there; it is never a claim that the wrong
ones have been excluded.

The stored `arthas` list is COMPLETE; only the tooltip limits what it displays.

SECOND COORDINATE WITNESS — MONIER-WILLIAMS (H4339). Böhtlingk is not the only
dictionary that cites his own dhātupāṭha numbering: MW cites the same coordinates with
the gaṇa in Roman numerals (`Dhātup. xxiv, 68` = 24,68), inside the article of the root
it numbers, `<k1>` in the same SLP1. That buys two things H1333 could not have:

  1. COVERAGE. A coordinate PWG drops — because Böhtlingk spells the root two ways
     (`skand`/`skund`) or because Palsule has no row for his spelling — is filled from
     MW when MW has exactly ONE claimant article. Never when MW is itself ambiguous.
  2. CROSS-VALIDATION. Where PWG and MW each resolve a coordinate to a single root,
     they can be compared. That agreement rate (`_stats.cross_*`) is the independent
     confirmation of the coordinate→root half that H1333 shipped without.

PROVENANCE IS STAMPED, NEVER BLURRED. Every record carries `source`: `pwg` (read off
Böhtlingk's own article, H1333's rule), `mw` (PWG had no single claimant, MW did) or
`mw-respell` (PWG's root is absent from Palsule and MW spells it differently). The
tooltip says so out loud. Disagreements between the two dictionaries are LISTED
(`_mw_disagreements`), never resolved by picking a winner.

MW does not touch the artha axis: its glosses are English, so the accuracy measurement
stays PWG's own parenthesized artha, and it is reported per source so the H1333 number
(139/232) remains readable after the MW rows land.

Raw XLS stays local (gitignored `pwg_ru/eval/`); the DERIVED table is what ships.

  python src/build_dhatup_palsule.py [--xls PATH] [--pwg PATH] [--mw PATH] [--out PATH]
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
from sibling_root import sibling_root  # noqa: E402
GH = sibling_root(HERE)

DEFAULT_XLS = os.path.join(REPO, 'pwg_ru', 'eval', 'Palsule_Artha_24_01_2014.xlsx')
DEFAULT_PWG = os.path.join(GH, 'csl-orig', 'v02', 'pwg', 'pwg.txt')
DEFAULT_MW = os.path.join(GH, 'csl-orig', 'v02', 'mw', 'mw.txt')
DEFAULT_PW = os.path.join(GH, 'csl-orig', 'v02', 'pw', 'pw.txt')
DEFAULT_OUT = os.path.join(HERE, 'data', 'dhatup_palsule.json')

_L = re.compile(r'^<L>(\d+)<pc>[^<]*<k1>([^<]*)<k2>')
_DHATUP = re.compile(r'<ls\b[^>]*>\s*DH[ĀA]TUP\.\s*(\d+)\s*,\s*(\d+)')
#: A `DHĀTUP. x,y` continuation carried on the n= attribute with a bare visible
#: number (`<ls n="DHĀTUP. 26,">91</ls>`) — same citation, different splitting.
_DHATUP_N = re.compile(r'<ls\b[^>]*\bn\s*=\s*"DH[ĀA]TUP\.\s*(\d+)\s*,\s*"[^>]*>\s*(\d+)')
#: A part-of-speech tag on the head line marks a NOMINAL article. Böhtlingk gives
#: such an article the dhātupāṭha coordinate only to say "this noun glosses that
#: root" (`{#loqana#}¦ <lex>n.</lex> … als Erkl. von {#bAD#} <ls>DHĀTUP. 2,4</ls>`)
#: — the coordinate belongs to the root, not to the noun. Root articles carry no
#: <lex> on the head line (they carry the finite form, and often a √).
_HEAD_LEX = re.compile(r'<lex\b')

#: THE POSITIVE TEST, and the one the H4349 sibling pass actually turns on. PWG's own
#: pass discriminates a root article from a noun article by the ABSENCE of a `<lex>`
#: part-of-speech tag on the head line, which works because PWG tags its nouns. pw
#: abridges, and often does not: `{#DAnya#}¦ (von {#Dana#}) {%das Reichsein%} <ls>DHĀTUP.
#: 20,3</ls>` is a noun meaning "wealth" with no `<lex>` anywhere, and the negative test
#: passes it through as a root — pw's citation for a coordinate PWG gives to `jal`.
#: Böhtlingk marks a verbal article positively instead, with `√` on its head line
#: (`*√{#cukk#}¦, {#cukkayati#}`), and that marker separates all 37 head-line claimants
#: of pw's DHĀTUP. citations cleanly: every `<lex>`-tagged claimant lacks it, every
#: untagged noun lacks it, and the 15 that carry it are roots. Requiring the marker
#: rather than merely not-forbidding it is what keeps meanings out of the root column.
_HEAD_RADICAL = re.compile('√')

#: SLP1 -> IAST for the root citation form only (consonants + simple vowels).
_S2I = {
    'A': 'ā', 'I': 'ī', 'U': 'ū', 'f': 'ṛ', 'F': 'ṝ', 'x': 'ḷ', 'X': 'ḹ',
    'E': 'ai', 'O': 'au', 'M': 'ṃ', 'H': 'ḥ',
    'K': 'kh', 'G': 'gh', 'N': 'ṅ', 'C': 'ch', 'J': 'jh', 'Y': 'ñ',
    'w': 'ṭ', 'W': 'ṭh', 'q': 'ḍ', 'Q': 'ḍh', 'R': 'ṇ',
    'T': 'th', 'D': 'dh', 'P': 'ph', 'B': 'bh',
    'S': 'ś', 'z': 'ṣ',
}


def slp1_root_iast(s):
    """The root's SLP1 citation form -> IAST (accents/markup already stripped)."""
    return ''.join(_S2I.get(c, c) for c in s)


#: Palsule's printed roots carry footnote markers that the XLS captured as trailing
#: digits (`gādh39`, `arj7`, `i4`). `_norm` already strips them for MATCHING, but the
#: stored/displayed `palsule_root` kept them and rendered them into the tooltip.
_FOOTNOTE_DIGITS = re.compile(r'\d+$')

#: The XLS root column carries the punctuation of the printed line it was cut from
#: (`⎷bhu,` in the two-root row `sattāyām : ⎷bhu, ⎷vid all (ex. V).`). Left in place it
#: forms a distinct key, which is how DHĀTUP. 1,1 — bhū, the first root of the whole
#: dhātupāṭha — shipped without its canonical artha `sattāyām`.
_EDGE_PUNCT = re.compile(r'^[\s.,;:]+|[\s.,;:]+$')

#: Source typos in the XLS's root column, folded to the attested root. Kept as an
#: explicit two-item allowlist rather than a general vowel-length fold: `bhu`/`bhū` and
#: `dhu`/`dhū` are safe because no short-vowel root of that shape exists, whereas a
#: blanket fold would collide genuine pairs (`vid`/`vīd`, `kṛ`/`kṝ`). Each entry is a
#: claim about ONE cell in ONE spreadsheet and is counted in `_stats.source_typo_folds`.
_XLS_ROOT_TYPOS = {'bhu': 'bhū', 'dhu': 'dhū'}


def _clean_root(s):
    """The displayable Palsule root: ⎷ removed, edge punctuation and footnote digits
    stripped."""
    return _FOOTNOTE_DIGITS.sub('', _EDGE_PUNCT.sub('', (s or '').replace('⎷', '')))


def _norm(s):
    """Join key: NFC IAST, lowercased, stripped of the XLS's ⎷ mark, of pada
    letters, of trailing homonym digits, of whitespace and of hyphens."""
    if not s:
        return ''
    s = unicodedata.normalize('NFC', s)
    s = s.replace('⎷', '').replace('√', '')
    s = _EDGE_PUNCT.sub('', s)
    s = re.sub(r'[\s\-·]', '', s)
    s = re.sub(r'\d+$', '', s)
    s = s.lower()
    return _XLS_ROOT_TYPOS.get(s, s)


def read_palsule(xls):
    """Palsule artha index -> {norm_root: {'root_iast', 'pages', 'arthas'}}.

    Sheet `Лист1`: # | Text | page | Описание(=artha) | Корень с метками |
    Корень | Метки(pada V/H) | ... . One root owns many artha rows; we keep the
    root's page set and its artha glosses in file order."""
    import openpyxl
    wb = openpyxl.load_workbook(xls, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    by_root = {}
    rows = 0
    typo_folds = 0
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue
        if not row or len(row) < 7:
            continue
        num, _text, page, artha, _marked, root, pada = row[:7]
        if not root:
            continue
        rows += 1
        key = _norm(str(root))
        if not key:
            continue
        if key != _clean_root(str(root)).lower():
            typo_folds += 1
        rec = by_root.setdefault(key, {
            'root_iast': _clean_root(str(root)),
            'pages': [], 'arthas': [], 'pada': [], 'nums': [],
        })
        p = (str(page).strip() if page else '')
        if p and p not in rec['pages']:
            rec['pages'].append(p)
        a = (str(artha).strip() if artha else '')
        if a and a not in rec['arthas']:
            rec['arthas'].append(a)
        pd = (str(pada).strip() if pada else '')
        if pd and pd not in rec['pada']:
            rec['pada'].append(pd)
        if num is not None:
            rec['nums'].append(str(num).strip())
    wb.close()
    return by_root, rows, typo_folds


#: Böhtlingk routinely prints the dhātupāṭha's own artha in SLP1 parentheses IMMEDIATELY
#: beside the citation, on either side of it:
#:   {#sni/hyati (prItO)#} <ls>DHĀTUP. 26,91</ls>          -> prItO  (prītau)
#:   {#ti/zWati#} <ls>DHĀTUP. 22,30</ls> ({#gatinivfttO#}) -> gatinivfttO (gatinivṛttau)
#: That is an INDEPENDENT witness of what the coordinate means — it comes from PWG, the
#: Palsule glosses come from the XLS — so agreement between the two is a real accuracy
#: measurement of the crosswalk rather than a spot-check anecdote. Verified only; never
#: used to build or to filter the table.
_ARTHA_BEFORE = re.compile(r'\(([^(){}#]+)\)#\}\s*(?:<[^>]*>\s*)?$')
_ARTHA_AFTER = re.compile(r'^\s*\(\{#([^#}]+)#\}\)')


def read_pwg_coords(pwg):
    """pwg.txt -> ({coord: {root_slp1: n_headline_citations}}, n_entries_seen).

    HEAD-LINE WEIGHTING. Böhtlingk gives a root its dhātupāṭha coordinate on the
    article's OWN head line (`{#aNg#}¦, {#a/Ngati#} … <ls>DHĀTUP. 5,38</ls>`).
    The same coordinate also turns up deeper inside derivative/noun articles that
    merely quote it. We record both, but a head-line citation outranks a body one
    when a coordinate has several claimants — an empirical discriminator, not a
    guess: it is where the lexicographer states the numbering."""
    coords = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))   # [head, body, head_nominal]
    key = None
    at_head = False
    entries = 0
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            m = _L.match(line)
            if m:
                key = m.group(2)
                at_head = True
                entries += 1
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            slot = 0 if at_head else 1
            nominal = bool(at_head and _HEAD_LEX.search(line))
            for rx in (_DHATUP, _DHATUP_N):
                for mm in rx.finditer(line):
                    coord = '%s,%s' % (mm.group(1), mm.group(2))
                    coords[coord][key][slot] += 1
                    if nominal:
                        coords[coord][key][2] += 1
            at_head = False
    return coords, entries


#: MW writes Böhtlingk's gaṇa as a lowercase Roman numeral and splits the citation
#: across the `n=` attribute in the same three ways PWG does:
#:   <ls>Dhātup. xxiv, 68</ls>            -> 24,68
#:   <ls n="Dhātup.">xxxiv, 40</ls>       -> 34,40
#:   <ls n="Dhātup. xxxiii,">92.</ls>     -> 33,92
#: All three are the same citation; missing any of them silently shrinks the witness.
_MW_DHATUP = re.compile(
    r'<ls\b[^>]*>\s*Dh[āaĀA]tup\.\s*([ivxlcIVXLC]+)\s*,\s*(\d+)')
_MW_DHATUP_N_FULL = re.compile(
    r'<ls\b[^>]*\bn\s*=\s*"Dh[āaĀA]tup\."[^>]*>\s*([ivxlcIVXLC]+)\s*,\s*(\d+)')
_MW_DHATUP_N_GANA = re.compile(
    r'<ls\b[^>]*\bn\s*=\s*"Dh[āaĀA]tup\.\s*([ivxlcIVXLC]+)\s*,\s*"[^>]*>\s*(\d+)')

#: MW numbers 23,194 of its articles with a dotted id (`<L>92747.1<pc>`), which the
#: `_L` regex above — written for PWG, where the shape is rarer — does not accept. A
#: separate pattern keeps H1333's PWG numbers byte-stable while the MW pass sees the
#: whole dictionary. (PWG has 636 such articles of its own; widening `_L` would move
#: the shipped H1333 baseline, so that is left as its own change, not smuggled in here.)
_L_ANY = re.compile(r'^<L>([\d.]+)<pc>[^<]*<k1>([^<]*)<k2>')
#: Kept as the MW-facing name it was born with (H4339); H4349 gave it the neutral
#: alias above because PWG's own dotted-id articles and pw need the same widening.
_L_MW = _L_ANY

#: MW's own structured cross-reference to Westergaard's *Radices* — the edition whose
#: numbering `DHĀTUP. x,y` IS: `<info westergaard="dIDIN,24.68,02.0084"/>` = the root
#: `dIDIN` at Westergaard 24.68 (and Pāṇinian 02.0084). Several are semicolon-joined.
#: This is MW editorially numbering an article, as against merely quoting a citation in
#: running prose, and where the two channels differ the field is the one to believe.
_MW_WESTERGAARD = re.compile(r'<info\b[^>]*\bwestergaard="([^"]*)"')

#: A variant-reading note, and the reason the prose channel cannot be trusted raw
#: (H4339 adjudication, 07-09-2026). MW's `kzal` article says, in full:
#:   `<hom>1.</hom> <s>kzal</s> ¦ <ab>v.l.</ab> for √ <s>kzar</s>, <ls>Dhātup. xx, 21</ls>.`
#: That sentence ASSIGNS 20,21 to `kzar` and names `kzal` as the rejected reading — so
#: harvesting the citation as a `kzal` claim inverts MW's own statement. This is the
#: `pad`/3,1 defect exactly, and the field-first rule does not catch it here because no
#: `<info westergaard>` anywhere numbers 20,21, so the prose fallback runs unguarded.
#: `w.r.` (wrong reading) is the same construction under a different siglum.
_MW_VL = re.compile(r'<ab>\s*(?:v\.\s*l\.|w\.\s*r\.)\s*</ab>')

#: WHICH SIDE OF THE CITATION THE NOTE SITS ON DECIDES WHAT IT MEANS, and a first,
#: line-scoped version of this guard got that wrong in both directions (found by the
#: second adjudication pass, 07-09-2026). Three real articles, three different answers:
#:
#:   kzal, 20,21   `<s>kzal</s> ¦ <ab>v.l.</ab> for √ <s>kzar</s>, <ls>Dhātup. xx, 21</ls>`
#:                 note BEFORE the citation, same clause -> the headword IS the rejected
#:                 reading and the coordinate belongs to someone else. REFUSE.
#:   juq, 28,37    `<ls n="Dhātup. xxviii,">37</ls> (<ab>v.l.</ab> √ <s>jun</s>)`
#:                 note AFTER the citation -> the coordinate is the headword's and `jun`
#:                 is the variant. The exact inverse. KEEP — line-scoping destroyed this
#:                 correct row.
#:   dAs, 27,32    `(<ab>v.l.</ab> for <s>dAS</s>, <ls>Vop.</ls>; <ab>ib.</ab> <ls …>xxvii, 32</ls>)`
#:                 note before, but a `;` ends its clause first -> it governs the `Vop.`
#:                 citation, not this one. KEEP — line-scoping destroyed a cross-validation
#:                 pair that AGREED with Böhtlingk.
#:
#:   paRq, 32,130 `pile up (<ab>v.l.</ab> for <s>piRq</s>), <ls n="Dhātup.">xxxii, 130</ls>`
#:                 note before, and the `)` only closes the parenthesis the note ITSELF
#:                 sits in — it does not end the clause, which runs on to the citation.
#:                 REFUSE. (Both dictionaries agree 32,130 is `piṇḍ`'s: PWG's `paRq`
#:                 article says `v. l. für {#piRq#}` and its `piRqay` article attributes
#:                 32,130 positively. A `)` counted blindly shipped `paṇḍ` anyway.)
#:
#: So the test is clause-scoped WITH PARENTHESIS DEPTH: a note disqualifies a citation
#: when it precedes it and nothing between them ends its clause — a `;`, or a `)` that
#: closes a parenthesis opened BEFORE the note. Residual and left alone deliberately:
#: a note in a trailing parenthesis is genuinely ambiguous in MW's own usage (`juq`'s
#: names the variant, `SloR`'s 13,15 `(<ab>w.r.</ab> for <s>pER</s>)` reads the other way),
#: so those are kept and the ambiguity is declared rather than guessed.
_MW_CLAUSE_END = re.compile(r'[;)]')

_ROMAN_VALUES = {'i': 1, 'v': 5, 'x': 10, 'l': 50, 'c': 100}


def roman_to_int(s):
    """`xxiv` -> 24. None for anything that is not a Roman numeral we can read.

    Böhtlingk's dhātupāṭha runs to gaṇa 35, so `i`–`c` covers the whole range; a
    subtractive pair (`iv`, `ix`, `xl`) is handled by the look-ahead."""
    s = (s or '').lower()
    if not s:
        return None
    total = 0
    for i, c in enumerate(s):
        v = _ROMAN_VALUES.get(c)
        if v is None:
            return None
        nxt = _ROMAN_VALUES.get(s[i + 1]) if i + 1 < len(s) else 0
        total += -v if (nxt or 0) > v else v
    return total or None


def _vl_governs(line, at):
    """Does a variant-reading note disqualify the citation starting at `at`?

    True only when the LAST such note before the citation is still in the same clause.
    Depth matters: the `)` that closes the parenthesis the note itself sits in does NOT
    end the clause (that is `paRq` at 32,130, which shipped a root both dictionaries
    disown when the paren was counted blindly), whereas a `)` closing a parenthesis
    opened before the note does. See `_MW_CLAUSE_END` for the four articles that fix
    this rule."""
    pre = line[:at]
    last = None
    for m in _MW_VL.finditer(pre):
        last = m
    if last is None:
        return False
    head = pre[:last.start()]
    # How deep inside parentheses the note itself sits. Those closers belong to the
    # note's own context and are transparent; anything shallower ends the clause.
    depth = max(0, head.count('(') - head.count(')'))
    for ch in pre[last.end():]:
        if ch == '(':
            depth += 1
        elif ch == ')':
            if depth == 0:
                return False
            depth -= 1
        elif ch == ';':
            return False
    return True


def read_mw_coords(mw):
    """mw.txt -> (prose, field, field_seen, n_entries_seen, vl_dropped).

    Two INDEPENDENT channels, deliberately not merged here — the caller's policy
    decides which one speaks for a coordinate:

      `prose[coord]`  -> {headword} for every article citing `Dhātup. R, N` in running
                         text. This is the survey's channel, and it is the noisy one: a
                         quotation is not an attribution. MW's `pad` article cites
                         `Dhātup. iii, 1` only to say `padati` is a variant reading for
                         `badati`, which would hand coordinate 3,1 to the wrong root.
      `field[coord]`  -> {headword} from MW's OWN structured statement
                         `<info westergaard="ata,3.1,01.0033"/>` — an editorial claim,
                         not prose — kept only when the article's headword occurs in the
                         Westergaard root token the field names. That test is what
                         rejects `pad` at 3,1: the field there names `ata` (= PWG's
                         `at`), so `pad` is not a claimant for its own citation.
                         Westergaard's citation forms carry anubandhas on both ends
                         (`ata` = at, `ScyutiR` = cyut, `dIDIN` = dIDI), so containment
                         is the honest test — stripping them by rule is exactly the
                         H328 negative result (a naive it-stripped join matched
                         454/930) and is not attempted.
      `field_seen`    -> every coordinate the field mentions at all, whoever it names.
                         A coordinate MW itself has numbered is one where prose must
                         NOT be consulted as a fallback: MW has already spoken.
      `vl_dropped`    -> coordinates whose only prose mention sat on a `<ab>v.l.</ab>`
                         line and was therefore refused (see `_MW_VL`). Reported so the
                         suppression is a published number, not a silent filter.

    CONTAINMENT IS CASE-FOLDED, and that is worth stating because SLP1 case is not
    decoration: folding conflates ā/a, ī/i, ū/u, ṝ/ṛ, ś/s, ṅ/n and ṇ/r. It is permissive
    (it can only admit claimants a strict test would refuse, never swap one), and the
    9 fills that depend on it — 2,19 `Urd`/`urda`, 5,53, 9,67, 9,74, 14,9, 26,109,
    28,28, 31,14, 32,63 — are ones where the case-sensitive claimant set is EMPTY, so
    no row's attribution turns on the fold. `pad` still fails against `ata` either way.
    Kept because MW and Westergaard genuinely differ on vowel case in citation forms;
    documented because relying on it undocumented would be luck, not design.

    MW uses the same Cologne markup as PWG (`<L>…<k1>KEY<k2>` opens, `<LEND>` closes),
    only the citation syntax differs (Roman gaṇa)."""
    prose = defaultdict(set)
    prose_raw = defaultdict(set)
    field = defaultdict(set)
    field_seen = set()
    vl_dropped = set()
    key = None
    entries = 0
    with open(mw, encoding='utf-8') as f:
        for line in f:
            m = _L_MW.match(line)
            if m:
                key = m.group(2)
                entries += 1
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            for rx in (_MW_DHATUP, _MW_DHATUP_N_FULL, _MW_DHATUP_N_GANA):
                for mm in rx.finditer(line):
                    gana = roman_to_int(mm.group(1))
                    if gana is None:
                        continue
                    coord = '%d,%s' % (gana, mm.group(2))
                    # The unguarded channel, kept so the prose-first counterfactual is
                    # the policy that actually shipped before this guard, not a hybrid.
                    prose_raw[coord].add(key)
                    if _vl_governs(line, mm.start()):
                        # MW is naming this article as the REJECTED reading of the
                        # coordinate. Recording it as a claimant would ship the one
                        # root the source explicitly disowns.
                        vl_dropped.add(coord)
                        continue
                    prose[coord].add(key)
            for mm in _MW_WESTERGAARD.finditer(line):
                for part in mm.group(1).split(';'):
                    bits = part.split(',')
                    if len(bits) < 2 or '.' not in bits[1]:
                        continue
                    gana, serial = bits[1].split('.', 1)
                    if not (gana.isdigit() and serial.isdigit()):
                        continue
                    coord = '%d,%d' % (int(gana), int(serial))
                    field_seen.add(coord)
                    if key.lower() in (bits[0] or '').lower():
                        field[coord].add(key)
    return prose, field, field_seen, entries, vl_dropped, prose_raw


def mw_claimants(prose, field, field_seen):
    """coord -> the ONE root MW attributes it to. FIELD FIRST, prose only as fallback.

    Where MW has numbered a coordinate in its own structured field, that statement is
    what MW says and the prose channel is not consulted — including when the field
    names nobody usable, in which case the coordinate simply has no MW claimant. This
    is the reading that gets 3,1 right, and it yields MORE usable fills than a
    prose-first policy (241 against 193 when this pass was first measured), because
    removing spurious claimants also *un*-ambiguates coordinates two prose citations had
    made look contested.

    TWO DIFFERENT QUANTITIES, DO NOT CONFLATE THEM. Prose-first produces more
    single-claimant COORDINATES (`_stats.mw_coords_single_claimant_prose_first`, 1192
    against this policy's 1062) and fewer usable FILLS, because most of its extra
    claimants are on coordinates PWG already resolved — they add confident-looking
    noise to the cross-validation, not coverage. The claimant counterfactual is
    published because it is re-derivable from the artifact; the fill counterfactual is
    a measurement of an earlier build and is quoted as such.

    THE FALLBACK IS THE WEAK BRANCH, and it is measured, not assumed away. Where no
    `<info westergaard>` numbers a coordinate anywhere in MW, prose IS consulted — that
    is a genuinely different evidence class from a field claim, and it is counted apart
    (`coords_filled_from_mw_prose_only`). Prose that sits on a variant-reading line is
    refused outright (`_MW_VL`): the `pad`/3,1 defect recurs in this branch, and at
    20,21 it shipped a root MW's own sentence disowns until the H4339 adjudication pass
    caught it."""
    out = {}
    for coord in set(prose) | set(field_seen):
        claim = field.get(coord) if coord in field_seen else prose.get(coord)
        if claim and len(claim) == 1:
            out[coord] = next(iter(claim))
    return out


def audit_inline_artha(pwg, table, sources=None):
    """Measure the table against PWG's OWN parenthesized artha beside each citation.

    Returns (agree, disagree, examined, samples). A coordinate counts as agreeing when
    the SLP1 artha PWG prints next to the citation, transliterated, appears in the
    Palsule artha set the table carries for it. Disagreements are returned verbatim so
    they can be read rather than summarized.

    `sources` restricts the measurement to rows of a given provenance (H4339). The
    PWG-derived and MW-derived rows are measured apart because pooling them would
    quietly move H1333's published accuracy number."""
    agree = disagree = loose = 0
    samples = []
    for line, coord in _iter_citation_lines(pwg):
        rec = table.get(coord)
        if not rec:
            continue
        if sources is not None and rec.get('source', 'pwg') not in sources:
            continue
        for pos, m in _inline_artha(line, coord):
            got = slp1_root_iast(m).replace('/', '').replace('\\', '')
            got_n = _norm(got)
            have = [_norm(a) for a in (rec.get('arthas') or [])]
            if got_n and got_n in have:
                agree += 1
                loose += 1
            elif got_n and _loose_hit(got_n, have):
                # Same artha, different citation form: PWG prints `ched` where Palsule
                # has `chede`, `saṃcalane` for `calane`, or runs two arthas into one
                # string (`mandāyāṃ gatau, śanairgatau`). Counted separately and never
                # folded into the strict number.
                loose += 1
                disagree += 1
                if len(samples) < 25:
                    samples.append({'coord': coord, 'pwg_artha': got,
                                    'palsule_arthas': rec.get('arthas')[:6],
                                    'where': pos, 'loose_match': True})
            elif got_n:
                disagree += 1
                if len(samples) < 25:
                    samples.append({'coord': coord, 'pwg_artha': got,
                                    'palsule_arthas': rec.get('arthas')[:6],
                                    'where': pos})
            break
    return agree, disagree, agree + disagree, samples, loose


def _loose_hit(got, have):
    """True when PWG's artha and a Palsule artha are the same gloss in different citation
    form. Deliberately weak — reported as its own number, never merged into the strict
    rate — because it accepts substring containment in either direction."""
    for a in have:
        if not a:
            continue
        if got in a or a in got:
            return True
        # PWG sometimes runs several arthas into one string; split and retry.
        for piece in re.split(r'[,;]', got):
            piece = piece.strip()
            if piece and (piece in a or a in piece):
                return True
    return False


def _iter_citation_lines(pwg):
    """Yield (line, coord) for every line carrying a DHĀTUP. x,y citation."""
    with open(pwg, encoding='utf-8') as f:
        for line in f:
            for rx in (_DHATUP, _DHATUP_N):
                for mm in rx.finditer(line):
                    yield line, '%s,%s' % (mm.group(1), mm.group(2))


def _inline_artha(line, coord):
    """Yield (position, slp1_artha) for the artha PWG prints beside this citation."""
    key = re.compile(r'<ls\b[^>]*>\s*DH[\u0100A]TUP\.\s*%s\s*,\s*%s\s*</ls>'
                     % tuple(coord.split(',')))
    m = key.search(line)
    if not m:
        return
    before = _ARTHA_BEFORE.search(line[:m.start()])
    if before:
        yield 'before', before.group(1)
        return
    after = _ARTHA_AFTER.match(line[m.end():])
    if after:
        yield 'after', after.group(1)


def _coord_key(coord):
    """Numeric sort key so 3,7 precedes 3,70 and 12,1 follows 3,70."""
    return [int(x) for x in coord.split(',')]


def _same_root(a, b):
    """Do two SLP1 headwords name the same root once transliterated and normalized?"""
    return _norm(slp1_root_iast(a)) == _norm(slp1_root_iast(b))


def _disagreement_shape(a, b):
    """Name the KIND of difference between two dictionaries' root spellings.

    Descriptive only — nothing downstream resolves a coordinate by this. It exists
    because the raw disagreement count conflates two very different things:

      `guṇa ar~ṛ`   Two citation conventions for one root: PWG prints the guṇa grade
                    (`arj`, `vart`, `bhar`), MW the ṛ grade (`ṛj`, `vṛt`, `bhṛ`). This
                    is the single largest bucket and it is not a dispute about which
                    root is meant, so it is also counted into `cross_agree_with_variant`
                    — as a SEPARATE, deliberately weaker number, never folded into the
                    strict rate.
      `stem~root`   One spells the derived/causative stem, the other the root
                    (`pālay`/`pāl`, `puṣpy`/`puṣpya`, `goṣṭ`/`goṣṭha`).
      `one letter`  A genuine variant reading of the H328 class — `nāth`/`nādh`,
                    `mlich`/`mlech`, `ran`/`raṇ`. These are the interesting ones.
      `other`       Everything else, including nasal infixes (`tup`/`tump`,
                    `stabh`/`stambh`) and outright different roots."""
    if a.replace('ar', 'ṛ', 1) == b or b.replace('ar', 'ṛ', 1) == a:
        return 'guṇa ar~ṛ'
    if a.replace('al', 'ḷ', 1) == b or b.replace('al', 'ḷ', 1) == a:
        return 'guṇa al~ḷ'
    if a in b or b in a:
        return 'stem~root'
    if len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1:
        return 'one letter'
    return 'other'


def _mw_pass(mw, palsule, coords, table, pwg_root):
    """H4339. Fill PWG's dropped coordinates from MW, and cross-validate the rest.

    MUTATES `table` — MW-derived rows are added, PWG-derived rows are never touched or
    overwritten. Returns (stats, disagreements).

    TWO FILL CLASSES, KEPT APART:
      `mw`         — PWG had NO single claimant (Böhtlingk's double spellings), MW has
                     exactly one. This is the coverage win.
      `mw-respell` — PWG resolved the coordinate, but Palsule has no row for Böhtlingk's
                     spelling and MW spells the root differently (`kvel`/`kṣvel`), and
                     Palsule DOES have MW's. Materially weaker than `mw`: it prefers one
                     dictionary's citation form over the other's, so it is stamped
                     separately and counted separately, never merged into `mw`.

    NOT A FILL CLASS: PWG and MW agreeing on a root Palsule simply does not gloss. MW
    adds nothing there and the coordinate stays dropped.

    THE 53 DISAGREEMENTS ARE NOT RESOLVED HERE. Where both dictionaries resolve a
    coordinate to a single, different root, the PWG row stands (it is Böhtlingk's own
    numbering) and the conflict is reported verbatim for adjudication."""
    empty = {
        'mw_available': False, 'mw_source': None, 'mw_entries': 0,
        'mw_coords_cited': 0, 'mw_coords_cited_in_prose': 0,
        'mw_coords_in_westergaard_field': 0, 'mw_coords_single_claimant': 0,
        'mw_coords_single_claimant_prose_first': 0,
        'mw_prose_claims_refused_variant_reading': 0,
        'coords_filled_from_mw_prose_only': 0,
        'mw_coords_overlapping_pwg': 0, 'mw_only_coords': 0,
        'coords_filled_from_mw': 0, 'coords_filled_from_mw_respell': 0,
        'mw_candidates_without_palsule_row': 0,
        'cross_validated': 0, 'cross_agree': 0, 'cross_disagree': 0,
        'cross_agreement_rate': 0.0, 'cross_agree_with_variant': 0,
        'cross_agreement_rate_with_variant': 0.0, 'cross_disagreement_shapes': {},
    }
    if not mw or not os.path.exists(mw):
        sys.stderr.write('build_dhatup_palsule: MW not found at %s — '
                         'second-witness pass skipped\n' % mw)
        return empty, []

    (prose, field, field_seen, mw_entries,
     vl_dropped, prose_raw) = read_mw_coords(mw)
    # "Unambiguous" is deliberately the strictest reading available: exactly ONE article
    # claims the coordinate in whichever channel speaks for it. A coordinate with two
    # claimants is not used at all rather than resolved by a rule nobody has measured.
    mw_single = mw_claimants(prose, field, field_seen)
    # The counterfactual the docs compare against, published so the policy comparison
    # is re-derivable instead of asserted. Computed on `prose_raw` — the UNGUARDED
    # channel — because the policy being compared against is the one that shipped
    # before the v.l. guard existed; measuring it on the guarded channel would publish
    # a hybrid that never ran (caught by the second adjudication pass).
    #
    # It is HIGHER than field-first, and that is not a point against field-first: a
    # prose citation is easy to come by, so prose-first calls more coordinates
    # "unambiguous" while filling fewer of them, because most of its extra claimants
    # land on coordinates PWG had already resolved. Confident-looking noise in the
    # cross-validation, not coverage.
    prose_first = {c for c in set(prose_raw) | set(field_seen)
                   if len(prose_raw.get(c) or field.get(c) or ()) == 1}

    agree = disagree = variant = 0
    disagreements = []
    for coord in sorted(pwg_root, key=_coord_key):
        mw_r = mw_single.get(coord)
        if not mw_r:
            continue
        if _same_root(pwg_root[coord], mw_r):
            agree += 1
            variant += 1
            continue
        disagree += 1
        pwg_i = slp1_root_iast(pwg_root[coord])
        mw_i = slp1_root_iast(mw_r)
        shape = _disagreement_shape(pwg_i, mw_i)
        if shape == 'guṇa ar~ṛ':
            variant += 1
        disagreements.append({
            'coord': coord,
            'pwg_root_slp1': pwg_root[coord],
            'pwg_root_iast': pwg_i,
            'mw_root_slp1': mw_r,
            'mw_root_iast': mw_i,
            # What KIND of difference this is — read off the pair, so a reader
            # adjudicating them can start with the 'variant reading' bucket and leave
            # the regular alternations alone. Never used to resolve anything.
            'shape': shape,
            # Filled in after the fills below.
            'shipped_reading': None,
        })

    filled = respelled = no_row = 0
    prose_only_fills = 0
    for coord in sorted(set(coords) - set(table), key=_coord_key):
        mw_r = mw_single.get(coord)
        if not mw_r:
            continue
        pwg_r = pwg_root.get(coord)
        if pwg_r is not None and _same_root(pwg_r, mw_r):
            continue
        source = 'mw-respell' if pwg_r is not None else 'mw'
        extra = {'mw_root_slp1': mw_r}
        if pwg_r is not None:
            extra['pwg_root_slp1'] = pwg_r
            extra['pwg_root_iast'] = slp1_root_iast(pwg_r)
        else:
            # What Böhtlingk could not choose between, kept on the record so a reader
            # can see exactly which ambiguity MW is being trusted to break.
            extra['pwg_claimants'] = sorted(coords[coord])
        row = _palsule_record(palsule, mw_r, source, extra)
        if row is None:
            no_row += 1
            continue
        table[coord] = row
        if coord not in field_seen:
            # No MW field numbers this coordinate anywhere: the fill rests on running
            # prose alone. Weaker evidence than a field claim, so it is counted apart.
            prose_only_fills += 1
        if source == 'mw':
            filled += 1
        else:
            respelled += 1

    # Which reading a reader actually sees for a disputed coordinate: `pwg` when
    # Böhtlingk's attribution shipped (MW's dissent recorded, not acted on),
    # `mw-respell` when Palsule had no row for Böhtlingk's spelling so MW's spelling is
    # what the table could gloss at all, `dropped` when neither shipped. This states
    # what the artifact says; it does not resolve the disagreement.
    for d in disagreements:
        d['shipped_reading'] = (table[d['coord']]['source'] if d['coord'] in table
                                else 'dropped')

    mw_all = set(prose) | set(field_seen)
    overlap = len(mw_all & set(coords))
    examined = agree + disagree
    stats = {
        'mw_available': True,
        'mw_source': os.path.relpath(mw, GH),
        'mw_entries': mw_entries,
        'mw_coords_cited': len(mw_all),
        'mw_coords_cited_in_prose': len(prose),
        'mw_coords_in_westergaard_field': len(field_seen),
        'mw_coords_single_claimant': len(mw_single),
        'mw_coords_single_claimant_prose_first': len(prose_first),
        'mw_prose_claims_refused_variant_reading': len(vl_dropped),
        'mw_coords_overlapping_pwg': overlap,
        'mw_only_coords': len(mw_all) - overlap,
        'coords_filled_from_mw': filled,
        'coords_filled_from_mw_respell': respelled,
        'coords_filled_from_mw_prose_only': prose_only_fills,
        'mw_candidates_without_palsule_row': no_row,
        'cross_validated': examined,
        'cross_agree': agree,
        'cross_disagree': disagree,
        'cross_agreement_rate': (round(100.0 * agree / examined, 1)
                                 if examined else 0.0),
        # The weaker companion number, on the same pattern as the loose artha rate:
        # additionally counting the regular guṇa ar~ṛ alternation as agreement, since
        # `arj`/`ṛj` is two citation conventions for one root, not two roots.
        'cross_agree_with_variant': variant,
        'cross_agreement_rate_with_variant': (round(100.0 * variant / examined, 1)
                                              if examined else 0.0),
        'cross_disagreement_shapes': dict(sorted(
            Counter(d['shape'] for d in disagreements).items(),
            key=lambda kv: (-kv[1], kv[0]))),
    }
    return stats, disagreements


#: The WIDENED article-id space, and why it is a separate pass rather than a wider `_L`
#: (H4349). `_L` accepts an all-digit `<L>` id only, which is what H1333 measured PWG on;
#: 636 of PWG's 123,366 articles carry a dotted id (`<L>26305.560<pc>`) and are invisible
#: to it. Widening `_L` in place would move H1333's shipped `pwg_entries`, so the dotted
#: articles are read by a pass that runs BESIDE the H1333 pass, exactly like the MW one.
#: MEASURED RESULT, and the reason this class ships nothing: those 636 articles cite
#: exactly ONE `DHĀTUP.` coordinate between them. See `read_pwg_dotted_coords`.
def _scan_coords(path, dotted_only=False):
    """path -> ({coord: {root_slp1: [head, body, head_nominal]}}, n_articles_seen).

    The same reader as `read_pwg_coords` — same head-line weighting, same `<lex>`
    nominal flag, same two citation-splitting patterns — over the `[\\d.]+` id space
    instead of the all-digit one, so it can be pointed at PWG's dotted-id articles or
    at a sibling dictionary in the same Cologne markup. `read_pwg_coords` is
    deliberately NOT re-expressed in terms of this function: H1333's numbers are a
    shipped baseline and the code that produces them stays where a reader can see it
    untouched.
    """
    coords = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
    key = None
    at_head = False
    in_scope = False
    articles = 0
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = _L_ANY.match(line)
            if m:
                in_scope = ('.' in m.group(1)) if dotted_only else True
                key = m.group(2) if in_scope else None
                at_head = in_scope
                articles += 1 if in_scope else 0
                continue
            if line.startswith('<LEND>'):
                key = None
                continue
            if key is None:
                continue
            slot = 0 if at_head else 1
            nominal = bool(at_head and _HEAD_LEX.search(line))
            radical = bool(at_head and _HEAD_RADICAL.search(line))
            for rx in (_DHATUP, _DHATUP_N):
                for mm in rx.finditer(line):
                    coord = '%s,%s' % (mm.group(1), mm.group(2))
                    coords[coord][key][slot] += 1
                    if nominal:
                        coords[coord][key][2] += 1
                    if radical:
                        coords[coord][key][3] += 1
            at_head = False
    return coords, articles


def read_pwg_dotted_coords(pwg):
    """PWG's 636 dotted-id articles -> the coordinates they cite (H4349).

    THE ANSWER IS ONE COORDINATE, and it is worth stating plainly because the
    expectation going in was a large hidden evidence class: 636 articles, one
    `DHĀTUP.` citation between them — `15,89`, claimed by `4. kar` in
    `<L>26305.560<pc>2-1103<k1>kar`. That coordinate was already contested without
    this pass (`<L>18794` heads it `kfv`; `<L>69734` claims it for `kar` again), and
    Böhtlingk's own prose in the `kfv` article says the root is `kṛv`, placed under
    `kar`, with its final `-v` unjustified — two readings, stated by the same
    lexicographer, which is exactly the shape the multi-claimant filter refuses to
    resolve by counting votes. So the dotted-id pass adds a third citation to an
    already-dropped coordinate and ships nothing.

    That is a negative result, not a wasted pass. Before it, "the dotted-id articles
    are unread" was an open hypothesis about the size of the gap; after it, the gap is
    measured at one coordinate and pinned by a regression, so a corpus update that
    puts real coordinates into that id space fails a test instead of passing silently.
    """
    return _scan_coords(pwg, dotted_only=True)


def read_pw_coords(pw):
    """pw.txt (Sanskrit-Wörterbuch in kürzerer Fassung) -> coordinates it cites.

    Böhtlingk's own abridgement, so a coordinate here is the same author's numbering
    rather than a second opinion — but the abridgement REDISTRIBUTES its citations:
    where pwg states a coordinate on the root's own head line, pw very often states it
    on the head line of the *artha* noun instead (`{#uttrAsana#}¦ <lex>n.</lex> …
    <ls>DHĀTUP. 9,15</ls>`). Harvesting a pw claimant without the `<lex>` nominal test
    would therefore ship meanings as roots — nine of pw's seventeen otherwise-unfilled
    coordinates are exactly that. The nominal discriminator PWG needed as a refinement
    is load-bearing here.
    """
    return _scan_coords(pw)


def coordinate_ceilings(coords):
    """gaṇa -> the highest serial PWG itself ever cites in that gaṇa.

    THE GUARD AGAINST A CITATION-SPLIT ARTIFACT, derived from the corpus and never
    typed as a constant. pw's Nachträge carry `<ls>DHĀTUP. 1,840</ls>` (√{#can#}) and
    `<ls>DHĀTUP. 1,960</ls>` ({#Kadana#}); PWG cites gaṇa 1 exactly twice and MW once,
    every time as the single coordinate `1,1` — bhū, the first root of the dhātupāṭha.
    A gaṇa whose attested serials stop at 1 does not have an 840th root, so those two
    numbers are not points in this coordinate space at all: they are some other
    numbering of Westergaard that the supplement reaches for twice. Admitting them
    would mint two coordinates no witness can confirm and would collide with any
    genuine future `1,840`. They are refused, listed, and counted — never quietly kept
    and never quietly dropped.
    """
    ceil = {}
    for coord in coords:
        gana, serial = _coord_key(coord)
        if serial > ceil.get(gana, 0):
            ceil[gana] = serial
    return ceil


def _sibling_pass(label, source_coords, articles, source_path, palsule,
                  pwg_root, table, ceilings, same_book_conflicted=frozenset()):
    """H4349. Fill still-empty coordinates from a PWG-family sibling. MUTATES `table`.

    `label` is the provenance token stamped on every row this pass adds (`pwg-dotted`
    or `pw`). Rows already in `table` — PWG's, MW's, or an earlier sibling's — are
    never touched or overwritten, so H1333's and H4339's shipped artifacts survive this
    pass byte-for-byte and a consumer that wants either of them filters on `source`.

    A coordinate is used only when the sibling gives it ONE claimant on the head line
    of an article Böhtlingk marks as verbal with `√` (see `_HEAD_RADICAL`): a body
    citation is a quotation, an unmarked head line is a noun being glossed, and two
    marked claimants is an ambiguity this pass has no standing to break.

    `same_book_conflicted` is the guard that keeps the `pwg-dotted` pass honest. MW and
    pw are different books, so a claim of theirs on a coordinate PWG left contested is
    new evidence and may fill it — that is the whole coverage argument of H4339. PWG's
    own dotted-id articles are not a different book: a citation there belongs in PWG's
    claimant set, and letting it fill a coordinate PWG's multi-claimant filter
    deliberately dropped would resolve a conflict by adding a vote, which is precisely
    what that filter refuses to do. Coordinates PWG conflicted on are therefore closed
    to a same-book pass and counted apart. (`15,89` is the live case, and it is worth
    knowing it was ALSO refused by the `√` test — the guard is not what happens to save
    it today, which is why it is stated as a rule rather than left to the accident.)
    """
    empty = {
        '%s_available' % label: False, '%s_source' % label: None,
        '%s_articles' % label: 0, '%s_coords_cited' % label: 0,
        '%s_coords_single_verbal_claimant' % label: 0,
        '%s_refused_out_of_coordinate_space' % label: 0,
        '%s_refused_nominal_head' % label: 0,
        '%s_refused_body_only' % label: 0,
        '%s_refused_multiple_claimants' % label: 0,
        '%s_refused_same_book_conflict' % label: 0,
        '%s_coords_overlapping_shipped' % label: 0,
        '%s_candidates_without_palsule_row' % label: 0,
        'coords_filled_from_%s' % label: 0,
        '%s_cross_validated' % label: 0, '%s_cross_agree' % label: 0,
        '%s_cross_disagree' % label: 0, '%s_cross_agreement_rate' % label: 0.0,
        '%s_cross_agree_modulo_citation_form' % label: 0,
        '%s_cross_agreement_rate_modulo_citation_form' % label: 0.0,
        '%s_cross_disagreement_shapes' % label: {},
    }
    if not source_coords and not articles:
        return empty, [], []

    claims = {}
    out_of_space = []
    nominal = body_only = multi = same_book = 0
    for coord, roots in source_coords.items():
        gana, serial = _coord_key(coord)
        if coord in same_book_conflicted:
            same_book += 1
            continue
        if serial > ceilings.get(gana, 0):
            out_of_space.append({
                'coord': coord,
                'gana': gana,
                'serial': serial,
                'attested_ceiling': ceilings.get(gana),
                'claimants': sorted(roots),
                'verdict': 'refused: not a point in the attested coordinate space',
            })
            continue
        head = [r for r, c in roots.items() if c[0]]
        if not head:
            body_only += 1
            continue
        verbal = [r for r in head if roots[r][3] and not roots[r][2]]
        if not verbal:
            nominal += 1
            continue
        if len(verbal) != 1:
            multi += 1
            continue
        claims[coord] = verbal[0]

    # Shapes that are two citation conventions for one root rather than two roots:
    # `vṛkṣ`/`varkṣ` is the regular guṇa alternation, `karṇ`/`karṇay` is the root
    # against the denominative stem pw happens to head its article with. Folded into a
    # COMPANION rate, never into the strict one — same treatment H4339 gives the guṇa
    # shape in the MW cross-validation, so the two witnesses stay comparable.
    _CITATION_FORM = ('guṇa ar~ṛ', 'guṇa al~ḷ', 'stem~root')
    agree = disagree = lenient = 0
    disagreements = []
    for coord in sorted(set(claims) & set(pwg_root), key=_coord_key):
        if _same_root(pwg_root[coord], claims[coord]):
            agree += 1
            lenient += 1
            continue
        disagree += 1
        if _disagreement_shape(slp1_root_iast(pwg_root[coord]),
                               slp1_root_iast(claims[coord])) in _CITATION_FORM:
            lenient += 1
        disagreements.append({
            'coord': coord,
            'source': label,
            'pwg_root_slp1': pwg_root[coord],
            'pwg_root_iast': slp1_root_iast(pwg_root[coord]),
            'sibling_root_slp1': claims[coord],
            'sibling_root_iast': slp1_root_iast(claims[coord]),
            'shape': _disagreement_shape(slp1_root_iast(pwg_root[coord]),
                                         slp1_root_iast(claims[coord])),
        })

    filled = no_row = 0
    for coord in sorted(set(claims) - set(table), key=_coord_key):
        root = claims[coord]
        extra = {'%s_root_slp1' % label: root}
        if coord in pwg_root:
            extra['pwg_root_slp1'] = pwg_root[coord]
            extra['pwg_root_iast'] = slp1_root_iast(pwg_root[coord])
        row = _palsule_record(palsule, root, label, extra)
        if row is None:
            no_row += 1
            continue
        table[coord] = row
        filled += 1

    examined = agree + disagree
    stats = {
        '%s_available' % label: True,
        '%s_source' % label: os.path.relpath(source_path, GH),
        '%s_articles' % label: articles,
        '%s_coords_cited' % label: len(source_coords),
        '%s_coords_single_verbal_claimant' % label: len(claims),
        '%s_refused_out_of_coordinate_space' % label: len(out_of_space),
        '%s_refused_nominal_head' % label: nominal,
        '%s_refused_body_only' % label: body_only,
        '%s_refused_multiple_claimants' % label: multi,
        '%s_refused_same_book_conflict' % label: same_book,
        '%s_coords_overlapping_shipped' % label: len(set(source_coords) & set(table)),
        '%s_candidates_without_palsule_row' % label: no_row,
        'coords_filled_from_%s' % label: filled,
        '%s_cross_validated' % label: examined,
        '%s_cross_agree' % label: agree,
        '%s_cross_disagree' % label: disagree,
        '%s_cross_agreement_rate' % label: (round(100.0 * agree / examined, 1)
                                            if examined else 0.0),
        '%s_cross_agree_modulo_citation_form' % label: lenient,
        '%s_cross_agreement_rate_modulo_citation_form' % label: (
            round(100.0 * lenient / examined, 1) if examined else 0.0),
        '%s_cross_disagreement_shapes' % label: dict(sorted(
            Counter(d['shape'] for d in disagreements).items(),
            key=lambda kv: (-kv[1], kv[0]))),
    }
    return stats, disagreements, out_of_space


def _palsule_record(palsule, root_slp1, source, extra=None):
    """One table row, or None when Palsule has no entry for that root spelling."""
    root_iast = slp1_root_iast(root_slp1)
    rec = palsule.get(_norm(root_iast))
    if not rec:
        return None
    row = {
        'root_slp1': root_slp1,
        'root_iast': root_iast,
        # Which dictionary attributed this coordinate to this root. `pwg` is H1333's
        # rule (Böhtlingk's own article); the `mw*` values are H4339's second witness.
        # A consumer that must not mix them filters on this key.
        'source': source,
        'palsule_root': rec['root_iast'],
        'pages': rec['pages'],
        'pada': rec['pada'],
        # Stored in FULL. An earlier cut truncated to 8, which silently dropped
        # `sattāyām` from DHĀTUP. 1,1 — bhū's canonical artha and the first entry of
        # the whole dhātupāṭha — while `artha_count` still said 11. The tooltip does
        # its own display-time limiting; the data layer keeps everything.
        'arthas': rec['arthas'],
        'artha_count': len(rec['arthas']),
    }
    row.update(extra or {})
    return row


def build(xls, pwg, mw=None, pw=None, pwg_dotted=True):
    palsule, xls_rows, typo_folds = read_palsule(xls)
    coords, entries = read_pwg_coords(pwg)

    # Baseline for the filters' measured contribution: with NO disambiguation at all,
    # every multi-claimant coordinate is simply dropped. Recorded so the "filters bought
    # us X points" claim in the docs is derivable from the artifact, not asserted.
    unfiltered_linked = sum(
        1 for c, roots in coords.items()
        if len(roots) == 1 and palsule.get(_norm(slp1_root_iast(next(iter(roots)))))
    )

    table = {}
    conflicts = []
    unmatched = []
    #: coord -> the ONE root PWG attributes it to, whether or not Palsule has that root.
    #: The cross-validation below compares this against MW, so a coordinate PWG resolved
    #: but Palsule could not gloss still counts as a comparable PWG verdict.
    pwg_root = {}
    resolved_by_head = 0
    for coord, roots in sorted(coords.items(), key=lambda kv: [int(x) for x in kv[0].split(',')]):
        if len(roots) > 1:
            head = [r for r, c in roots.items() if c[0]]
            if len(head) > 1:
                # Drop the nominal head-line claimants (`<lex>` articles quoting the
                # coordinate as a gloss); what survives is the verbal article.
                verbal = [r for r in head if not roots[r][2]]
                if verbal:
                    head = verbal
            if len(head) != 1:
                # No single head-line claimant -> not safely attributable. Drop it;
                # never pick a winner by citation count.
                conflicts.append({'coord': coord, 'roots': sorted(roots),
                                  'head_claimants': sorted(head)})
                continue
            resolved_by_head += 1
            root_slp1 = head[0]
        else:
            root_slp1 = next(iter(roots))
        pwg_root[coord] = root_slp1
        row = _palsule_record(palsule, root_slp1, 'pwg')
        if row is None:
            unmatched.append({'coord': coord, 'root_slp1': root_slp1,
                              'root_iast': slp1_root_iast(root_slp1)})
            continue
        table[coord] = row

    linked_pwg = len(table)
    mw_stats, mw_disagreements = _mw_pass(mw, palsule, coords, table, pwg_root)
    linked_after_mw = len(table)

    # H4349. Two more PWG-FAMILY sources, run after MW so they can only fill what is
    # still empty, each stamped with its own token and each measured on its own. The
    # ceiling is derived from PWG's citations alone — the sibling being screened must
    # not be allowed to widen the space it is screened against.
    ceilings = coordinate_ceilings(coords)
    dotted_coords, dotted_articles = (read_pwg_dotted_coords(pwg) if pwg_dotted
                                      else ({}, 0))
    dotted_stats, dotted_disagreements, dotted_out = _sibling_pass(
        'pwg-dotted', dotted_coords, dotted_articles, pwg, palsule, pwg_root,
        table, ceilings,
        same_book_conflicted=frozenset(c['coord'] for c in conflicts))
    if pw and os.path.exists(pw):
        pw_coords, pw_articles = read_pw_coords(pw)
    else:
        if pw:
            sys.stderr.write('build_dhatup_palsule: pw not found at %s — '
                             'kuerzere-Fassung pass skipped\n' % pw)
        pw_coords, pw_articles = {}, 0
    pw_stats, pw_disagreements, pw_out = _sibling_pass(
        'pw', pw_coords, pw_articles, pw or DEFAULT_PW, palsule, pwg_root,
        table, ceilings)

    stats = {
        'built': date.today().strftime('%d-%m-%Y'),
        'source_xls': os.path.basename(xls),
        'source_pwg': os.path.relpath(pwg, GH),
        'xls_artha_rows': xls_rows,
        'xls_root_typo_folds': typo_folds,
        'xls_distinct_roots': len(palsule),
        'pwg_entries': entries,
        'coords_cited': len(coords),
        'coords_conflicted': len(conflicts),
        'coords_resolved_by_head_line': resolved_by_head,
        'coords_unmatched': len(unmatched),
        # PWG-derived rows only — H1333's shipped number, deliberately still readable
        # after the MW rows land beside it.
        'coords_linked_pwg': linked_pwg,
        'match_rate_pwg': (round(100.0 * linked_pwg / len(coords), 1)
                           if coords else 0.0),
        'coords_linked': len(table),
        'match_rate': round(100.0 * len(table) / len(coords), 1) if coords else 0.0,
        'coords_linked_without_filters': unfiltered_linked,
        'match_rate_without_filters': (round(100.0 * unfiltered_linked / len(coords), 1)
                                       if coords else 0.0),
    }
    stats.update(mw_stats)
    stats['coords_linked_after_mw'] = linked_after_mw
    stats.update(dotted_stats)
    stats.update(pw_stats)
    # Recomputed AFTER the sibling passes. `coords` is PWG's citation set and stays the
    # denominator: a sibling fills coordinates PWG cites but never resolved, so the
    # numerator grows while the denominator does not. A sibling-only coordinate cannot
    # enter here — the ceiling screen keeps every candidate inside PWG's own space —
    # but the asymmetry is stated rather than left to be inferred.
    stats['coords_linked'] = len(table)
    stats['match_rate'] = (round(100.0 * len(table) / len(coords), 1)
                           if coords else 0.0)
    stats['coords_refused_out_of_coordinate_space'] = (
        len(dotted_out) + len(pw_out))
    # The artha measurement stays on the PWG-derived rows, so the H1333 number
    # (139/232 = 59.9%) means the same thing before and after H4339. MW rows are
    # measured separately: PWG's parenthesized artha is still an independent witness
    # for them, but pooling the two would silently redefine the shipped accuracy figure.
    agree, disagree, examined, samples, loose = audit_inline_artha(
        pwg, table, sources=('pwg',))
    stats['inline_artha_examined'] = examined
    stats['inline_artha_agree'] = agree
    stats['inline_artha_disagree'] = disagree
    stats['inline_artha_agreement_rate'] = (round(100.0 * agree / examined, 1)
                                            if examined else 0.0)
    stats['inline_artha_agree_loose'] = loose
    stats['inline_artha_agreement_rate_loose'] = (round(100.0 * loose / examined, 1)
                                                  if examined else 0.0)
    m_agree, _m_dis, m_examined, mw_artha_samples, m_loose = audit_inline_artha(
        pwg, table, sources=('mw', 'mw-respell'))
    stats['inline_artha_examined_mw'] = m_examined
    stats['inline_artha_agree_mw'] = m_agree
    stats['inline_artha_agreement_rate_mw'] = (round(100.0 * m_agree / m_examined, 1)
                                               if m_examined else 0.0)
    stats['inline_artha_agree_loose_mw'] = m_loose
    stats['inline_artha_agreement_rate_loose_mw'] = (
        round(100.0 * m_loose / m_examined, 1) if m_examined else 0.0)
    sibling = {
        'disagreements': dotted_disagreements + pw_disagreements,
        'out_of_coordinate_space': dotted_out + pw_out,
    }
    return (table, stats, conflicts, unmatched, samples, mw_disagreements,
            mw_artha_samples, sibling)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xls', default=DEFAULT_XLS)
    ap.add_argument('--pwg', default=DEFAULT_PWG)
    ap.add_argument('--mw', default=DEFAULT_MW,
                    help='Monier-Williams, the second coordinate witness (H4339). '
                         'Pass --mw "" to rebuild the H1333 PWG-only table.')
    ap.add_argument('--pw', default=DEFAULT_PW,
                    help="Sanskrit-Woerterbuch in kuerzerer Fassung, Boehtlingk's own "
                         'abridgement and the third coordinate witness (H4349). '
                         'Pass --pw "" to skip it.')
    ap.add_argument('--no-pwg-dotted', action='store_true',
                    help="Skip the pass over PWG's 636 dotted-id articles (H4349).")
    ap.add_argument('--out', default=DEFAULT_OUT)
    a = ap.parse_args()

    (table, stats, conflicts, unmatched, artha_samples,
     mw_disagreements, mw_artha_samples, sibling) = build(
         a.xls, a.pwg, a.mw, a.pw, pwg_dotted=not a.no_pwg_dotted)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    payload = {
        '_README': (
            'DHĀTUP. gaṇa,serial -> what Palsule records FOR THAT ROOT SPELLING. '
            'Built by src/build_dhatup_palsule.py (H1333). '
            'GRANULARITY: keyed by coordinate, but the content is the union of every '
            'XLS row whose root normalizes to the same spelling. Palsule\'s artha index '
            'is keyed on the root, not on gaṇa,serial, so it CANNOT separate the '
            'homonyms Böhtlingk numbers apart: 26,91 is the divādi snih, but its arthas '
            'are every snih in Palsule. Read a record as "what Palsule says about this '
            'root", never as "what Palsule says at exactly this coordinate". '
            'The coordinate->root half is read off PWG itself (the citation sits in the '
            'root\'s own article, <k1> is the dhātu); only root->Palsule is a join. '
            'Coordinates whose citing articles disagree on the root are DROPPED, not '
            'guessed. ACCURACY: _stats.inline_artha_* measures the table against the '
            'artha PWG itself prints beside the citation — an independent witness. '
            'Coverage and accuracy are different numbers; both are in _stats. '
            'PROVENANCE (H4339): every row carries `source` — `pwg` is Böhtlingk\'s own '
            'attribution (H1333), `mw` is a coordinate PWG could not disambiguate that '
            'Monier-Williams claims for exactly one root, `mw-respell` is a coordinate '
            'PWG resolved to a root Palsule does not gloss where MW\'s spelling of it '
            'is in Palsule. Filter on `source` to get the PWG-only table back. Where '
            'both dictionaries resolve a coordinate to a DIFFERENT single root, the PWG '
            'reading stands and the conflict is listed in `_mw_disagreements` for '
            'adjudication — never resolved by picking a winner.'
            ' TWO MORE PWG-FAMILY SOURCES (H4349), each stamped apart and never '
            'merged into `pwg`: `pwg-dotted` is a coordinate cited only by one of '
            'PWG\'s 636 dotted-id articles, which the H1333 scan\'s all-digit <L> '
            'pattern cannot see; `pw` is a coordinate from Böhtlingk\'s own '
            'abridgement, the Sanskrit-Wörterbuch in kürzerer Fassung. Both are '
            'admitted only on a single VERBAL head-line claimant — pw states most of '
            'its DHĀTUP. citations on the head line of the artha noun rather than the '
            'root, so the <lex> nominal test that is a refinement for PWG is '
            'load-bearing there. Both are screened against the attested coordinate '
            'space (the highest serial PWG itself cites in that gaṇa); refusals are '
            'listed in `_out_of_coordinate_space` with the ceiling they failed, never '
            'silently dropped.'),
        '_stats': stats,
        # Listed, not resolved. Each row is a live disagreement between two Böhtlingk-
        # numbering witnesses about which root a coordinate belongs to.
        '_mw_disagreements': mw_disagreements,
        # The same shape for the H4349 siblings, kept in their own key so a consumer
        # reading H4339's disagreement list is unaffected by their arrival.
        '_sibling_disagreements': sibling['disagreements'],
        # Citations that name a point outside the attested coordinate space. Published
        # because "we dropped two numbers" is a claim a reader must be able to check:
        # each row carries the gaṇa, the serial, the ceiling it exceeded and who cited
        # it, so the adjudication is re-derivable rather than asserted.
        '_out_of_coordinate_space': sibling['out_of_coordinate_space'],
        'table': table,
    }
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write('\n')
    for k, v in stats.items():
        print('%-22s %s' % (k, v))
    print('wrote %s' % a.out)
    if conflicts:
        print('sample conflicts: %s' % json.dumps(conflicts[:5], ensure_ascii=False))
    if unmatched:
        print('sample unmatched: %s' % json.dumps(unmatched[:8], ensure_ascii=False))
    if artha_samples:
        print('sample inline-artha disagreements: %s'
              % json.dumps(artha_samples[:5], ensure_ascii=False))
    if mw_artha_samples:
        print('sample inline-artha disagreements (MW-derived rows): %s'
              % json.dumps(mw_artha_samples[:3], ensure_ascii=False))
    if mw_disagreements:
        print('PWG/MW root disagreements (%d, listed in full in _mw_disagreements): %s'
              % (len(mw_disagreements),
                 ', '.join('%s PWG=%s MW=%s' % (d['coord'], d['pwg_root_iast'],
                                                d['mw_root_iast'])
                           for d in mw_disagreements[:8])))


if __name__ == '__main__':
    main()
