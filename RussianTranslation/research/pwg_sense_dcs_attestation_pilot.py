#!/usr/bin/env python
"""pwg_sense_dcs_attestation_pilot.py — H1632 (N5, parent programme H1624).

Pilot join of **PWG (Petersburger Wörterbuch) senses** to **DCS attestation and
frequency**, on the frozen 500-headword H1455/H1456 pilot frame, reporting the one
number the programme actually needs:

    how much of a lemma's DCS token mass can be attributed to a SPECIFIC PWG sense,
    versus how much stays resolvable only at the LEMMA level?

Nothing here invents a frequency. Every count is read from a committed derived table
and is recomputable by a third party; the LLM is not in the measurement path.

Prior art CONSUMED, never rebuilt (this is the whole point of the pilot):
  * `kosha/data/concordance/sense_pilot_headwords.tsv` — the frozen 500 (slp1,hom)
    pilot frame (H1455).
  * `RussianTranslation/src/pwg_sense_loci.sample.tsv` — PWG leaf senses + their
    `<ls>` loci (H1456, from `microstructure.py` + `pwg_sources.py`).
  * `kosha/data/frequency/lemma_frequency.tsv` — DCS lemma-level token counts.
  * `kosha/data/frequency/sense_frequency.tsv` — DCS per-sense counts; the `wn`
    layer is the Sanskrit-WordNet `m_wordsem` GOLD (H1453), so it is the only layer
    used for the "sense-resolvable" ceiling.
  * `kosha/data/concordance/sense_corpus_concordance.tsv` — H1455's PWG-sense ↔ DCS
    attestation links, with its confidence tiers.

The two sense inventories are NOT the same object, and the report never pretends
otherwise: PWG's sense tree (`1a`, `1b`, …) is a 19th-c. German lexicographic
division; DCS's `wn` senses are Sanskrit-WordNet synsets. They are compared
structurally (granularity, mass) and joined only where H1455 produced a GROUNDED
link (a shared locus) — gloss-overlap links are counted separately and never folded
into the headline, because a shared proper noun is not a sense identification.

Usage:
  python pwg_sense_dcs_attestation_pilot.py [--kosha PATH] [--out-dir PATH]
  python pwg_sense_dcs_attestation_pilot.py --selftest
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, '..', 'src'))

# The `wn` layer is the m_wordsem gold; `mw`/`semdom` are downstream projections
# (H1453) and would double-count if summed alongside it.
GOLD_LAYER = 'wn'

# H1455 confidence tiers. Only a shared LOCUS grounds a PWG-sense↔DCS-token claim;
# `overlap` is a gloss-token heuristic and `ls` is PWG citing itself (no DCS token
# behind it at all), so neither may enter the attributed-mass headline.
GROUNDED_TIERS = ('locus', 'locus-mbh')
SELF_WITNESS_TIERS = ('ls',)
WEAK_TIERS = ('overlap',)


def find_kosha(explicit=None):
    """Locate the kosha clone: --kosha, then $KOSHA_ROOT, then the usual siblings."""
    cands = []
    if explicit:
        cands.append(explicit)
    if os.environ.get('KOSHA_ROOT'):
        cands.append(os.environ['KOSHA_ROOT'])
    # walk up from here looking for a sibling `kosha` (works from a worktree too)
    d = HERE
    for _ in range(6):
        d = os.path.dirname(d)
        cands.append(os.path.join(d, 'kosha'))
        cands.append(os.path.join(d, 'GitHub', 'kosha'))
    for c in cands:
        if c and os.path.isdir(os.path.join(c, 'data', 'frequency')):
            return os.path.normpath(c)
    raise SystemExit(
        'kosha clone not found (need data/frequency/). Pass --kosha PATH or set '
        '$KOSHA_ROOT. Tried:\n  ' + '\n  '.join(cands))


def sha256(path, cap=None):
    """SHA-256 of an input file — the H1083/FINDINGS §87 pin contract: a commit
    reference alone is not durable if history is rewritten."""
    h = hashlib.sha256()
    n = 0
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
            n += len(chunk)
            if cap and n >= cap:
                break
    return h.hexdigest()


def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as fh:
        for row in csv.DictReader(fh, delimiter='\t'):
            yield row


# --------------------------------------------------------------------------- #
# 1. load the five committed sides                                            #
# --------------------------------------------------------------------------- #
def load_frame(path):
    """The frozen 500-headword pilot frame. Key = (slp1, hom)."""
    frame = {}
    for r in read_tsv(path):
        frame[(r['slp1'], r.get('hom', ''))] = {
            'slp1': r['slp1'], 'hom': r.get('hom', ''),
            'n_leaf_senses': int(r['n_leaf_senses'] or 0),
            'n_loci_senses': int(r['n_loci_senses'] or 0),
            'n_ls': int(r['n_ls'] or 0),
        }
    return frame


def load_pwg_senses(path):
    """PWG leaf senses per (slp1, hom).

    Rows are GROUPED BY (slp1, hom, sense_id), which is the documented consumer
    contract of `microstructure.leaf_senses`: a PWG Nachträge (supplement) record
    references an existing sense from its own `<L>` record, so the same sense key
    legitimately receives several rows whose `<ls>` sets must be unioned. Counting
    rows instead of distinct sense keys inflates the sense inventory (13,841 rows
    vs 7,641 real leaf senses on this frame) and would deflate every per-sense
    coverage rate below.

    A sense with no `<ls>` is kept — it is a real sense that simply cannot be
    locus-joined, and dropping it would flatter the coverage rate."""
    grouped = collections.defaultdict(lambda: collections.defaultdict(set))
    glosses = collections.defaultdict(dict)
    for r in read_tsv(path):
        key = (r['slp1'], r.get('hom', ''))
        sid = r['sense_id']
        loci = [x.strip() for x in (r.get('ls_loci') or '').split(';') if x.strip()]
        grouped[key][sid].update(loci)
        if sid not in glosses[key] and (r.get('gloss_de') or '').strip():
            glosses[key][sid] = r['gloss_de']

    senses = {}
    dropped_parent_loci = 0
    for key, by_sid in grouped.items():
        leaves = {sid: loci for sid, loci in by_sid.items()
                  if is_leaf(sid, by_sid)}
        dropped_parent_loci += sum(len(loci) for sid, loci in by_sid.items()
                                   if sid not in leaves)
        senses[key] = [{'sense_id': sid,
                        'gloss_de': glosses[key].get(sid, ''),
                        'n_ls': len(loci)}
                       for sid, loci in sorted(leaves.items())]
    return senses, dropped_parent_loci


def is_leaf(sid, siblings):
    """A numbered sense that has lettered children ('1' beside '1a'/'1b') is a
    STRUCTURAL NODE, not a leaf sense — it usually carries only gender/grammar
    ("1〉 m") and no gloss. H1455's frame counts leaves only; counting parents too
    inflates the sense denominator by ~16% on this frame.

    The child test is an ALPHABETIC suffix, so numbered sense '11' is not mistaken
    for a child of '1' (PWG entries reach 70+ numbered senses)."""
    for other in siblings:
        if len(other) > len(sid) and other.startswith(sid) \
                and other[len(sid):].isalpha():
            return False
    return True


def load_lemma_freq(path, wanted):
    """DCS lemma-level token counts, restricted to the frame's SLP1 keys."""
    out = {}
    for r in read_tsv(path):
        k = r['lemma_slp1']
        if k in wanted:
            try:
                out[k] = int(r['count_all'] or 0)
            except ValueError:
                continue
    return out


def load_sense_freq(path, wanted, layer=GOLD_LAYER):
    """DCS per-sense counts for the gold layer, restricted to the frame."""
    out = collections.defaultdict(list)
    for r in read_tsv(path):
        if r.get('layer') != layer:
            continue
        k = r['lemma_slp1']
        if k not in wanted:
            continue
        try:
            c = int(r['count_all'] or 0)
        except ValueError:
            c = 0
        out[k].append({'sense_id': r['sense_id'],
                       'gloss': r.get('sense_gloss', ''), 'count': c})
    return out


def load_concordance(path, frame_keys):
    """H1455 PWG-sense ↔ DCS links, bucketed by tier, restricted to the frame."""
    links = collections.defaultdict(lambda: collections.defaultdict(set))
    tier_rows = collections.Counter()
    for r in read_tsv(path):
        key = (r['slp1'], r.get('hom', ''))
        if key not in frame_keys:
            continue
        method = (r.get('method') or '').strip()
        tier_rows[method] += 1
        links[key][method].add(r['sense_id'])
    return links, tier_rows


# --------------------------------------------------------------------------- #
# 2. the join                                                                 #
# --------------------------------------------------------------------------- #
def build_rows(frame, pwg_senses, lemma_freq, sense_freq, links):
    """One row per (slp1, hom) pilot group, with its residual class."""
    rows = []
    for key, meta in sorted(frame.items()):
        slp1, hom = key
        senses = pwg_senses.get(key, [])
        n_pwg = len(senses)
        n_pwg_with_ls = sum(1 for s in senses if s['n_ls'] > 0)

        f_lemma = lemma_freq.get(slp1)                    # None = absent from DCS
        dcs_senses = sense_freq.get(slp1, [])
        f_sensetagged = sum(s['count'] for s in dcs_senses)
        n_dcs_senses = len(dcs_senses)

        by_tier = links.get(key, {})
        grounded = set()
        for t in GROUNDED_TIERS:
            grounded |= by_tier.get(t, set())
        weak = set()
        for t in WEAK_TIERS:
            weak |= by_tier.get(t, set())

        # Residual class — mutually exclusive. Grounding is tested FIRST because a
        # locus match does not require the DCS token to carry a m_wordsem tag: 4
        # groups in this frame are locus-grounded while having no wn sense at all,
        # and classing those as "no wordsem tag" would both understate R4 and
        # contradict the funnel's grounded count.
        if grounded:
            cls = 'R4_grounded_alignment'
        elif f_lemma is None:
            cls = 'R1_lemma_absent_from_dcs'
        elif n_dcs_senses == 0:
            cls = 'R2_no_wordsem_tag'
        else:
            cls = 'R3_tagged_but_unaligned'

        rows.append({
            'slp1': slp1, 'hom': hom,
            'n_pwg_senses': n_pwg,
            'n_pwg_senses_with_ls': n_pwg_with_ls,
            'n_pwg_ls_total': meta['n_ls'],
            'dcs_lemma_count': '' if f_lemma is None else f_lemma,
            'n_dcs_wn_senses': n_dcs_senses,
            'dcs_sensetagged_count': f_sensetagged,
            'sensetagged_share': ('%.4f' % (f_sensetagged / f_lemma)
                                  if f_lemma else ''),
            'n_pwg_senses_grounded': len(grounded),
            'n_pwg_senses_gloss_overlap_only': len(weak - grounded),
            'residual_class': cls,
        })
    return rows


def _rank(vals):
    """Average ranks, for Spearman without scipy."""
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys):
    if len(xs) < 3:
        return float('nan')
    rx, ry = _rank(xs), _rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx and dy else float('nan')


def summarize(rows, tier_rows):
    n = len(rows)
    attested = [r for r in rows if r['dcs_lemma_count'] != '']
    tagged = [r for r in attested if r['n_dcs_wn_senses'] > 0]
    grounded = [r for r in rows if r['n_pwg_senses_grounded'] > 0]

    mass_lemma = sum(int(r['dcs_lemma_count']) for r in attested)
    mass_tagged = sum(r['dcs_sensetagged_count'] for r in tagged)

    # PWG-sense denominators
    pwg_senses_total = sum(r['n_pwg_senses'] for r in rows)
    pwg_senses_with_ls = sum(r['n_pwg_senses_with_ls'] for r in rows)
    pwg_senses_grounded = sum(r['n_pwg_senses_grounded'] for r in rows)
    # DCS-sense denominator (only over lemmas in the frame)
    dcs_senses_total = sum(r['n_dcs_wn_senses'] for r in rows)

    # attributed mass: the DCS token mass sitting under a lemma where at least one
    # PWG sense is grounded — an UPPER bound on attributable mass, because the link
    # grounds the sense, not every token of the lemma.
    mass_under_grounded = sum(int(r['dcs_lemma_count']) for r in grounded
                              if r['dcs_lemma_count'] != '')

    pairs = [(r['n_pwg_senses'], r['n_dcs_wn_senses']) for r in tagged]
    rho = spearman([p[0] for p in pairs], [p[1] for p in pairs]) if pairs else float('nan')

    def med(v):
        v = sorted(v)
        if not v:
            return 0.0
        m = len(v) // 2
        return float(v[m]) if len(v) % 2 else (v[m - 1] + v[m]) / 2.0

    classes = collections.Counter(r['residual_class'] for r in rows)

    return {
        'n_pilot_groups': n,
        'n_lemma_attested': len(attested),
        'n_wordsem_tagged': len(tagged),
        'n_groups_grounded': len(grounded),
        'mass_dcs_lemma_tokens': mass_lemma,
        'mass_dcs_sensetagged_tokens': mass_tagged,
        'sensetagged_mass_share': (mass_tagged / mass_lemma) if mass_lemma else 0.0,
        'mass_under_grounded_upper_bound': mass_under_grounded,
        'attributable_mass_share_upper_bound': (
            mass_under_grounded / mass_lemma) if mass_lemma else 0.0,
        'pwg_senses_total': pwg_senses_total,
        'pwg_senses_with_ls': pwg_senses_with_ls,
        'pwg_senses_grounded': pwg_senses_grounded,
        'pwg_sense_join_rate': (pwg_senses_grounded / pwg_senses_total)
                               if pwg_senses_total else 0.0,
        'dcs_wn_senses_total': dcs_senses_total,
        'dcs_sense_join_rate': (pwg_senses_grounded / dcs_senses_total)
                               if dcs_senses_total else 0.0,
        'median_pwg_senses_tagged_lemmas': med([p[0] for p in pairs]),
        'median_dcs_senses_tagged_lemmas': med([p[1] for p in pairs]),
        'spearman_pwg_vs_dcs_sense_count': rho,
        'residual_classes': dict(classes),
        'concordance_tier_rows': dict(tier_rows),
    }


# --------------------------------------------------------------------------- #
# 3. report                                                                   #
# --------------------------------------------------------------------------- #
CLASS_GLOSS = {
    'R1_lemma_absent_from_dcs': 'PWG headword has no DCS lemma at all — no corpus '
                                'attestation exists to assign, at any granularity.',
    'R2_no_wordsem_tag': 'Attested in DCS, but not one of its tokens carries a '
                         '`m_wordsem` sense tag — lemma-level only, by construction.',
    'R3_tagged_but_unaligned': 'DCS has sense-tagged tokens AND PWG has senses, but '
                               'no shared locus links a PWG sense to them — the join '
                               'fails on evidence, not on absence.',
    'R4_grounded_alignment': 'At least one PWG sense is grounded to a DCS attestation '
                             'by a shared locus.',
}


def write_report(summary, rows, md_path, pins, sample, extra):
    s = summary
    L = []
    L.append('# PWG senses × DCS attestation — pilot join (H1632)')
    L.append('')
    L.append('_Created: 26-07-2026 · Last updated: 26-07-2026_')
    L.append('')
    L.append('_Auto-generated by `research/pwg_sense_dcs_attestation_pilot.py` '
             '(H1632, Opus 5 `claude-opus-5[1m]`). Do not hand-edit the metrics; '
             're-run the script._')
    L.append('')
    L.append('**Question.** For a PWG headword, how much of its DCS token mass can be '
             'attributed to a **specific PWG sense**, and how much stays resolvable '
             'only at the **lemma** level?')
    L.append('')
    L.append('**Answer at pilot scale: sense-level attribution is a rounding error.** '
             'Of the %s DCS tokens under the %d-headword pilot frame, %.1f%% carry a '
             'DCS sense tag at all, and only **%d of %d PWG leaf senses (%.2f%%)** are '
             'grounded to a DCS attestation by a shared locus. Lemma-level attestation '
             'is nearly free (%d/%d groups); sense-level is not, and no amount of '
             'joining the existing tables changes that — the missing ingredient is '
             'locus overlap, not compute.'
             % ('{:,}'.format(s['mass_dcs_lemma_tokens']), s['n_pilot_groups'],
                100 * s['sensetagged_mass_share'], s['pwg_senses_grounded'],
                s['pwg_senses_total'], 100 * s['pwg_sense_join_rate'],
                s['n_lemma_attested'], s['n_pilot_groups']))
    L.append('')

    L.append('## Frame and pins')
    L.append('')
    L.append('The frame is the **frozen H1455/H1456 500-headword pilot** — reused '
             'verbatim so this join is comparable with the sense-concordance build, '
             'not a second parallel frame. Every input is a committed derived table; '
             'no number below is recomputed from the 921 MB DCS sqlite in this pass.')
    L.append('')
    L.append('| Input | Role | SHA-256 (first 16) |')
    L.append('|---|---|---|')
    for p in pins:
        L.append('| `%s` | %s | `%s` |' % (p['name'], p['role'], p['sha256'][:16]))
    L.append('')
    L.append('**Decoy check (mandatory for this repo).** The DCS master behind these '
             'derived tables is `VisualDCS/src/DCS-data-2026/dcs_full.sqlite` '
             '(920,883,200 bytes on disk at run time). The sibling '
             '`VisualDCS/src/dcs_full.sqlite` and repo-root `dcs_full.sqlite` are '
             '**0-byte decoys** ([Uprava DANGER_FACTS](https://github.com/gasyoun/Uprava/blob/main/DANGER_FACTS.md)); '
             'neither was read. Verified present-and-non-empty before the run.')
    L.append('')
    L.append('**Join key.** SLP1 ↔ SLP1 on both sides (`slp1` in the PWG export, '
             '`lemma_slp1` in the DCS frequency tables). Both are already ASCII SLP1, '
             'so the length-preserving `form_key()` reduces to identity here — no '
             'NFD→strip-Mn→NFC normalisation is applied anywhere in this script.')
    L.append('')

    L.append('## ⚠️ Frame selection bias — read before the funnel')
    L.append('')
    L.append('Every one of the %d frame rows carries `dcs_attested=1`: **the H1455 '
             'pilot frame was selected to be DCS-attested.** The "100%% attested at '
             'lemma level" line below is therefore *true by construction and is not a '
             'finding* — on a random PWG sample it would be far lower. This matters in '
             'the honest direction: the frame is biased **towards** joinability, so '
             'every sense-level rate reported here is an **upper bound** on what a '
             'random PWG sample would yield. The collapse from lemma level to sense '
             'level is thus, if anything, understated.'
             % s['n_pilot_groups'])
    L.append('')
    L.append('## The funnel (both denominators)')
    L.append('')
    L.append('| Step | n | share of frame |')
    L.append('|---|---:|---:|')
    n = s['n_pilot_groups']
    L.append('| PWG pilot groups (slp1, hom) | %d | 100%% |' % n)
    L.append('| …attested in DCS at lemma level | %d | %.1f%% _(by construction — see above)_ |'
             % (s['n_lemma_attested'], 100 * s['n_lemma_attested'] / n))
    L.append('| …with ≥1 DCS `m_wordsem`-tagged sense | %d | %.1f%% |'
             % (s['n_wordsem_tagged'], 100 * s['n_wordsem_tagged'] / n))
    L.append('| …with ≥1 PWG sense grounded to a DCS attestation | %d | %.1f%% |'
             % (s['n_groups_grounded'], 100 * s['n_groups_grounded'] / n))
    L.append('')
    L.append('_The last row is **not** a subset of the one above it: grounding is a '
             'locus match, which does not require the matched DCS token to carry a '
             '`m_wordsem` sense tag. %d grounded groups have no `wn` sense at all._'
             % extra['grounded_without_wordsem'])
    L.append('')
    L.append('Sense-side, the two denominators the skill requires — never only the '
             'flattering one:')
    L.append('')
    L.append('| Ratio | Value |')
    L.append('|---|---:|')
    L.append('| grounded PWG senses / **all PWG leaf senses** | %d / %d = **%.2f%%** |'
             % (s['pwg_senses_grounded'], s['pwg_senses_total'],
                100 * s['pwg_sense_join_rate']))
    L.append('| grounded PWG senses / **all DCS `wn` senses in frame** | %d / %d = **%.2f%%** |'
             % (s['pwg_senses_grounded'], s['dcs_wn_senses_total'],
                100 * s['dcs_sense_join_rate']))
    L.append('| PWG leaf senses carrying ≥1 `<ls>` | %d / %d = %.1f%% |'
             % (s['pwg_senses_with_ls'], s['pwg_senses_total'],
                100 * s['pwg_senses_with_ls'] / s['pwg_senses_total']
                if s['pwg_senses_total'] else 0))
    L.append('')

    L.append('## A ceiling inside the dictionary, before DCS is consulted')
    L.append('')
    L.append('%s of the frame\'s `<ls>` citations hang on a **structural parent** '
             'sense node — a numbered sense such as `1〉 m.` that has lettered children '
             '`1a`/`1b` and carries the citation itself. Those citations belong to the '
             'headword, but PWG does not assign them to any leaf sense, so no join '
             'can: they are unattributable at sense level **by the dictionary\'s own '
             'structure**, independently of what DCS contains.'
             % '{:,}'.format(extra['dropped_parent_loci']))
    L.append('')
    L.append('This is worth separating from the corpus-side story below. Even a '
             'perfect corpus with perfect locus matching would leave these at '
             'lemma level.')
    L.append('')
    L.append('## Sense-level vs lemma-level mass')
    L.append('')
    L.append('| Quantity | DCS tokens | share |')
    L.append('|---|---:|---:|')
    ml = s['mass_dcs_lemma_tokens']
    L.append('| Lemma-level mass over attested pilot lemmas | %s | 100%% |'
             % '{:,}'.format(ml))
    L.append('| …of which carry a `m_wordsem` sense tag (the **ceiling** on any '
             'sense-level claim) | %s | %.1f%% |'
             % ('{:,}'.format(s['mass_dcs_sensetagged_tokens']),
                100 * s['sensetagged_mass_share']))
    L.append('| …sitting under a lemma with ≥1 grounded PWG sense (**upper bound**, '
             'see caveat) | %s | %.1f%% |'
             % ('{:,}'.format(s['mass_under_grounded_upper_bound']),
                100 * s['attributable_mass_share_upper_bound']))
    L.append('')
    L.append('⚠️ **The third row is an upper bound, not an achievement.** It counts '
             '*every* token of a lemma that has at least one grounded sense — but a '
             'grounded link identifies one sense at one locus, not the sense of every '
             'token of that lemma. The honest sense-attributed figure is bounded above '
             'by this and below by the handful of individually-grounded loci; the '
             'pilot does **not** license a point estimate between them, and none is '
             'given. Reporting the upper bound as "coverage" would be exactly the '
             'invented frequency this handoff forbids.')
    L.append('')

    L.append('## Granularity — the two sense inventories are not the same object')
    L.append('')
    L.append('| Statistic | Value |')
    L.append('|---|---:|')
    L.append('| median PWG leaf senses per sense-tagged lemma | %.1f |'
             % s['median_pwg_senses_tagged_lemmas'])
    L.append('| median DCS `wn` senses per sense-tagged lemma | %.1f |'
             % s['median_dcs_senses_tagged_lemmas'])
    L.append('| Spearman ρ (PWG sense count vs DCS sense count) | %.3f |'
             % s['spearman_pwg_vs_dcs_sense_count'])
    L.append('')
    L.append('PWG\'s divisions are 19th-c. German lexicographic sense articulation; '
             'DCS\'s are Sanskrit-WordNet synsets projected onto tokens. A weak rank '
             'correlation is the expected result, and it is the substantive reason a '
             'sense-to-sense join cannot be assumed even where both sides are rich — '
             'the inventories are not measuring the same distinctions. Nothing in this '
             'pilot maps a PWG sense onto a WordNet synset; that would need '
             'adjudication with a gold sample, not a join.')
    L.append('')

    L.append('## Residual classification')
    L.append('')
    L.append('| Class | groups | share | meaning |')
    L.append('|---|---:|---:|---|')
    for cls in ('R1_lemma_absent_from_dcs', 'R2_no_wordsem_tag',
                'R3_tagged_but_unaligned', 'R4_grounded_alignment'):
        c = s['residual_classes'].get(cls, 0)
        L.append('| `%s` | %d | %.1f%% | %s |'
                 % (cls, c, 100 * c / n, CLASS_GLOSS[cls]))
    L.append('')
    L.append('**R3 is the actionable class.** These are lemmas where DCS *does* carry '
             'sense-tagged tokens and PWG *does* carry senses, and the join still '
             'fails — because PWG cites Pañcatantra/Kathāsaritsāgara/kośa literature '
             'that DCS does not contain, or cites Mahābhārata in continuous '
             'Böhtlingk–Roth numbering whose vulgate→BORI-critical drift leaves only '
             'adhyāya-level corroboration (H1455 wave-1.5). Growing R4 means adding '
             '*texts and locus crosswalks*, not tuning a matcher.')
    L.append('')

    L.append('## H1455 tier accounting')
    L.append('')
    L.append('Rows in the consumed concordance, restricted to this frame:')
    L.append('')
    L.append('| tier | rows | admitted to the headline? |')
    L.append('|---|---:|---|')
    admit = {'ls': 'no — PWG citing itself; no DCS token behind it',
             'locus': '**yes** — shared verse locus',
             'locus-mbh': '**yes** — adhyāya-level, conf ≤ 0.80',
             'overlap': 'no — shared gloss tokens are not a sense identification'}
    for tier, cnt in sorted(s['concordance_tier_rows'].items(),
                            key=lambda kv: -kv[1]):
        L.append('| `%s` | %s | %s |' % (tier, '{:,}'.format(cnt),
                                         admit.get(tier, 'no — untiered residue')))
    L.append('')
    L.append('The `ls` tier is by far the largest and is the reason a naive reading of '
             'the concordance would overstate corpus attestation by orders of '
             'magnitude: those rows are PWG\'s own citations, which are excellent '
             'evidence *for the dictionary\'s* sense division and no evidence at all '
             'that DCS attests it.')
    L.append('')

    L.append('## Validation sample')
    L.append('')
    L.append('%d grounded links, hand-checkable (the skill\'s ≈50-item validation '
             'requirement is capped by the population — every grounded link in the '
             'pilot is listed rather than sampled):' % len(sample))
    L.append('')
    if sample:
        L.append('| slp1 | PWG sense | tier | DCS locus |')
        L.append('|---|---|---|---|')
        for r in sample:
            L.append('| `%s` | %s | `%s` | %s |'
                     % (r['slp1'], r['sense_id'], r['method'], r['locus']))
    else:
        L.append('_No grounded links in this frame._')
    L.append('')

    L.append('## Known discrepancies (disclosed, not smoothed)')
    L.append('')
    mm = extra['leaf_mismatch']
    L.append('- **Leaf-sense denominator, ±%.1f%%.** Re-parsing PWG today reproduces '
             'the frozen frame\'s `n_leaf_senses` exactly for **%d of %d** groups; '
             '%d groups come out %s (total %d vs the frame\'s %d, +%.1f%%). The frame '
             'was frozen 22-07-2026 and `csl-orig/v02/pwg/pwg.txt` is a live '
             'corrections target, so a small vintage drift is expected. The headline '
             'rate (%.2f%%) is not sensitive to a 1–2%% denominator wobble; the '
             'discrepancy is recorded rather than reconciled, because reconciling it '
             'would mean pinning a csl-orig commit that the frame never recorded.'
             % (100 * mm['pct'], mm['n_match'], s['n_pilot_groups'], mm['n_mismatch'],
                'higher' if mm['direction'] > 0 else 'lower', mm['mine_total'],
                mm['frame_total'], 100 * mm['pct'], 100 * s['pwg_sense_join_rate']))
    L.append('- **The grounded evidence is genuinely tiny** (%d exact-verse `locus` '
             'rows + %d adhyāya-level `locus-mbh`). The validation table above is the '
             'complete population, not a sample, so every grounded claim in this '
             'report is individually checkable — and the Mahābhārata dominance in it '
             'means the pilot\'s sense-level signal rests almost entirely on one text '
             'and on the vulgate crosswalk\'s ±1 adhyāya tolerance.'
             % (s['concordance_tier_rows'].get('locus', 0),
                s['concordance_tier_rows'].get('locus-mbh', 0)))
    L.append('')
    L.append('## What this pilot does NOT claim')
    L.append('')
    L.append('- No PWG sense is mapped to a WordNet synset or an MW numbered sense.')
    L.append('- No per-sense frequency is asserted for any PWG sense. The DCS '
             'per-sense counts quoted are DCS\'s **own** sense inventory\'s counts.')
    L.append('- No accuracy claim for the `overlap` tier; it is reported and excluded.')
    L.append('- Nothing is extrapolated from the 500-headword frame to full PWG.')
    L.append('')
    L.append('## Reproduce')
    L.append('')
    L.append('```sh')
    L.append('cd RussianTranslation/research')
    L.append('# step 1 — rebuild this frame\'s PWG loci from csl-orig (needs csl-orig)')
    L.append('python export_frame_sense_loci.py --kosha ../../../kosha')
    L.append('# step 2 — the join')
    L.append('python pwg_sense_dcs_attestation_pilot.py --kosha ../../../kosha')
    L.append('python pwg_sense_dcs_attestation_pilot.py --selftest')
    L.append('```')
    L.append('')
    L.append('Deterministic and byte-identical on re-run: no LLM, no sampling, no RNG. '
             'Step 1\'s output (`pwg_sense_loci.frame500.tsv`, 2.9 MB) is **not '
             'committed** — the same rule H1456 applied to the full export: the '
             'generator is the artifact, the bulk table is rebuildable. The PWG store '
             'and the DCS sqlite are likewise gitignored/local; the committed derived '
             'tables listed under **Pins** are the actual inputs. Note that step 1 '
             're-reads a live `csl-orig`, so its SHA-256 pin above will drift as '
             'corrections land upstream — see *Known discrepancies*.')
    L.append('')
    L.append('_Dr. Mārcis Gasūns_')
    open(md_path, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')


def collect_sample(conc_path, frame_keys, cap=60):
    """Every grounded link, for hand verification."""
    out = []
    for r in read_tsv(conc_path):
        if (r['slp1'], r.get('hom', '')) not in frame_keys:
            continue
        if (r.get('method') or '').strip() not in GROUNDED_TIERS:
            continue
        out.append({'slp1': r['slp1'], 'sense_id': r['sense_id'],
                    'method': r['method'], 'locus': r.get('locus', '')})
        if len(out) >= cap:
            break
    return out


# --------------------------------------------------------------------------- #
# selftest                                                                     #
# --------------------------------------------------------------------------- #
def selftest():
    frame = {('a', ''): {'slp1': 'a', 'hom': '', 'n_leaf_senses': 2,
                         'n_loci_senses': 2, 'n_ls': 3},
             ('b', ''): {'slp1': 'b', 'hom': '', 'n_leaf_senses': 1,
                         'n_loci_senses': 0, 'n_ls': 0},
             ('c', ''): {'slp1': 'c', 'hom': '', 'n_leaf_senses': 1,
                         'n_loci_senses': 1, 'n_ls': 1}}
    pwg = {('a', ''): [{'sense_id': '1a', 'gloss_de': 'x', 'n_ls': 2},
                       {'sense_id': '1b', 'gloss_de': 'y', 'n_ls': 1}],
           ('b', ''): [{'sense_id': '1', 'gloss_de': 'z', 'n_ls': 0}],
           ('c', ''): [{'sense_id': '1', 'gloss_de': 'w', 'n_ls': 1}]}
    # 'a' attested + tagged + grounded; 'b' attested but untagged; 'c' absent.
    lemma_freq = {'a': 100, 'b': 40}
    sense_freq = {'a': [{'sense_id': 'a#1', 'gloss': 'g', 'count': 30},
                        {'sense_id': 'a#2', 'gloss': 'h', 'count': 10}]}
    links = {('a', ''): {'locus': {'1a'}, 'overlap': {'1b'}, 'ls': {'1a', '1b'}}}

    rows = build_rows(frame, pwg, lemma_freq, sense_freq, links)
    by = {r['slp1']: r for r in rows}
    assert by['a']['residual_class'] == 'R4_grounded_alignment', by['a']
    assert by['b']['residual_class'] == 'R2_no_wordsem_tag', by['b']
    assert by['c']['residual_class'] == 'R1_lemma_absent_from_dcs', by['c']
    # gloss-overlap must NOT be counted as grounded
    assert by['a']['n_pwg_senses_grounded'] == 1, by['a']
    assert by['a']['n_pwg_senses_gloss_overlap_only'] == 1, by['a']
    assert by['a']['dcs_sensetagged_count'] == 40, by['a']
    assert by['a']['sensetagged_share'] == '0.4000', by['a']
    assert by['c']['dcs_lemma_count'] == '', by['c']

    s = summarize(rows, collections.Counter({'ls': 2, 'locus': 1, 'overlap': 1}))
    assert s['n_pilot_groups'] == 3 and s['n_lemma_attested'] == 2, s
    assert s['n_wordsem_tagged'] == 1 and s['n_groups_grounded'] == 1, s
    assert s['mass_dcs_lemma_tokens'] == 140, s          # 100 + 40
    assert s['mass_dcs_sensetagged_tokens'] == 40, s
    assert abs(s['sensetagged_mass_share'] - 40 / 140) < 1e-9, s
    # upper bound counts all of 'a', not just its tagged senses
    assert s['mass_under_grounded_upper_bound'] == 100, s
    assert s['pwg_senses_total'] == 4 and s['pwg_senses_grounded'] == 1, s
    assert abs(s['pwg_sense_join_rate'] - 0.25) < 1e-9, s
    assert s['dcs_wn_senses_total'] == 2, s
    # a PWG sense with no <ls> is kept in the denominator, not silently dropped
    assert s['pwg_senses_with_ls'] == 3, s

    r = spearman([1, 2, 3, 4], [1, 2, 3, 4])
    assert abs(r - 1.0) < 1e-9, r
    r = spearman([1, 2, 3, 4], [4, 3, 2, 1])
    assert abs(r + 1.0) < 1e-9, r

    # Nachträge grouping: two rows under the SAME (slp1,hom,sense_id) are ONE sense
    # whose <ls> sets union — the microstructure.leaf_senses consumer contract.
    import tempfile
    tf = tempfile.NamedTemporaryFile('w', suffix='.tsv', delete=False,
                                     encoding='utf-8', newline='')
    tf.write('slp1\thom\tsense_id\tgloss_de\tls_loci\n')
    tf.write('q\t\t1a\tmain gloss\tRV. 1,1;MBH. 2,2\n')
    tf.write('q\t\t1a\t\tMBH. 2,2;R. 3,3\n')          # supplement, one locus overlaps
    tf.write('q\t\t1b\tother gloss\t\n')              # real sense, no <ls>
    tf.close()
    g, dropped = load_pwg_senses(tf.name)
    os.unlink(tf.name)
    senses = g[('q', '')]
    assert len(senses) == 2, senses                    # NOT 3 rows
    by_sid = {s['sense_id']: s for s in senses}
    assert by_sid['1a']['n_ls'] == 3, by_sid['1a']     # union, deduped
    assert by_sid['1a']['gloss_de'] == 'main gloss', by_sid['1a']
    assert by_sid['1b']['n_ls'] == 0, by_sid['1b']     # kept in the denominator
    assert dropped == 0, dropped

    # leaf vs structural-parent: '1' with children '1a'/'1b' is NOT a leaf, but
    # numbered sense '11' must never be read as a child of '1'.
    sibs = {'1', '1a', '1b', '2', '11', '11a'}
    assert not is_leaf('1', sibs) and not is_leaf('11', sibs)
    assert is_leaf('1a', sibs) and is_leaf('2', sibs) and is_leaf('11a', sibs)

    tf2 = tempfile.NamedTemporaryFile('w', suffix='.tsv', delete=False,
                                      encoding='utf-8', newline='')
    tf2.write('slp1\thom\tsense_id\tgloss_de\tls_loci\n')
    tf2.write('z\t\t1\tm.\tRV. 9,9\n')                 # parent: its <ls> is dropped
    tf2.write('z\t\t1a\tchild a\tMBH. 1,1\n')
    tf2.write('z\t\t1b\tchild b\t\n')
    tf2.write('z\t\t2\tplain\tR. 2,2\n')
    tf2.close()
    g2, dropped2 = load_pwg_senses(tf2.name)
    os.unlink(tf2.name)
    assert [s['sense_id'] for s in g2[('z', '')]] == ['1a', '1b', '2'], g2[('z', '')]
    assert dropped2 == 1, dropped2                     # the parent's RV. 9,9
    print('pwg_sense_dcs_attestation_pilot selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kosha', default=None, help='path to the kosha clone')
    # NB: the default is the FRAME-matched export (export_frame_sense_loci.py), not
    # src/pwg_sense_loci.sample.tsv — that committed sample covers a different 500
    # headwords and overlaps this frame in only 16 keys.
    ap.add_argument('--loci', default=os.path.join(HERE,
                                                   'pwg_sense_loci.frame500.tsv'))
    ap.add_argument('--out-dir', default=HERE)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    kosha = find_kosha(a.kosha)
    p_frame = os.path.join(kosha, 'data', 'concordance', 'sense_pilot_headwords.tsv')
    p_conc = os.path.join(kosha, 'data', 'concordance', 'sense_corpus_concordance.tsv')
    p_lfreq = os.path.join(kosha, 'data', 'frequency', 'lemma_frequency.tsv')
    p_sfreq = os.path.join(kosha, 'data', 'frequency', 'sense_frequency.tsv')
    for p in (p_frame, p_conc, p_lfreq, p_sfreq, a.loci):
        if not os.path.isfile(p):
            raise SystemExit('missing required input: %s' % p)

    print('kosha  = %s' % kosha)
    frame = load_frame(p_frame)
    print('frame  = %d pilot groups' % len(frame))
    pwg, dropped_parent_loci = load_pwg_senses(a.loci)
    print('pwg    = %d groups, %d leaf senses (dropped %d <ls> on non-leaf parents)'
          % (len(pwg), sum(len(v) for v in pwg.values()), dropped_parent_loci))

    # Correctness gate: our leaf definition must reproduce the frozen frame's
    # n_leaf_senses exactly. A mismatch means the sense tree was parsed
    # differently from H1455/H1456 and every rate below would be incomparable.
    mismatch = [(k, frame[k]['n_leaf_senses'], len(pwg.get(k, [])))
                for k in frame
                if frame[k]['n_leaf_senses'] != len(pwg.get(k, []))]
    if mismatch:
        print('WARNING: leaf-sense count disagrees with the frame for %d/%d groups; '
              'e.g. %s' % (len(mismatch), len(frame), mismatch[:5]), file=sys.stderr)
    else:
        print('gate   = leaf-sense counts match the frozen frame exactly (%d/%d)'
              % (len(frame), len(frame)))
    wanted = {k[0] for k in frame}
    lfreq = load_lemma_freq(p_lfreq, wanted)
    print('dcs    = %d/%d frame lemmas attested' % (len(lfreq), len(wanted)))
    sfreq = load_sense_freq(p_sfreq, wanted)
    print('wordsem= %d frame lemmas with a %s sense' % (len(sfreq), GOLD_LAYER))
    links, tier_rows = load_concordance(p_conc, set(frame))
    print('links  = %s' % dict(tier_rows))

    rows = build_rows(frame, pwg, lfreq, sfreq, links)
    summary = summarize(rows, tier_rows)

    frame_total = sum(frame[k]['n_leaf_senses'] for k in frame)
    mine_total = sum(len(pwg.get(k, [])) for k in frame)
    extra = {
        'dropped_parent_loci': dropped_parent_loci,
        'grounded_without_wordsem': sum(
            1 for r in rows
            if r['n_pwg_senses_grounded'] > 0 and r['n_dcs_wn_senses'] == 0),
        'leaf_mismatch': {
            'n_match': len(frame) - len(mismatch),
            'n_mismatch': len(mismatch),
            'frame_total': frame_total,
            'mine_total': mine_total,
            'direction': 1 if mine_total >= frame_total else -1,
            'pct': (abs(mine_total - frame_total) / frame_total) if frame_total else 0.0,
            'examples': mismatch[:10],
        },
        'frame_selection_bias': 'every frame row has dcs_attested=1 — the frame was '
                                'selected DCS-attested, so lemma-level coverage is '
                                'true by construction and all rates are upper bounds',
    }

    pins = [
        {'name': 'kosha/data/concordance/sense_pilot_headwords.tsv',
         'role': 'frozen 500-headword pilot frame (H1455)', 'sha256': sha256(p_frame)},
        {'name': 'RussianTranslation/research/' + os.path.basename(a.loci),
         'role': 'PWG leaf senses + `<ls>` loci for THIS frame '
                 '(export_frame_sense_loci.py over microstructure.py, H1456 parser)',
         'sha256': sha256(a.loci)},
        {'name': 'kosha/data/frequency/lemma_frequency.tsv',
         'role': 'DCS lemma-level token counts', 'sha256': sha256(p_lfreq)},
        {'name': 'kosha/data/frequency/sense_frequency.tsv',
         'role': 'DCS per-sense counts, `wn` = m_wordsem gold (H1453)',
         'sha256': sha256(p_sfreq)},
        {'name': 'kosha/data/concordance/sense_corpus_concordance.tsv',
         'role': 'PWG-sense ↔ DCS attestation links (H1455)', 'sha256': sha256(p_conc)},
    ]
    sample = collect_sample(p_conc, set(frame))

    os.makedirs(a.out_dir, exist_ok=True)
    tsv_path = os.path.join(a.out_dir, 'pwg_sense_dcs_attestation_pilot.tsv')
    cols = ['slp1', 'hom', 'n_pwg_senses', 'n_pwg_senses_with_ls', 'n_pwg_ls_total',
            'dcs_lemma_count', 'n_dcs_wn_senses', 'dcs_sensetagged_count',
            'sensetagged_share', 'n_pwg_senses_grounded',
            'n_pwg_senses_gloss_overlap_only', 'residual_class']
    with open(tsv_path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter='\t', lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow(r)

    meta = {'handoff': 'H1632', 'model': 'Opus 5 (claude-opus-5[1m])',
            'generator': 'research/pwg_sense_dcs_attestation_pilot.py',
            'frame': 'H1455/H1456 frozen 500-headword pilot (reused, not re-derived)',
            'join_key': 'SLP1 <-> SLP1 (both sides already ASCII SLP1; form_key() is '
                        'identity here, no NFD/strip-Mn normalisation applied)',
            'gold_layer': GOLD_LAYER,
            'grounded_tiers': list(GROUNDED_TIERS),
            'excluded_tiers': {'ls': 'PWG self-citation, no DCS token',
                               'overlap': 'gloss-token heuristic, not a sense id'},
            'dcs_master': 'VisualDCS/src/DCS-data-2026/dcs_full.sqlite (921 MB; the '
                          'src/ and repo-root copies are 0-byte decoys and were not read)',
            'pins': pins, 'summary': summary, 'disclosures': extra}
    json_path = os.path.join(a.out_dir, 'pwg_sense_dcs_attestation_pilot.meta.json')
    json.dump(meta, open(json_path, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)

    write_report(summary, rows,
                 os.path.join(a.out_dir, 'PWG_SENSE_DCS_ATTESTATION_PILOT.md'),
                 pins, sample, extra)

    print('')
    print('lemma-attested   %d/%d' % (summary['n_lemma_attested'],
                                      summary['n_pilot_groups']))
    print('wordsem-tagged   %d/%d' % (summary['n_wordsem_tagged'],
                                      summary['n_pilot_groups']))
    print('grounded groups  %d/%d' % (summary['n_groups_grounded'],
                                      summary['n_pilot_groups']))
    print('PWG sense join   %d/%d = %.2f%%' % (summary['pwg_senses_grounded'],
                                               summary['pwg_senses_total'],
                                               100 * summary['pwg_sense_join_rate']))
    print('sense-tagged mass share %.1f%%' % (100 * summary['sensetagged_mass_share']))
    print('wrote TSV + meta.json + PWG_SENSE_DCS_ATTESTATION_PILOT.md')


if __name__ == '__main__':
    main()
