#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H1681 — agent adjudication of ALL 4,226 PWG-vs-index compound `differs` rows.

Per the H1664 triage (screening audit §11, verdict HYBRID-B2): the ~4.2k-row
`differs` queue flagged by H1624 G6 is not votable by a human, so every row gets an
agent verdict with a rule label and CITED EVIDENCE, and the already-built 200-card
stratified sheet (H1628, seed=1628) becomes the blind verification arm that prices
this adjudicator per stratum. Same pattern as H1657 (`adjudicate_p2.py`).

## What the two sides actually are (read this before trusting a verdict)

Neither side is a machine guess; both are dictionary text, and they were never
built to the same specification:

* **PWG side** — `compound_members_pwg`, from `SanskritGrammar/data/pwg_compound_split/`,
  mined from PWG's etymology parenthesis: `{#aMsatrakoSa#}¦ ({#aMsatra#} + {#koSa#})`.
  Böhtlingk & Roth state the compound's **underlying members as lexemes**, in lemma
  form; they do NOT have to spell the headword back.
* **index side** — `headword_index.tsv:compound_members`, from `mw_compounds.py`,
  i.e. Jim Funderburk's em-dash segmentation of MW's `<k2>`: `a/Msa—tra—koSa`. This
  is a **surface segmentation**: its members concatenate back to the headword by
  construction (4,142/4,226 exactly, vs 81/4,226 on the PWG side).

So most of this queue is not "one dictionary is wrong". It is two conventions
meeting, plus four upstream extractor defects that this pass measures and works
around **in memory** (it does not rewrite either upstream file — that is a non-goal
of H1681, exactly as H1657 was forbidden from re-running P0/P1).

## The four upstream defects this pass measures

1. `pwg_layer_inner_chain` — PWG nests sub-analyses in brackets:
   `({#akftta#} [<hom>3.</hom> {#a#} + {#kftta#} …] + {#ruc#})`. The extractor takes the
   FIRST `+`-chain in the entry head with no bracket awareness, so it captured the
   INNER chain `a + kftta` instead of the top-level `akftta + ruc`.
2. `pwg_layer_no_headword_paren` — the first `+`-chain in the head can belong to a
   *different* word: `{#aDikazAzwika#}¦ <lex>adj.</lex> von {#aDikazazwi#} ({#aDika#} +
   {#zazwi#})` — those members compose `aDikazazwi`, not the headword.
3. `mw_variant_fusion` — MW lists variants inside one `<k2>`: `gaRa—kAri; gaRakAri`.
   `mw_compounds._clean_member` strips `;` AND the space, fusing the variants into a
   bogus member `kArigaRakAri`.
4. Both sides defective at once (1 row).

Verdicts: `pwg_members-right` (= the sheet's *approve*) · `index_members-right`
(= *reject*) · `unresolved` (= *defer*). Nothing here writes the store: promotion of
non-sampled rows is gated on the human 200-vote and a per-stratum Wilson-95 % lower
bound, computed by `--write` into the promotion plan.

Usage:
    python src/pilot/adjudicate_compound_differs.py --selftest   parsers + rules on fixtures
    python src/pilot/adjudicate_compound_differs.py --report     counts only, writes nothing
    python src/pilot/adjudicate_compound_differs.py --write      verdicts TSV + promotion plan JSON
"""
import csv
import io
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))                 # src/pilot
SRC = os.path.dirname(HERE)                                       # src
REPO = os.path.dirname(SRC)                                       # RussianTranslation
SL = os.path.dirname(REPO)                                        # SanskritLexicography
GITHUB = os.path.dirname(SL)

DERIV_TSV = os.path.join(SRC, 'pwg_derivation_layer.tsv')
INDEX_TSV = os.path.join(SRC, 'headword_index.tsv')
FREQ_TSV = os.path.join(SRC, 'pwg_freq_order.tsv')
FRAME_TSV = os.path.join(REPO, 'review',
                         'sanskritlexicography-pwg-compound-differs_stratified200_frame.tsv')
LOCK_DIR = os.path.join(REPO, 'review', 'locks')

# The blind arms, in the order they were drawn. Card ids come from each sheet's
# COMMITTED LOCK, not its frame TSV: the lock is what `validate_decisions.py` will
# check the human's export against, so it is the only list that can actually pay out.
ARMS = (
    ('arm1 (H1628)', 'sanskritlexicography-pwg-compound-differs_stratified200'),
    ('arm2 (H1703)', 'sanskritlexicography-pwg-compound-differs_rulestrat_arm2'),
)
HWL_DIR = os.path.join(SL, 'HeadwordLists', 'now-2026')
SG_ROOT = os.environ.get('SANSKRITGRAMMAR_ROOT', os.path.join(GITHUB, 'SanskritGrammar'))
CSL_ORIG = os.environ.get('CSL_ORIG_ROOT', os.path.join(GITHUB, 'csl-orig'))
PWG_TXT = os.path.join(CSL_ORIG, 'v02', 'pwg', 'pwg.txt')
MW_TXT = os.path.join(CSL_ORIG, 'v02', 'mw', 'mw.txt')

OUT_TSV = os.path.join(REPO, 'research', 'pwg_compound_differs_adjudication.tsv')
OUT_PLAN = os.path.join(REPO, 'research', 'pwg_compound_differs_promotion_plan.json')

ADJUDICATOR = ('adjudicate_compound_differs.py (H1681, Opus 5 1M `claude-opus-5[1m]`)')

# ---------------------------------------------------------------- source parsing

MEMBER_RE = re.compile(r'\{#([^#]+)#\}')
HEAD_RE = re.compile(r'\{#[^#]+#\}¦\s*')      # `{#headword#}¦ `
ENTRY_RE = re.compile(r'<L>([\d.]+).*?<k1>([^<]*)<k2>([^<]*)')
K2_STRIP = str.maketrans('', '', "/'^;| ")          # accents + the variant separator
EMDASH = '—'
GAP_MAX = 120          # chars of annotation a paren may sit behind and still be ours
MAX_CANDIDATES = 24    # product cap when a part offers several candidate members


def mask_brackets(s):
    """Blank every `[...]` group (PWG's nested sub-analysis) keeping offsets."""
    out = list(s)
    depth = 0
    for i, ch in enumerate(s):
        if ch == '[':
            depth += 1
        if depth:
            out[i] = ' '
        if ch == ']' and depth:
            depth -= 1
    return ''.join(out)


def balanced_paren(s):
    """The balanced `(...)` group at the head of `s`, or None."""
    if not s.startswith('('):
        return None
    depth = 0
    for i, ch in enumerate(s):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return s[:i + 1]
    return None


def head_paren(body):
    """The balanced paren belonging to THIS entry's own headword, or (None, why).

    Anchored on the entry's `{#headword#}¦`. The paren may open after annotation-only
    material (`<lex>m.</lex>`, a sense number `1〉`) — but never after another
    `{#word#}` (that paren analyses the OTHER word), nor too far into the article. A
    paren behind a citation or a gloss is only PROVISIONALLY the headword's: it has to
    compose the headword to count.
    """
    m = HEAD_RE.search(body)
    if not m:
        return None, 'no_head'
    rest = body[m.end():]
    i = 0 if rest.startswith('(') else rest.find('(')
    if i < 0:
        return None, 'no_paren'
    provisional = False
    if i:
        gap = rest[:i]
        if MEMBER_RE.search(gap):
            return None, 'paren_after_other_word'
        if len(gap) > GAP_MAX:
            return None, 'paren_too_far'
        provisional = '<ls' in gap or '{%' in gap
    paren = balanced_paren(rest[i:])
    if not paren:
        return None, 'unbalanced'
    return paren, 'ok_provisional' if provisional else 'ok'


def covers_surface(hw, members):
    """Do these members account for the headword's surface? Sandhi at a seam moves the
    length by about a character, so a chain that accounts for the headword lands within
    ±1 per member; one that falls short by more is analysing something else — typically
    the base of a *derivative* of the compound (`DvajAgravatI` ← `DvajAgravant` ←
    `Dvaja + agra`)."""
    return abs(sum(len(m) for m in members) - len(hw)) <= len(members)


def pwg_toplevel(body, hw=None):
    """PWG's TOP-LEVEL member chain for the entry's own headword.

    Returns (members|None, paren_text|None, status). Bracket-aware, and within each
    `+`-separated part the member is normally the FIRST `{#…#}` — what follows it is
    PWG's annotation of that member (`<lex>f.</lex> von {#agamya#}`, `= {#loman#}`,
    `<ab>acc.</ab> von {#agni#}`), not a second member. Where a part offers several
    candidates (a derivation ladder or disjunction: `von {#BAnumant#} oder von
    {#BAnu#} + {#mati#}`) the chain is settled against the headword's surface, and
    ambiguity is dropped rather than guessed.

    Kept in sync with `pwg_toplevel()` in SanskritGrammar's
    `scripts/pwg_compound_split.py` (SanskritGrammar#527), which BUILDS the layer this
    pass adjudicates: if the two disagree about what PWG says, this queue measures the
    extractors instead of the dictionaries.
    """
    paren, status = head_paren(body)
    if not paren:
        return None, None, status
    inner = mask_brackets(paren[1:-1])
    parts = []
    for part in inner.split('+'):
        found = MEMBER_RE.findall(part)
        if not found:
            return None, paren, 'part_without_member'
        if len(found) > 1 and EMDASH in part.split('{#', 1)[1]:
            return None, paren, 'ambiguous_sense_divider'
        parts.append(found)
    if len(parts) < 2:
        return None, paren, 'single_member'
    first = [p[0] for p in parts]
    if hw is None:
        return first, paren, 'ok'
    if covers_surface(hw, first):
        return first, paren, 'ok'
    if status == 'ok_provisional':
        return None, paren, 'paren_after_article_text'
    if all(len(p) == 1 for p in parts):
        return first, paren, 'ok'
    total = 1
    for p in parts:
        total *= len(p)
    if total > MAX_CANDIDATES:
        return None, paren, 'ambiguous_too_many_candidates'
    covering = [c for c in itertools.product(*parts) if covers_surface(hw, c)]
    if len(covering) == 1:
        return list(covering[0]), paren, 'ok'
    return None, paren, 'ambiguous_no_unique_cover'


def mw_variants(k2):
    """MW `<k2>` -> (raw variants, first-variant em-dash members WITH hyphens kept).

    MW's own two boundary marks are distinct and both are evidence: `—` (em-dash)
    separates members, `-` (hyphen) marks a bound juncture INSIDE a member (`a-kAma`
    = the privative bound to kāma). `mw_compounds.py` strips the hyphen; this keeps
    it, because a hyphen is MW telling us where it does NOT put a member boundary.
    """
    variants = [v.strip() for v in k2.split(';') if v.strip()]
    if not variants:
        return [], []
    segs = [s.strip().translate(K2_STRIP) for s in variants[0].split(EMDASH)]
    return variants, [s for s in segs if s]


def entries(path):
    """Yield (L_id, k1, k2, body) for every csl-orig entry."""
    L = k1 = k2 = None
    buf, on = [], False
    with io.open(path, encoding='utf-8') as fh:
        for ln in fh:
            ln = ln.rstrip('\n')
            h = ENTRY_RE.match(ln)
            if h:
                if on:
                    yield L, k1, k2, '\n'.join(buf)
                L, k1, k2 = h.group(1), h.group(2), h.group(3)
                buf, on = [], True
                continue
            if on:
                if ln.startswith('<LEND>'):
                    yield L, k1, k2, '\n'.join(buf)
                    on = False
                else:
                    buf.append(ln)
        if on:
            yield L, k1, k2, '\n'.join(buf)


# ---------------------------------------------------------------- member folding

# Internal-sandhi and stem-vs-surface alternations that make two spellings the SAME
# member, not two different ones. MW spells the segment as it stands in the compound
# (`agni + zwut`, `agni + jihva`); PWG names the lexeme (`agni + stut`, `agni + jihvA`).
_RETRO = str.maketrans('zRwWqQ', 'sntTdD')


def fold(m):
    """Normalize a member for identity comparison across the two conventions."""
    s = m.replace('-', '')
    s = s.translate(_RETRO)
    # final long vowel vs short (jihvA/jihva, devA/deva, BU/Bu)
    if s and s[-1] in 'AIU':
        s = s[:-1] + {'A': 'a', 'I': 'i', 'U': 'u'}[s[-1]]
    # final visarga / anusvāra vs the underlying consonant (antar/antaH, kim/kiM)
    if s.endswith('H') or s.endswith('M'):
        s = s[:-1]
    elif s.endswith('r') or s.endswith('s') or s.endswith('m') or s.endswith('n'):
        s = s[:-1]
    elif s.endswith('d') or s.endswith('t'):
        s = s[:-1]
    # vocalic ṛ written out at the seam (nar/nf, kar/kf)
    if s.endswith('ar'):
        s = s[:-2] + 'f'
    return s


def levenshtein(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# Vowel -> glide before a vowel-initial second member (vi + aBra -> vy-aBra).
GLIDE = {'i': 'y', 'I': 'y', 'u': 'v', 'U': 'v', 'f': 'r', 'F': 'r'}


def glide_alt(p, s):
    return len(p) >= 2 and p[:-1] == s[:-1] and GLIDE.get(p[-1]) == s[-1:]


def seam_compatible(p, s):
    """Is PWG's member `p` the lexeme behind MW's surface segment `s`?

    The two sources differ systematically at the seam: PWG cites the stem
    (`sant`, `diS`, `payas`, `brahman`, `vi`, `kim`), MW the sandhi-adjusted surface
    (`saj`, `dig`, `payo`, `brahma`, `vy`, `kiM`). Rather than enumerate the sandhi
    rules, this asks the weaker, checkable question: do the two strings agree except
    at their tail, and are they the same length to within two characters? A genuine
    boundary move (`dvirada` vs `dvi`, `agnihotra` vs `agni`, `a` vs `akAma`) fails
    the length test; a genuine different word (`arha` vs `rha`) fails the prefix
    test; a derivation (`BU` vs `BAva`) fails the two-character agreement floor.
    """
    if fold(p) == fold(s):
        return True
    if abs(len(p) - len(s)) > 2:
        return False
    if glide_alt(p, s):
        return True
    fp, fs = p.translate(_RETRO), s.translate(_RETRO)
    common = 0
    for a, b in zip(fp, fs):
        if a != b:
            break
        common += 1
    if min(len(fp), len(fs)) <= 2:
        return False          # too short to tell a sandhi alternant from a new word
    return common >= 2 and common >= min(len(fp), len(fs)) - 2


def same_split(P, I):
    """Same arity and every member pairwise seam-compatible = one analysis, two
    spellings. This is a positional proxy for `the boundaries sit in the same place`:
    MW's members concatenate to the headword by construction, so equal arity plus a
    per-position lexeme↔surface correspondence pins the boundaries."""
    return len(P) == len(I) and all(seam_compatible(p, s) for p, s in zip(P, I))


# Taddhita / secondary suffixes: MW's last surface segment often carries the suffix
# that derives the WHOLE compound (agra + dAnin vs PWG's agra + dAna), and MW
# sometimes gives that suffix its own em-dash member (`sarva—veda—maya`). Either way
# the suffix is not a member of the compound — it applies to the compound.
SUFFIX_MEMBERS = frozenset((
    'maya', 'tA', 'tva', 'ka', 'kA', 'tas', 'in', 'ika', 'IkA', 'Ika', 'aka',
    'akA', 'ya', 'vat', 'mat', 'mant', 'vant', 'iya', 'Iya', 'la', 'ra'))


def suffix_of(longer, shorter):
    """`longer` = `shorter` + a known secondary suffix? -> the suffix, else None.

    Strictly longer, and the tail must be a suffix this repo already names — a bare
    final-vowel difference (`jihvA`/`jihva`) is a FORM difference, not a derivation,
    and must not be smuggled in here.
    """
    if len(longer) <= len(shorter):
        return None
    fp, fl = shorter.translate(_RETRO), longer.translate(_RETRO)
    if fl.startswith(fp):
        tail = fl[len(fp):]
        return tail if tail in SUFFIX_MEMBERS else None
    # stem-final vowel replaced by the suffix (mAtrA -> mAtrika, SreRi -> SreRya)
    if len(fp) > 2 and fl.startswith(fp[:-1]):
        tail = fl[len(fp) - 1:]
        return tail if tail in SUFFIX_MEMBERS else None
    return None


# ---------------------------------------------------------------- the rule ladder

APPROVE = 'pwg_members-right'
REJECT = 'index_members-right'
DEFER = 'unresolved'

# `pwg_toplevel` statuses that mean PWG's entry states NO member chain for this
# headword at all (as opposed to stating one this extractor could not resolve).
NO_CHAIN_FOR_HEADWORD = frozenset((
    'no_head', 'no_paren', 'paren_after_other_word', 'paren_after_article_text'))


def adjudicate(k1, P, I, Pstar, why, Istar, n_variants, attested, freq):
    """First rule that fires wins. Returns (verdict, rule, reason, extras).

    Order is deliberate: the four provenance defects come first, because a row whose
    shipped list does not faithfully report its own source is decided by that fact
    alone — no convention question arises. Only then do the convention rules run, on
    rows where BOTH shipped lists are what their dictionaries actually say.
    """
    ex = {}
    p_faithful = (Pstar is not None and P == Pstar)
    i_faithful = bool(Istar) and I == [s.replace('-', '') for s in Istar]
    ex['pwg_source_split'] = ' + '.join(Pstar) if Pstar else ''
    ex['mw_k2_first_variant'] = ' + '.join(Istar)
    ex['mw_k2_variants'] = n_variants

    # --- tier 1: provenance defects -----------------------------------------
    if not p_faithful and not i_faithful:
        return (DEFER, 'both_layers_defective',
                'neither shipped member list faithfully reports its own dictionary '
                '(PWG chain %s; MW k2 carries %d variants) — the row cannot be '
                'decided without repairing both extractors first'
                % (why or 'mismatch', n_variants), ex)
    if not p_faithful and i_faithful:
        if Pstar is None and why in NO_CHAIN_FOR_HEADWORD:
            return (REJECT, 'pwg_layer_no_headword_paren',
                    "PWG's entry states no member chain for this headword — the "
                    "shipped PWG members were lifted from a neighbouring chain (a "
                    "base word's own parenthesis or a citation run), so they analyse "
                    "a different word; MW's segmentation is faithful", ex)
        if Pstar is None:
            return (REJECT, 'pwg_layer_unparsed_chain',
                    "PWG's parenthesis does not resolve to a top-level member chain "
                    "(%s), so the shipped PWG members are unverifiable against the "
                    "source; MW's segmentation is faithful to its own <k2>" % why, ex)
        return (REJECT, 'pwg_layer_inner_chain',
                "the shipped PWG members are the INNER bracketed sub-analysis; PWG's "
                "own top-level chain for this headword is `%s` — the extractor's "
                "first-chain rule is not bracket-aware; MW's segmentation is faithful"
                % ' + '.join(Pstar), ex)
    if p_faithful and not i_faithful:
        if n_variants > 1:
            return (APPROVE, 'mw_variant_fusion',
                    "MW's <k2> lists %d `;`-separated variants (`%s`) and "
                    "mw_compounds.py strips the separator AND the space, fusing them "
                    "into a bogus member; PWG's chain is faithful to its source"
                    % (n_variants, ex['mw_k2_first_variant']), ex)
        return (APPROVE, 'mw_layer_unfaithful',
                "the shipped index members do not match MW's own <k2> segmentation "
                "(`%s`); PWG's chain is faithful to its source"
                % ex['mw_k2_first_variant'], ex)

    # --- tier 2: both faithful — a convention difference ---------------------
    fp, fi = [fold(x) for x in P], [fold(x) for x in I]
    hyphens = [s for s in Istar if '-' in s]
    ex['mw_hyphen_members'] = ' '.join(hyphens)
    p_all = all(m in attested for m in P)
    i_all = all(m in attested for m in I)
    ex['pwg_members_unattested'] = ', '.join(m for m in P if m not in attested)
    ex['index_members_unattested'] = ', '.join(m for m in I if m not in attested)

    # T2.0 — a PWG member that is not a word but IS one edit away from MW's attested
    # member is a typo in the SOURCE TEXT, not an analysis: `{#deva#} + {#sda#}` for
    # `sUda`, `{#eka#} + {#hasaM#}` for `haMsa`. The layer reports pwg.txt faithfully;
    # pwg.txt is wrong. Routed to the csl-orig correction queue, never patched here.
    if len(P) == len(I) and i_all and not p_all:
        typos = [(a, b) for a, b in zip(P, I)
                 if a != b and a not in attested and b in attested
                 and levenshtein(a, b) <= 2 and abs(len(a) - len(b)) <= 2
                 and not seam_compatible(a, b)]
        if typos and len(typos) == sum(1 for a, b in zip(P, I) if a != b):
            ex['pwg_typo_pairs'] = '; '.join('%s|%s' % t for t in typos)
            return (REJECT, 'pwg_member_typo_in_source',
                    'PWG\'s own text spells the member `%s` where the word is `%s` '
                    '(edit distance %d, unattested vs attested) — a transcription '
                    'typo in pwg.txt, so the shipped PWG members cannot be promoted'
                    % (typos[0][0], typos[0][1], levenshtein(*typos[0])), ex)

    # T2.1 — the tail carries a secondary suffix. Checked BEFORE the same-split rule:
    # `agra + dAna` vs `agra + dAnin` agrees on the cut, but the members are a lexeme
    # and that lexeme PLUS a suffix, which is a different claim from a spelling.
    if len(P) == len(I) and \
            all(seam_compatible(p, s) for p, s in zip(P[:-1], I[:-1])):
        suf = suffix_of(I[-1], P[-1])
        if suf and P[-1] in attested:
            ex['taddhita_suffix'] = suf
            return (APPROVE, 'pwg_lexeme_vs_mw_suffixed_tail',
                    "only the final member differs: PWG's `%s` is an attested "
                    "headword and MW's `%s` is that lexeme plus `-%s`, a suffix that "
                    "derives the WHOLE compound rather than being one of its members"
                    % (P[-1], I[-1], suf), ex)
        suf2 = suffix_of(P[-1], I[-1])
        if suf2 and I[-1] in attested and P[-1] not in attested:
            return (REJECT, 'mw_lexeme_vs_pwg_overlong_tail',
                    "only the final member differs and MW's `%s` is the attested "
                    "headword while PWG's `%s` is not" % (I[-1], P[-1]), ex)

    # T2.2 — same analysis, two spellings of the same members
    if same_split(P, I):
        diffs = [(a, b) for a, b in zip(P, I) if a != b]
        ex['form_diffs'] = '; '.join('%s|%s' % d for d in diffs)
        return (APPROVE, 'same_split_pwg_lemma_form',
                'both sources cut the word in the same place; the members differ '
                'only in form (%s) — MW spells each segment as it stands in the '
                'compound (sandhi applied), PWG names the lexeme behind it, which '
                'is what a member list is for' % ex['form_diffs'], ex)

    if len(P) == len(I):
        # T2.2b — MW's cut absorbs the member's initial vowel into the seam. MW's
        # segment is PWG's member minus its opening vowel (`akza` -> `kza`, `aSva` ->
        # `'Sva` with the avagraha still in the k2, `antya` -> `ntya`): the vowel was
        # eaten by sandhi with the preceding member, so MW's segment is a fragment of
        # the word PWG names.
        cut_pos = [j for j in range(len(P)) if not seam_compatible(P[j], I[j])]
        if len(cut_pos) == 1:
            j = cut_pos[0]
            p_m, i_m = P[j], I[j]
            if len(p_m) > len(i_m) and p_m.endswith(i_m) and p_m[0] in 'aAiIuUfeo':
                ex['absorbed_vowel'] = p_m[:len(p_m) - len(i_m)]
                return (APPROVE, 'mw_cut_absorbs_initial_vowel',
                        "MW's segment `%s` is PWG's member `%s` with its initial `%s` "
                        "eaten by sandhi at the seam — the fragment is not the word, "
                        "PWG names it" % (i_m, p_m, ex['absorbed_vowel']), ex)
            # mum-āgama: MW puts the linking nasal on the RIGHT of the boundary and
            # hyphenates it (`jala—M-gama`), PWG keeps the accusative (`jalam + gama`)
            if j > 0 and i_m.startswith('M') and P[j - 1].endswith('m'):
                return (APPROVE, 'mw_anusvara_right_of_boundary',
                        "MW puts the linking anusvāra on the right of the cut (`%s`, "
                        "hyphenated in its own <k2>) while PWG keeps it on the "
                        "accusative first member (`%s`) — MW's `%s` is not a word"
                        % (i_m, P[j - 1], i_m), ex)

        # T2.3 — the privative: PWG negates the whole, MW's hyphen negates member 1
        if P[0] == 'a' and any(s.startswith('a-') for s in Istar):
            return (DEFER, 'privative_scope_disputed',
                    "PWG makes the privative `a` a member of its own (negation over "
                    "the whole compound); MW's hyphen in `%s` binds it to the first "
                    "member only (negation over that member). The two readings are "
                    "different analyses of the same string, and nothing in either "
                    "entry settles which the store should carry"
                    % (hyphens[0] if hyphens else I[0]), ex)
        # T2.4 — MW's cut falls inside a vowel-sandhi seam, leaving a non-word
        if p_all and not i_all:
            return (APPROVE, 'mw_cut_leaves_nonword',
                    'the two segmentations differ and every PWG member is an '
                    'attested headword while MW\'s `%s` is not a word — MW cuts '
                    'inside a sandhi-fused seam (mahA+arha -> mahA|rha) or spells '
                    'the seam\'s surface form' % ex['index_members_unattested'], ex)
        if i_all and not p_all:
            return (REJECT, 'pwg_cut_leaves_nonword',
                    'the cut differs and every MW member is an attested headword '
                    'while PWG\'s `%s` is not' % ex['pwg_members_unattested'], ex)
        if p_all and i_all:
            return (DEFER, 'cut_moved_both_readings_lexical',
                    'the two sources cut the word in different places and BOTH '
                    'readings decompose into attested headwords (`%s` vs `%s`) — a '
                    'genuine lexicographic disagreement, not a notation difference'
                    % (' + '.join(P), ' + '.join(I)), ex)
        return (DEFER, 'cut_moved_neither_reading_lexical',
                'the cut differs and neither reading decomposes into attested '
                'headwords throughout', ex)

    # --- different arity ----------------------------------------------------
    # T2.5 — MW gives the deriving suffix its own member (sarva—veda—maya)
    if len(I) == len(P) + 1 and I[-1] in SUFFIX_MEMBERS and \
            all(seam_compatible(p, s) for p, s in zip(P, I[:-1])):
        ex['mw_suffix_member'] = I[-1]
        return (APPROVE, 'mw_splits_derivational_suffix',
                'MW gives `%s` its own member; it is a secondary suffix applied to '
                'the finished compound, not one of the words compounded' % I[-1], ex)
    if len(I) > len(P):
        merged_ok = _merges_to(fi, fp)
        ex['mw_is_finer'] = merged_ok
        if merged_ok:
            extra = [m for m in I if m not in attested]
            if p_all and extra:
                return (APPROVE, 'mw_splits_bound_morph',
                        'MW cuts the same string finer and its extra piece(s) `%s` '
                        'are not attested headwords, i.e. bound morphs, while every '
                        'PWG member is attested' % ', '.join(extra), ex)
            # MG's ruling, 30-07-2026 (H1918): a compound's vigraha is always binary
            # (a dvandva excepted, and a dvandva is never detectable from arity
            # alone — so this rule only fires where PWG's OWN list is length 2). An
            # n-member MW list past that point is not a competing arity for the
            # headword: it is the RECURSIVE decomposition, with the first member
            # analysed in turn (`goṣṭhīpati` = `goṣṭhī + pati`; MW's `go + ṣṭhī +
            # pati` is samāsa-within-samāsa, not a rival split of the headword).
            if len(P) == 2:
                return (APPROVE, 'mw_recursive_decomposition',
                        'MW lists %d members (`%s`) against PWG\'s binary vigraha '
                        '(`%s`) and they concatenate to the same string; a samāsa is '
                        'always binary (dvandva excepted), so MW\'s extra granularity '
                        'is the recursive decomposition of the first member, not a '
                        'competing arity for the headword itself'
                        % (len(I), ' + '.join(I), ' + '.join(P)), ex)
            return (DEFER, 'granularity_ic_vs_full_decomposition',
                    'MW decomposes a lexicalised member further (`%s` vs `%s`) and '
                    'every piece is an attested headword — immediate constituents vs '
                    'full decomposition is a convention choice, and neither entry '
                    'states which one this field wants'
                    % (' + '.join(I), ' + '.join(P)), ex)
    else:
        if _merges_to(fp, fi):
            ex['pwg_is_finer'] = True
            extra = [m for m in P if m not in attested]
            if i_all and extra:
                return (REJECT, 'pwg_splits_bound_morph',
                        'PWG cuts the same string finer and its extra piece(s) `%s` '
                        'are not attested headwords while every MW member is'
                        % ', '.join(extra), ex)
            return (DEFER, 'granularity_pwg_finer',
                    'PWG cuts the same string finer and every piece is an attested '
                    'headword — the same granularity choice, mirrored', ex)
    return (DEFER, 'arity_differs_no_alignment',
            'the two member lists have different arity and neither is a merge of the '
            'other, so they are not two spellings of one analysis', ex)


def _merges_to(finer, coarser):
    """Can `finer` be merged (adjacent, in order) into `coarser`? Fold-tolerant."""
    i = 0
    for c in coarser:
        acc = ''
        while i < len(finer) and len(acc) < len(c):
            acc += finer[i]
            i += 1
        if acc != c and not (acc.startswith(c[:max(1, len(c) - 1)]) and
                             abs(len(acc) - len(c)) <= 1):
            return False
    return i == len(finer)


# ---------------------------------------------------------------- strata / Wilson

MIN_STRATUM = 25       # same floor as adjudicate_p2.py — below this no interval helps


def wilson_lower(k, n, z=1.96):
    """Wilson score interval lower bound for k/n successes."""
    if n == 0:
        return 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return max(0.0, (centre - margin) / denom)


# ---------------------------------------------------------------- data loading

def read_tsv(path):
    with io.open(path, encoding='utf-8') as fh:
        for row in csv.DictReader(fh, delimiter='\t'):
            yield row


def mem(s):
    return [m.strip() for m in (s or '').split('+') if m.strip()]


def load_attested():
    """Union of PWG/MW/GRA <k1> headwords — the member-attestation evidence."""
    out = set()
    for fn in os.listdir(HWL_DIR):
        if re.match(r'^(PWG|MW|GRA)-unique-key1-\d+\.txt$', fn):
            with io.open(os.path.join(HWL_DIR, fn), encoding='utf-8') as fh:
                out |= {ln.strip() for ln in fh if ln.strip()}
    return out


def load_rows():
    """The 4,226 `differs` rows joined to the index + the L_id that produced each
    PWG member list (replicating pwg_derivation_layer.load_compound's precedence)."""
    lid_hom = {r['L_id']: (r['k1'], r['hom'])
               for r in read_tsv(os.path.join(SG_ROOT, 'data', 'pwg_lid_hom_map',
                                              'pwg_lid_hom_map.tsv'))}
    precise, byk1 = {}, {}
    for r in read_tsv(os.path.join(SG_ROOT, 'data', 'pwg_compound_split',
                                   'pwg_compound_splits.tsv')):
        kh = lid_hom.get(r.get('L_id', ''))
        members = mem(r['members_slp1'])
        if kh:
            precise.setdefault(kh, (r['L_id'], members))
        byk1.setdefault(r['headword_slp1'], (r['L_id'], members))
    idx = {(r['k1'], r['hom']): r for r in read_tsv(INDEX_TSV)}
    rows = []
    for r in read_tsv(DERIV_TSV):
        if (r.get('compound_status') or '').strip() != 'differs':
            continue
        kh = (r['k1'], r['hom'])
        got = precise.get(kh) or byk1.get(r['k1'])
        rows.append({
            'k1': r['k1'], 'hom': r['hom'],
            'P': mem(r['compound_members_pwg']),
            'I': mem((idx.get(kh) or {}).get('compound_members')),
            'L_id': got[0] if got else '',
            'panini_sutras': r.get('panini_sutras') or '',
            'deriv_suffix': r.get('deriv_suffix') or '',
        })
    return rows


def lock_path_for(sheet_id):
    return os.path.join(LOCK_DIR, sheet_id + '.lock.json')


def load_arm_ids(sheet_id):
    """A blind arm's card ids, from its committed lock. An unbound sheet yields an
    empty arm on purpose: votes cast on it cannot be validated, so it prices nothing
    and must not be counted as if it could."""
    path = lock_path_for(sheet_id)
    if not os.path.exists(path):
        return set()
    with io.open(path, encoding='utf-8') as fh:
        data = json.load(fh)
    return set(data.get('ids') or data.get('item_ids') or ())


def load_freq():
    out = {}
    for r in read_tsv(FREQ_TSV):
        try:
            out[r['k1_slp1']] = int(r['count_all'])
        except (KeyError, ValueError):
            continue
    return out


def load_sources(rows):
    """PWG entry bodies for the exact L_ids, and MW's first em-dash <k2> per k1."""
    want_lids = {r['L_id'] for r in rows if r['L_id']}
    want_k1 = {r['k1'] for r in rows}
    pwg = {}
    for L, k1, k2, body in entries(PWG_TXT):
        if L in want_lids:
            pwg[L] = body
    mw = {}
    for L, k1, k2, body in entries(MW_TXT):
        # mw_compounds.py keeps the first k1 record whose <k2> carries an em-dash
        if k1 in want_k1 and EMDASH in k2 and k1 not in mw:
            mw[k1] = k2
    return pwg, mw


# ---------------------------------------------------------------- strata + plan

def stratum_for(rule, k1, freq):
    """The RULE is the stratum, full stop.

    A first cut of this pass also banded the two largest rules by DCS frequency (the
    H1628 sheet's own stratifier). Measured against the existing 199-card arm that is
    strictly harmful: banding `same_split_pwg_lemma_form` splits its 140 arm cards
    into 74/25/23/18, and a 25-card arm cannot clear a 0.90 Wilson lower bound even
    if the human agrees with every card (max 0.867), so three of the four bands
    become unpriceable and ~1,400 rows lose any route to promotion. DCS frequency
    stays on every verdict row as a covariate; it is not a stratum.
    """
    return rule


def collapse(counts):
    """A stratum smaller than MIN_STRATUM cannot carry an interval, so it joins a
    single `residual-undersized` pool. Reported in the plan, never silent."""
    return {s: (s if n >= MIN_STRATUM else 'residual-undersized')
            for s, n in counts.items()}


# ---------------------------------------------------------------- selftest

def selftest():
    assert balanced_paren('({#a#} + {#b#}) x') == '({#a#} + {#b#})'
    assert balanced_paren('no paren') is None
    body = '{#akfttaruc#}¦ ({#akftta#} [<hom>3.</hom> {#a#} + {#kftta#} von {#kart#}] + {#ruc#}) <lex>adj.</lex>'
    assert pwg_toplevel(body)[0] == ['akftta', 'ruc'], pwg_toplevel(body)
    body2 = '{#agnizwut#}¦ ({#agni#} + {#stut#} von {#stu#}) <ls>P.</ls>'
    assert pwg_toplevel(body2)[0] == ['agni', 'stut']
    body3 = '{#aDikazAzwika#}¦ <lex>adj.</lex> von {#aDikazazwi#} ({#aDika#} + {#zazwi#})'
    assert pwg_toplevel(body3)[2] == 'paren_after_other_word'
    assert pwg_toplevel(body3)[2] in NO_CHAIN_FOR_HEADWORD
    # the paren need not touch `¦`; a derivation ladder is settled by surface coverage
    body4 = '{#BUsuta#}¦ 1〉 <lex>m.</lex> (<hom>2.</hom> {#BU#} + {#suta#})'
    assert pwg_toplevel(body4, 'BUsuta')[0] == ['BU', 'suta']
    body5 = '{#BAnumatin#}¦ (von {#BAnumant#} oder von {#BAnu#} + {#mati#})'
    assert pwg_toplevel(body5, 'BAnumatin')[0] == ['BAnu', 'mati']
    body6 = ('{#DvajAgravatI#}¦ (<lex>f.</lex> von {#DvajAgravant#} und dieses von '
             '{#Dvaja#} + {#agra#})')
    assert pwg_toplevel(body6, 'DvajAgravatI')[2] == 'ambiguous_no_unique_cover'
    v, segs = mw_variants('gaRa—kAri; gaRakAri')
    assert len(v) == 2 and segs == ['gaRa', 'kAri'], (v, segs)
    assert mw_variants('a/-kAma—karSana')[1] == ['a-kAma', 'karSana']
    assert fold('jihvA') == fold('jihva')
    assert fold('zwut') == fold('stut')
    assert fold('antar') == fold('antaH')
    assert suffix_of('dAnin', 'dAna') is not None
    # seam compatibility: a sandhi alternant folds, a moved boundary does not
    assert seam_compatible('sant', 'saj') and seam_compatible('payas', 'payo')
    assert seam_compatible('vi', 'vy') and seam_compatible('brahman', 'brahma')
    assert not seam_compatible('dvirada', 'dvi')
    assert not seam_compatible('arha', 'rha')
    assert not seam_compatible('a', 'akAma')
    assert not seam_compatible('BU', 'BAva')      # derivation, not a spelling
    assert same_split(['sant', 'jana'], ['saj', 'jana'])
    assert not same_split(['dvirada', 'arAti'], ['dvi', 'radArAti'])
    assert levenshtein('sda', 'sUda') == 1
    # a suffixed tail must NOT be read as a spelling difference, and vice versa
    assert suffix_of('dAnin', 'dAna') == 'in'
    assert suffix_of('karRaka', 'karRa') == 'ka'
    assert suffix_of('jihva', 'jihvA') is None
    v5 = adjudicate('agradAnin', ['agra', 'dAna'], ['agra', 'dAnin'],
                    ['agra', 'dAna'], 'ok', ['agra', 'dAnin'], 1,
                    {'agra', 'dAna', 'dAnin'}, {})
    assert v5[1] == 'pwg_lexeme_vs_mw_suffixed_tail', v5
    v6 = adjudicate('tArakAkza', ['tArakA', 'akza'], ['tArakA', 'kza'],
                    ['tArakA', 'akza'], 'ok', ['tArakA', 'kza'], 1,
                    {'tArakA', 'akza', 'kza'}, {})
    assert v6[1] == 'mw_cut_absorbs_initial_vowel', v6
    v7 = adjudicate('jalaMgama', ['jalam', 'gama'], ['jala', 'Mgama'],
                    ['jalam', 'gama'], 'ok', ['jala', 'M-gama'], 1,
                    {'jala', 'gama'}, {})
    assert v7[1] == 'mw_anusvara_right_of_boundary', v7
    # a sandhi alternant of an unlisted stem is NOT a typo (jIvant/jIvan)
    v8 = adjudicate('jIvanmfta', ['jIvant', 'mfta'], ['jIvan', 'mfta'],
                    ['jIvant', 'mfta'], 'ok', ['jIvan', 'mfta'],
                    1, {'jIvan', 'mfta'}, {})
    assert v8[1] != 'pwg_member_typo_in_source', v8
    assert _merges_to(['aMsa', 'tra', 'koSa'], ['aMsatra', 'koSa'])
    assert not _merges_to(['a', 'b'], ['xy'])
    # rule ladder on the four defect fixtures
    att = {'akftta', 'ruc', 'agni', 'stut', 'jihvA', 'jihva', 'gaRa', 'kAri'}
    v1 = adjudicate('akfttaruc', ['a', 'kftta'], ['akftta', 'ruc'], ['akftta', 'ruc'],
                    'ok', ['a-kftta', 'ruc'], 1, att, {})
    assert v1[0] == REJECT and v1[1] == 'pwg_layer_inner_chain', v1
    v2 = adjudicate('gaRakAri', ['gaRa', 'kAri'], ['gaRa', 'kArigaRakAri'],
                    ['gaRa', 'kAri'], 'ok', ['gaRa', 'kAri'], 2, att, {})
    assert v2[0] == APPROVE and v2[1] == 'mw_variant_fusion', v2
    v3 = adjudicate('agnijihva', ['agni', 'jihvA'], ['agni', 'jihva'], ['agni', 'jihvA'],
                    'ok', ['agni', 'jihva'], 1, att, {})
    assert v3[0] == APPROVE and v3[1] == 'same_split_pwg_lemma_form', v3
    v4 = adjudicate('aDikazAzwika', ['aDika', 'zazwi'], ['aDika', 'zAzwika'], None,
                    'no_paren', ['aDika', 'zAzwika'], 1, att, {})
    assert v4[0] == REJECT and v4[1] == 'pwg_layer_no_headword_paren', v4
    # H1918 — MG's binary-samasa ruling: MW's 3-member list is the RECURSIVE
    # decomposition of PWG's binary vigraha (goSWIpati = goSWI + pati; MW also
    # decomposes goSWI itself into go + SWI), so PWG's binary split wins.
    v9 = adjudicate('goSWIpati', ['goSWI', 'pati'], ['go', 'SWI', 'pati'],
                    ['goSWI', 'pati'], 'ok', ['go', 'SWI', 'pati'], 1,
                    {'goSWI', 'pati', 'go', 'SWI'}, {})
    assert v9[0] == APPROVE and v9[1] == 'mw_recursive_decomposition', v9
    # a genuine dvandva (PWG itself gives >2 members) must NOT be swept in here —
    # the rule only fires where PWG's OWN list is binary.
    v10 = adjudicate('aBgo', ['a', 'B', 'go'], ['a', 'B', 'g', 'o'],
                     ['a', 'B', 'go'], 'ok', ['a', 'B', 'g', 'o'], 1,
                     {'a', 'B', 'go', 'g', 'o'}, {})
    assert v10[1] == 'granularity_ic_vs_full_decomposition', v10
    assert abs(wilson_lower(9, 10) - 0.5958) < 0.01, wilson_lower(9, 10)
    assert wilson_lower(0, 0) == 0.0
    print('selftest OK — paren/bracket parser, MW variant split, member fold, '
          'suffix detector, merge alignment, 4 rule fixtures, Wilson bound')


# ---------------------------------------------------------------- main

def run(write=False):
    rows = load_rows()
    attested = load_attested()
    freq = load_freq()
    pwg, mw = load_sources(rows)
    print('rows %d · PWG entries %d · MW k2 %d · attested headwords %d'
          % (len(rows), len(pwg), len(mw), len(attested)), file=sys.stderr)

    verdicts = []
    for r in rows:
        Pstar, paren, why = (None, None, 'no_lid')
        if r['L_id'] and r['L_id'] in pwg:
            Pstar, paren, why = pwg_toplevel(pwg[r['L_id']], r['k1'])
        k2 = mw.get(r['k1'], '')
        variants, Istar = mw_variants(k2)
        verdict, rule, reason, ex = adjudicate(
            r['k1'], r['P'], r['I'], Pstar, why, Istar, len(variants), attested, freq)
        verdicts.append({
            'id': '%s~~h%s' % (r['k1'], r['hom']) if r['hom'] else r['k1'],
            'k1': r['k1'], 'hom': r['hom'], 'L_id': r['L_id'],
            'verdict': verdict, 'rule': rule, 'reason': reason,
            'pwg_members': ' + '.join(r['P']), 'index_members': ' + '.join(r['I']),
            'pwg_source_paren': (paren or '').replace('\t', ' ').replace('\n', ' '),
            'mw_k2_raw': k2,
            'pwg_source_split': ex.get('pwg_source_split', ''),
            'mw_first_variant': ex.get('mw_k2_first_variant', ''),
            'mw_variant_count': ex.get('mw_k2_variants', 0),
            'evidence': '; '.join('%s=%s' % (k, v) for k, v in sorted(ex.items())
                                  if k not in ('pwg_source_split', 'mw_k2_first_variant',
                                               'mw_k2_variants') and v not in ('', None)),
            'dcs_freq': freq.get(r['k1'], ''),
            'stratum_provisional': stratum_for(rule, r['k1'], freq),
        })

    prov = Counter(v['stratum_provisional'] for v in verdicts)
    final_of = collapse(prov)
    for v in verdicts:
        v['stratum'] = final_of[v['stratum_provisional']]

    by_verdict = Counter(v['verdict'] for v in verdicts)
    by_rule = Counter(v['rule'] for v in verdicts)
    by_stratum = Counter(v['stratum'] for v in verdicts)

    # --- the blind arms: which sampled cards land in which stratum
    ids_in_queue = {v['id'] for v in verdicts}
    arms = []
    for label, sheet_id in ARMS:
        ids = load_arm_ids(sheet_id)
        live = ids & ids_in_queue
        arms.append({
            'label': label, 'sheet_id': sheet_id, 'cards': len(ids),
            'cards_still_in_queue': len(live), 'cards_left_the_queue': len(ids - live),
            'bound': os.path.exists(lock_path_for(sheet_id)),
            '_by_stratum': Counter(v['stratum'] for v in verdicts if v['id'] in live),
        })
    arm = arms[0]['_by_stratum'] if arms else Counter()
    pooled = Counter()
    for a in arms:
        pooled.update(a['_by_stratum'])

    print('\nverdicts: %s' % dict(by_verdict))
    print('\nby rule:')
    for rule, n in by_rule.most_common():
        print('   %-42s %6d  %5.1f%%' % (rule, n, 100.0 * n / len(verdicts)))
    for a in arms:
        print('\n%s [%s]: %d cards, %d still in the queue%s'
              % (a['label'], 'bound' if a['bound'] else 'UNBOUND', a['cards'],
                 a['cards_still_in_queue'],
                 '' if not a['cards_left_the_queue']
                 else ', %d no longer `differs` (drawn before the extractor repairs)'
                 % a['cards_left_the_queue']))
    print('\n%d strata; per arm: cards / max Wilson-95 lb if that arm votes perfectly'
          % len(by_stratum))
    head = '   %-42s %7s' % ('stratum', 'rows')
    for a in arms:
        head += ' %14s' % a['label']
    print(head + ' %14s' % 'pooled')
    for s, n in by_stratum.most_common():
        line = '   %-42s %7d' % (s, n)
        for a in arms:
            c = a['_by_stratum'].get(s, 0)
            line += ' %6d %7s' % (c, ('%.3f' % wilson_lower(c, c)) if c else '—')
        p = pooled.get(s, 0)
        line += ' %6d %7s' % (p, ('%.3f' % wilson_lower(p, p)) if p else '—')
        print(line)

    if not write:
        return verdicts, by_stratum, arm, arms

    os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
    cols = ['id', 'k1', 'hom', 'L_id', 'verdict', 'rule', 'stratum', 'pwg_members',
            'index_members', 'pwg_source_split', 'mw_first_variant', 'mw_variant_count',
            'mw_k2_raw', 'pwg_source_paren', 'dcs_freq', 'evidence', 'reason']
    with io.open(OUT_TSV, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter='\t', extrasaction='ignore')
        w.writeheader()
        for v in sorted(verdicts, key=lambda x: (x['k1'], x['hom'])):
            w.writerow(v)

    def stratum_entry(s, n):
        e = {'stratum': s, 'rows': n, 'arms': {}}
        for a in arms:
            c = a['_by_stratum'].get(s, 0)
            e['arms'][a['sheet_id']] = {
                'cards': c,
                'max_wilson_lb_if_perfect': round(wilson_lower(c, c), 4),
                'can_promote_alone_if_perfect': wilson_lower(c, c) >= 0.90,
            }
        p = pooled.get(s, 0)
        e['pooled_cards'] = p
        e['pooled_max_wilson_lb_if_perfect'] = round(wilson_lower(p, p), 4)
        e['priceable'] = p >= 5
        # A stratum whose every row carries a human vote needs no interval at all:
        # there is nothing to extrapolate to. A small stratum can therefore be
        # promotable by CENSUS while its Wilson bound sits below the threshold.
        e['censused'] = p >= n
        e['promotable_at_threshold_if_arms_perfect'] = (
            e['censused'] or wilson_lower(p, p) >= 0.90)
        e['promotion_basis'] = ('census' if e['censused']
                                else ('wilson' if wilson_lower(p, p) >= 0.90 else 'none'))
        e['promoted_by'] = [a['sheet_id'] for a in arms
                            if e['arms'][a['sheet_id']]['can_promote_alone_if_perfect']]
        return e

    plan = {
        'handoff': 'H1703 (queue + arms) / H1681 (adjudicator)',
        'adjudicator': ADJUDICATOR,
        'generated': '26-07-2026',
        'queue_rows': len(verdicts),
        'queue_cards': len(ids_in_queue),
        'upstream_repairs_applied': [
            'SanskritGrammar#527 — pwg_compound_split.py headword-anchored + bracket-aware',
            'SanskritLexicography#801 — mw_compounds.py <k2> variant fusion',
        ],
        'blind_arms': [{k: v for k, v in a.items() if not k.startswith('_')}
                       for a in arms],
        'verdicts': dict(by_verdict),
        'by_rule': dict(by_rule),
        'gate': {
            'rule': 'per-stratum Wilson 95% lower bound on agent precision, measured '
                    'against the human vote of a blind arm. Each arm prices a stratum '
                    'on its own; `pooled` combines the arms, which is legitimate only '
                    'because they are disjoint random samples of the same strata.',
            'threshold': 0.90,
            'min_arm_cards': 5,
            'cards_needed_for_threshold': 35,
            'provenance_on_promotion': 'agent',
            'never': 'human_reviewed',
        },
        'strata': [stratum_entry(s, n) for s, n in by_stratum.most_common()],
    }
    plan['rows_in_priceable_strata'] = sum(
        s['rows'] for s in plan['strata'] if s['priceable'])
    plan['rows_promotable_if_arms_perfect'] = sum(
        s['rows'] for s in plan['strata'] if s['promotable_at_threshold_if_arms_perfect'])
    plan['rows_unpriceable'] = sum(
        s['rows'] for s in plan['strata'] if not s['priceable'])
    with io.open(OUT_PLAN, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('\nwrote %d verdicts -> %s' % (len(verdicts), OUT_TSV))
    print('wrote promotion plan -> %s' % OUT_PLAN)
    return verdicts, by_stratum, arm, arms


def main():
    args = sys.argv[1:]
    if '--selftest' in args:
        selftest()
        return
    run(write='--write' in args)


if __name__ == '__main__':
    main()
