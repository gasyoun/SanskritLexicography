"""ACC x NCC P2 -- agent adjudication of all 49,019 Tier C/D candidate rows.

Per H1657 (MG ruling B2, 26-07-2026): the Tier C/D sheet built on 09-07-2026 is
not votable by a human at any cadence (49,019 rows ~ 14 working days at a
sustained 1 s/row). MG's 09-07-2026 "full coverage, no sampling" ruling is NOT
reversed -- every row still gets a verdict. What changes is who casts it: this
script adjudicates all of them with cited evidence, and a human then votes a
stratified sample to measure THIS adjudicator's precision
(build_p2_spotcheck_sheet.py -> p2_precision_gate.py).

Every verdict carries the evidence it was decided on -- both catalogue entries
verbatim, the matched span, tier/score, the rule that fired, and a one-clause
reason -- so any row can be re-audited later without re-deriving it.

## The NCC match_key defect this adjudicator has to work around

`parse_ncc.py` computes its match_key as `slp1_simplify(to_slp1(iast))` on the
RAW NCC headword, which is capitalised ("Kalāpatattvārṇava"). `to_slp1` is
case-preserving and does not map uppercase IAST initials, so the capital
survives into the SLP1 string and `slp1_simplify` then reads it as a *different
SLP1 letter*: K = kh, G = gh, C = ch, J = jh, T = th, D = dh, P = ph, B = bh,
N = n(g), Y = n(y), R = n(.), E = ai, O = au. Non-ASCII capitals (Ś, Ī, Ā, ...)
are not transliterated at all and survive verbatim into the key.

Measured on the shipped data: 91,548 of 152,526 NCC keys (60.0%) are wrong.
Consequences for P1's tiering, both of which this script must handle:

  * PRECISION side -- 40,757 of Tier D's 43,666 rows (93.3%) are a genuinely
    EXACT title match that the inserted 'h' (or the n-fold) pushed to edit
    distance 1. They are Tier-A-grade matches wearing a Tier D label.
  * RECALL side -- where the corruption changes the FIRST letter (Rāmāyaṇa ->
    "namayana", Śiva- -> "śiva-"), P1's first-letter blocking never compared the
    pair at all, so no candidate row exists to adjudicate. Exact-key overlap is
    22,775 keys once repaired, against the 8,397 P1 measured. That is a P0/P1
    recall hole, out of scope here (H1657 non-goal: "re-running P1 matching"),
    reported in P2_AGENT_ADJUDICATION_REPORT.md and tracked separately.

This script does NOT rewrite crosswalk_candidates.jsonl.gz and does not re-tier
anything -- rows keep the tier P1 gave them. It only adjudicates them with a
correctly-derived key as evidence.

Usage:
    python HeadwordLists/works_catalogue/adjudicate_p2.py
"""
import sys
import os
import re
import json
import gzip
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get("SANSKRIT_UTIL_PY",
                                  r"C:/Users/user/Documents/GitHub/sanskrit-util/py"))
import sanskrit_util as su  # noqa: E402

ACC_JSONL = os.path.join(HERE, "acc.jsonl")
NCC_JSONL = os.path.join(HERE, "ncc.jsonl")
CANDIDATES = os.path.join(HERE, "crosswalk_candidates.jsonl.gz")
OUT_VERDICTS = os.path.join(HERE, "p2_agent_verdicts.jsonl.gz")
OUT_DECISIONS = os.path.join(HERE, "p2_agent_decisions.json")

TAG_RE = re.compile(r'<[^>]+>')
PARENTHETICAL_RE = re.compile(r'\([^)]*\)')

# ---------------------------------------------------------------- key repair

def ncc_key_repaired(iast):
    """The key parse_ncc.py would have produced had it case-folded first.

    Lower-casing the whole IAST headword before transliteration is safe: IAST
    uses case only to mark the start of a headword/proper noun, never to
    distinguish two different sounds. It is the capital that SLP1 reads as a
    different letter.
    """
    text = PARENTHETICAL_RE.sub('', iast).replace('_', '')
    return su.slp1_simplify(su.to_slp1(text.lower()))


def nasal_and_geminate_fold(key):
    """Tier B's fold, reused verbatim from build_works_crosswalk.py."""
    folded = key.replace('n', 'm')
    out, prev = [], None
    for ch in folded:
        if ch != prev:
            out.append(ch)
        prev = ch
    return ''.join(out)


# Sanskrit stem alternations that are the SAME title written two ways, not two
# titles: -naman/-nama (n-stem cited in stem vs nominative form), a final -n on
# an -an stem, and a bare final vowel-length difference already folded away by
# slp1_simplify.
STEM_TAILS = ("n",)


def stem_normalize(key):
    for t in STEM_TAILS:
        if key.endswith(t) and len(key) > len(t) + 3:
            return key[: -len(t)]
    return key


# ------------------------------------------------------------ body evidence

def clean_body(raw):
    text = raw.replace('\\n', ' ')
    text = TAG_RE.sub(' ', text)
    return re.sub(r'\s+', ' ', text).strip()


# A tolerant catalogue-citation shape: a capitalised siglum (optionally a
# multi-token one, optionally with a roman volume) followed by an accession or
# page number. Deliberately looser than parse_acc/parse_ncc's own SIGLUM_RE,
# which misses comma-separated forms ("Oudh XIX, 86") that are extremely common
# on the ACC side -- those misses are why the shipped `sigla` arrays intersect
# on only 260 of the 7,647 hard rows.
CIT_RE = re.compile(
    r"\b([A-ZĀĪŪŚṢṬḌṆṄÑṚ][A-Za-zĀāĪīŪūŚśṢṣṬṭḌḍṆṇṄṅÑñṚṛ.]{0,18})\.?\s*"
    r"(?:(?:[IVXL]+)\s*[.,]?\s*)?"
    r"(?:pp?\.\s*)?"
    r"(\d{1,6})\b"
)

# Sigla so generic that sharing one is not evidence of anything (they name a
# volume/page of the catalogue itself, or a ubiquitous series).
CIT_STOPWORDS = {"p", "pp", "vol", "no", "see", "cf", "comp", "c", "ib", "ibid",
                 "page", "extr", "fr", "inc", "a", "b", "i", "ii", "iii", "iv"}

# The two catalogues romanise a handful of library sigla differently. Without
# these aliases a genuinely shared witness reads as two different citations --
# ACC "Ulwar 2196" vs NCC "Alwar 2196" is the same Alwar manuscript.
SIGLUM_ALIASES = {
    "ulwar": "alwar", "radh": "rādh", "rgb": "rgb", "oudh": "oudh",
    "burnell": "burnell", "sg": "śg", "hz": "hz",
}


def citations(text):
    out = set()
    for m in CIT_RE.finditer(text):
        name = m.group(1).rstrip('.').lower()
        if not name or name in CIT_STOPWORDS or len(name) < 2:
            continue
        name = SIGLUM_ALIASES.get(name, name)
        out.add(f"{name} {m.group(2)}")
    return out


AUTHOR_RE = re.compile(
    r"\bby\s+([A-ZĀĪŪŚṢṬḌṆṄÑṚ][A-Za-zĀāĪīŪūŚśṢṣṬṭḌḍṆṇṄṅÑñṚṛ]+"
    r"(?:\s+[A-ZĀĪŪŚṢṬḌṆṄÑṚ][A-Za-zĀāĪīŪūŚśṢṣṬṭḌḍṆṇṄṅÑñṚṛ]+){0,2})"
)


def authors(text):
    out = set()
    for m in AUTHOR_RE.finditer(text):
        name = m.group(1).strip()
        # keep only the head word: catalogues differ on honorific tails
        # ("Raghunandana Ācāryaśiromaṇi" vs "Raghunandana Śiromaṇi")
        head = name.split()[0]
        if len(head) > 3:
            out.add(su.slp1_simplify(su.to_slp1(head.lower())))
    return out


PERSON_RE = re.compile(
    r"\b(pupil of|son of|father of|grandfather of|brother of|disciple of|"
    r"guru of|alias|poet\b|king\b|writer\b|a Śvetāmbara|Jaina monk|"
    r"Pāli writer|his pupil|wrote\b|flourished|cent\.|"
    r"of the \w+ family|composed in \d|nephew of|preceptor|his son)", re.I)
# NCC author entries list their works as `--Title` / `-C.` paragraphs.
WORKLIST_RE = re.compile(r"(?:^|\s)-{1,2}[A-ZĀĪŪŚṢṬḌṆ]")


def is_person(text):
    if PERSON_RE.search(text):
        return True
    return bool(WORKLIST_RE.search(text))


# Morphemes that make the longer title a DIFFERENT work -- a commentary on, or
# a critical apparatus over, the shorter one. Base text and commentary are two
# catalogue works and must not be crosswalked onto each other.
COMMENTARY_TAILS = (
    "tika", "tikka", "vrtti", "vrttika", "bhasya", "vyakhya", "vyakhyana",
    "dipika", "dipaka", "pradipika", "panjika", "tippani", "tippana",
    "vivarana", "vivrti", "subodhini", "bodhini", "candrika", "prakasika",
    "kaumudi", "manjari", "darpana", "tatparyatika", "sangraha", "samgraha",
    "khandana", "parisista", "anukramani",
)

# Morphemes where the longer title is usually the SAME text cited more fully
# (a ritual manual named either bare or with its procedure word). These get
# their own stratum rather than a confident verdict, because the class is
# genuinely mixed and only a human sample can price it.
MANUAL_TAILS = (
    "vidhi", "vidhana", "prayoga", "paddhati", "puja", "pujavidhi", "karma",
    "stotra", "kavaca", "mahatmya", "katha", "mantra", "yantra", "phala",
)


def tail_of(longer, shorter):
    return longer[len(shorter):] if longer.startswith(shorter) else None


# ------------------------------------------------------------------ ladder

def adjudicate(row, acc_ev, ncc_ev):
    """Return (decision, rule, reason, evidence_extras).

    First rule that fires wins. Order is deliberate: title identity is
    decisive and comes first; the person/commentary disqualifiers come before
    the corroboration rules, because a person entry or a commentary can easily
    share a citation with the work it is attached to.
    """
    ak = row['acc_match_key']
    nk = row['_ncc_key_fixed']
    ex = {}

    # --- title identity (decisive) ------------------------------------
    if ak == nk:
        return ('approve', 'exact_after_key_repair',
                'ACC key and the repaired NCC key are identical -- an exact '
                'title match that P1 mis-tiered on a corrupted NCC key',
                {'matched_span': ak})
    if nasal_and_geminate_fold(ak) == nasal_and_geminate_fold(nk):
        return ('approve', 'fold_after_key_repair',
                'repaired keys are equal under the nasal/geminate fold P1 '
                'already accepts as Tier B',
                {'matched_span': nasal_and_geminate_fold(ak)})
    if stem_normalize(ak) == stem_normalize(nk):
        return ('approve', 'stem_variant',
                'same title cited in stem vs nominative form (-an/-man stem)',
                {'matched_span': stem_normalize(ak)})

    longer, shorter = (nk, ak) if len(nk) > len(ak) else (ak, nk)
    tail = tail_of(longer, shorter)
    ex['prefix_tail'] = tail

    # --- disqualifiers -------------------------------------------------
    if acc_ev['person'] != ncc_ev['person']:
        side = 'NCC' if ncc_ev['person'] else 'ACC'
        return ('reject', 'person_vs_work',
                f'the {side} entry is a person (author/poet/king), not a work, '
                f'so the two entries are not the same catalogue object',
                ex)

    # Only a SHORT tail is "the same title plus a commentary word". A long tail
    # that merely happens to end in one (nyaya + kusumanjalikarikasamgraha) is a
    # substantively different title and belongs to the prefix-extension rule --
    # same verdict, but the reason has to name the real ground.
    if tail and (any(tail.startswith(t) for t in COMMENTARY_TAILS)
                 or (len(tail) <= 12
                     and any(tail.endswith(t) for t in COMMENTARY_TAILS))):
        return ('reject', 'commentary_extension',
                f'the longer title adds the commentary morpheme "{tail}" -- a '
                f'commentary is a different catalogue work from its base text',
                ex)

    shared_cit = acc_ev['cit'] & ncc_ev['cit']
    shared_auth = acc_ev['auth'] & ncc_ev['auth']
    ex['shared_citations'] = sorted(shared_cit)[:8]
    ex['shared_authors'] = sorted(shared_auth)[:4]

    if acc_ev['auth'] and ncc_ev['auth'] and not shared_auth:
        return ('reject', 'different_author',
                'both catalogues name an author and the names disagree',
                ex)

    # --- corroboration -------------------------------------------------
    if shared_cit:
        return ('approve', 'shared_citation',
                f'both entries cite the same manuscript witness '
                f'({", ".join(sorted(shared_cit)[:3])})',
                ex)
    if shared_auth and tail:
        return ('approve', 'same_author_prefix',
                'same author and one title is a proper extension of the other',
                ex)

    # --- unsupported ---------------------------------------------------
    if tail and any(tail.startswith(t) for t in MANUAL_TAILS):
        return ('reject', 'manual_extension_unsupported',
                f'the longer title adds the procedure word "{tail}" but no '
                f'shared witness or author corroborates the identification',
                ex)
    if row['tier'] == 'C':
        return ('reject', 'prefix_extension_unsupported',
                'prefix containment only -- the extra title segment is '
                'substantive and nothing else links the two entries',
                ex)
    return ('reject', 'edit_distance_unsupported',
            'the repaired titles still differ and no shared witness or author '
            'supports treating them as one work',
            ex)


# ------------------------------------------------------------------ strata

def score_band(tier, score):
    if tier == 'C':
        return 'c'
    if score >= 0.95:
        return 'hi'
    if score >= 0.88:
        return 'mid'
    return 'lo'


# Rules that fire on TITLE IDENTITY. For these the P1 score is not a property
# of the pair at all -- it is the edit distance between the ACC key and a
# CORRUPTED NCC key, i.e. a measure of how badly parse_ncc.py mangled the
# headword, not of how well the two works match. Banding these strata by score
# would stratify on noise, so tier alone carries them. Every other rule keeps
# its score band, where the score does measure real title divergence.
IDENTITY_RULES = {'exact_after_key_repair', 'fold_after_key_repair', 'stem_variant'}

# A stratum smaller than this cannot be measured usefully -- a census of 6 rows
# has a Wilson lower bound of 0.61 even at 6/6, so it would be held back for
# ever no matter how right the agent was. Undersized strata are pooled upward
# (band -> tier+rule -> rule) until they can carry an interval.
MIN_STRATUM = 25


def stratum_for(tier, rule, score):
    if rule in IDENTITY_RULES:
        return f"{tier}-{rule}"
    return f"{tier}-{rule}-{score_band(tier, score)}"


def collapse_map(provisional_counts, tier_rule_of):
    """provisional stratum -> final stratum, pooling anything undersized.

    Collapsing is done a WHOLE GROUP at a time, never band-by-band: if any
    score band of a tier+rule is too small to measure, all bands of that
    tier+rule merge into one stratum. Renaming just the small band would leave
    it small -- it has to actually join the larger rows to gain an interval.
    """
    by_tier_rule = defaultdict(list)
    for s in provisional_counts:
        by_tier_rule[tier_rule_of[s]].append(s)
    tier_rule_total = {tr: sum(provisional_counts[s] for s in ss)
                       for tr, ss in by_tier_rule.items()}

    by_rule = defaultdict(list)
    for tr in by_tier_rule:
        by_rule[tr.split('-', 1)[1]].append(tr)
    rule_total = {rule: sum(tier_rule_total[tr] for tr in trs)
                  for rule, trs in by_rule.items()}

    out = {}
    for tr, strata in by_tier_rule.items():
        rule = tr.split('-', 1)[1]
        bands_ok = all(provisional_counts[s] >= MIN_STRATUM for s in strata)
        if bands_ok:
            for s in strata:
                out[s] = s
        elif tier_rule_total[tr] >= MIN_STRATUM:
            for s in strata:
                out[s] = tr
        elif rule_total[rule] >= MIN_STRATUM:
            for s in strata:
                out[s] = f"{rule}-alltiers"
        else:
            for s in strata:
                out[s] = f"{rule}-residual"
    # A rule that had to pool across tiers must do so on BOTH sides, or the
    # large tier keeps a stratum the small tier was merged away from.
    for rule, trs in by_rule.items():
        targets = {out[s] for tr in trs for s in by_tier_rule[tr]}
        if f"{rule}-alltiers" in targets and len(targets) > 1:
            for tr in trs:
                for s in by_tier_rule[tr]:
                    out[s] = f"{rule}-alltiers"
    return out


def main():
    print("loading ACC/NCC bodies for evidence extraction ...", file=sys.stderr)
    acc_ev = {}
    with open(ACC_JSONL, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            body = r['body'] or ''
            acc_ev[r['acc_L']] = {
                'cit': citations(body) | {c.lower() for c in (r.get('sigla') or [])},
                'auth': authors(body),
                'person': is_person(body),
            }
    ncc_ev = {}
    with open(NCC_JSONL, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            body = clean_body(r['body_html'] or '')
            ncc_ev[r['ncc_id']] = {
                'cit': citations(body) | {c.lower() for c in (r.get('sigla') or [])},
                'auth': authors(body),
                'person': is_person(body),
            }
    print(f"  ACC {len(acc_ev):,} · NCC {len(ncc_ev):,}", file=sys.stderr)

    key_cache = {}
    rule_counts = Counter()
    decision_counts = Counter()
    stratum_counts = Counter()
    key_repaired_n = 0
    total = 0

    # --- pass 1: decide every row, so undersized strata can be pooled before
    # any of them is written. Only the compact decision tuple is kept; the
    # verbatim bodies are re-read from the candidate file in pass 2.
    print("pass 1/2: adjudicating ...", file=sys.stderr)
    decided = []
    provisional_counts = Counter()
    tier_rule_of = {}
    with gzip.open(CANDIDATES, 'rt', encoding='utf-8') as fin:
        for line in fin:
            r = json.loads(line)
            if r['tier'] not in ('C', 'D'):
                continue
            iast = r['ncc_iast']
            if iast not in key_cache:
                key_cache[iast] = ncc_key_repaired(iast)
            r['_ncc_key_fixed'] = key_cache[iast]
            ae = acc_ev.get(r['acc_L'], {'cit': set(), 'auth': set(), 'person': False})
            ne = ncc_ev.get(r['ncc_id'], {'cit': set(), 'auth': set(), 'person': False})
            out = adjudicate(r, ae, ne)
            prov = stratum_for(r['tier'], out[1], r['score'])
            provisional_counts[prov] += 1
            tier_rule_of[prov] = f"{r['tier']}-{out[1]}"
            decided.append((prov, out))

    final_of = collapse_map(provisional_counts, tier_rule_of)
    n_pooled = sum(n for s, n in provisional_counts.items() if final_of[s] != s)
    print(f"pass 1: {len(decided):,} rows · {len(provisional_counts)} provisional "
          f"strata · {n_pooled:,} rows pooled into a larger stratum",
          file=sys.stderr)

    print("pass 2/2: writing verdicts ...", file=sys.stderr)
    items = []
    idx = 0
    with gzip.open(CANDIDATES, 'rt', encoding='utf-8') as fin, \
            gzip.open(OUT_VERDICTS, 'wt', encoding='utf-8', newline='\n') as fout:
        for line in fin:
            r = json.loads(line)
            if r['tier'] not in ('C', 'D'):
                continue
            total += 1
            iast = r['ncc_iast']
            r['_ncc_key_fixed'] = key_cache[iast]
            if r['_ncc_key_fixed'] != r['ncc_match_key']:
                key_repaired_n += 1

            prov, (decision, rule, reason, extras) = decided[idx]
            idx += 1
            stratum = final_of[prov]
            rid = f"{r['acc_L']}__{r['ncc_id']}"

            rule_counts[rule] += 1
            decision_counts[decision] += 1
            stratum_counts[stratum] += 1

            verdict = {
                'id': rid,
                'acc_L': r['acc_L'],
                'ncc_id': r['ncc_id'],
                'tier': r['tier'],
                'score': r['score'],
                'decision': decision,
                'rule': rule,
                'reason': reason,
                'stratum': stratum,
                'evidence': {
                    'acc_match_key': r['acc_match_key'],
                    'ncc_match_key_p1': r['ncc_match_key'],
                    'ncc_match_key_repaired': r['_ncc_key_fixed'],
                    'ncc_key_was_corrupt': r['_ncc_key_fixed'] != r['ncc_match_key'],
                    'acc_k1_slp1': r['acc_k1_slp1'],
                    'ncc_iast': iast,
                    'ncc_deva': r['ncc_deva'],
                    'acc_body': r['acc_body'],
                    'ncc_body_html': r['ncc_body_html'],
                    **extras,
                },
            }
            fout.write(json.dumps(verdict, ensure_ascii=False) + '\n')
            items.append({'id': rid, 'decision': decision, 'note': f'agent:{rule}'})

    payload = {
        'sheet_id': 'sanskritlexicography-acc_ncc_p2_c_d_review',
        'generated': 'H1657 agent adjudication (ungated)',
        'decided': len(items),
        'adjudicator': 'adjudicate_p2.py (H1657, Opus 5 1M `claude-opus-5[1m]`)',
        'gated': False,
        'items': items,
    }
    with open(OUT_DECISIONS, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    print(f"\nadjudicated {total:,} Tier C/D rows -> {OUT_VERDICTS}")
    print(f"  NCC key was corrupt on {key_repaired_n:,} of them "
          f"({key_repaired_n / total:.1%})")
    print(f"  decisions: {dict(decision_counts)}")
    print("\n  by rule:")
    for rule, n in rule_counts.most_common():
        print(f"    {rule:34s} {n:7,}")
    print(f"\n  {len(stratum_counts)} strata; those with >=25 rows:")
    for s, n in sorted(stratum_counts.items(), key=lambda kv: -kv[1]):
        if n >= 25:
            print(f"    {s:52s} {n:7,}")
    print(f"\nungated decisions.json -> {OUT_DECISIONS}")


if __name__ == '__main__':
    main()
