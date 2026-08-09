#!/usr/bin/env python
r"""rv_divergence_type.py -- typed divergence taxonomy over the RV spine (H1844 C3, steps 7-9).

Consumes `pwg_ru/rv_stanza_translations.jsonl` (H1843 wave 1a) and emits one typed
label per (stanza x translator pair) over the five classes of ARCHITECTURE Sec.3.5:
`agreement` / `lexical_variant` / `semantic_shift` / `omitted_by_one` / `added_by_one`.
Five translators give ten ordered-by-convention pairs (H1910; four gave six).

Two label sources, and the split is the point:

  deterministic  -- a pair where one side's stanza is `absent_from_source` (or `empty`)
                    is `omitted_by_one` BY CONSTRUCTION. Computed from the spine with no
                    model call and no token spend (IMPLEMENTATION step 7). The measured
                    baseline is Geldner's four stanzas RV 10.106.5-8, so this arm has a
                    known ground truth before any model runs (ARCHITECTURE Sec.1).
  model          -- everything else. One chat call per stanza covering all six pairs.

Provider-pluggable, because the same OpenAI-compatible /chat/completions shape serves
both lanes we can reach from this machine:

  --provider deepseek    https://api.deepseek.com/v1        $DEEPSEEK_API_KEY
  --provider openrouter  https://openrouter.ai/api/v1       $OPENROUTER_API_KEY

The HTTP client, JSON-repair and cost accounting are REUSED verbatim from the committed
H1210 arm-B client (`src/pilot/h1210/deepseek_arm.py`) rather than rewritten -- that class
already survived a 100-card production run and carries the IncompleteRead fix. Only the
base URL and model id vary per arm, which is exactly what an A/B over model provenance
(Chinese-trained vs not) needs.

Every run is an ARM: a named (provider, model) pair written into every row, so two arms
over the SAME seeded sample can be compared with `agree` (Cohen's kappa, fine and coarse).
That comparison IS spike S2 (VERIFICATION Sec.4): if two independently-trained models do
not agree on `lexical_variant` vs `semantic_shift` above chance, the distinction is not
separable and the taxonomy collapses to the coarse three (K3) BEFORE the pilot is spent.

  python src/rv_divergence_type.py spike  --arm ds --provider deepseek --model deepseek-chat
  python src/rv_divergence_type.py pilot  --arm ds --provider deepseek --model deepseek-chat
  python src/rv_divergence_type.py agree  --a pwg_ru/h1844/spike.ds.jsonl --b ...openrouter.jsonl
  python src/rv_divergence_type.py report --in pwg_ru/rv_divergence_pilot.jsonl
  python src/rv_divergence_type.py selftest        # deterministic asserts, no model, no network
"""
import argparse
import collections
import json
import os
import random
import sys
import threading

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
RT_ROOT = os.path.normpath(os.path.join(HERE, '..'))
PWG_RU_DIR = os.path.join(RT_ROOT, 'pwg_ru')
RUN_DIR = os.path.join(PWG_RU_DIR, 'h1844')

STANZA_PATH = os.path.join(PWG_RU_DIR, 'rv_stanza_translations.jsonl')
PILOT_OUT = os.path.join(PWG_RU_DIR, 'rv_divergence_pilot.jsonl')
FULL_OUT = os.path.join(PWG_RU_DIR, 'rv_divergence.jsonl')

# Reuse the committed H1210 arm-B HTTP client verbatim (see module docstring).
sys.path.insert(0, os.path.join(HERE, 'pilot', 'h1210'))
import deepseek_arm as ds_arm  # noqa: E402

# H1910: five translators, so 5-choose-2 = 10 ordered-by-convention pairs, not 6.
TRANSLATORS = [
    'grassmann_de_1876', 'geldner_de_1951', 'elizarenkova_ru_1989', 'griffith_en_1896',
    'jamison_brereton_en_2014',
]
TRANSLATOR_LABEL = {
    'grassmann_de_1876': 'Grassmann 1876-77, German',
    'geldner_de_1951': 'Geldner 1951-57, German',
    'elizarenkova_ru_1989': 'Elizarenkova 1989-99, Russian',
    'griffith_en_1896': 'Griffith 1896, English',
    'jamison_brereton_en_2014': 'Jamison-Brereton 2014, English',
}
PAIRS = [(a, b) for i, a in enumerate(TRANSLATORS) for b in TRANSLATORS[i + 1:]]
PAIR_KEYS = ['%s|%s' % (a, b) for a, b in PAIRS]

FIVE_CLASSES = [
    'agreement', 'lexical_variant', 'semantic_shift', 'omitted_by_one', 'added_by_one',
]
# K3 / spike-S2 fallback taxonomy: the projection the five classes collapse to if the
# fine distinction turns out not to be separable. Measured from the same run, never a
# second spend.
COARSE_MAP = {
    'agreement': 'agreement',
    'lexical_variant': 'divergence',
    'semantic_shift': 'divergence',
    # H2192: `added_by_one` and `omitted_by_one` are converse readings of ONE undirected
    # event -- material present on one side and absent on the other -- so they MUST share a
    # coarse class. Before H2192 this map sent them to 'divergence' and 'omission'
    # respectively, which made the K3 projection move under a semantically vacuous choice
    # between two names for the same fact. The defect was latent rather than damaging:
    # `added_by_one` had fired 0/12,000 times, so every published coarse kappa (H1901:
    # 0.235 / 0.350 / 0.216) is bit-identical under both maps -- re-verified by
    # `rv_added_by_one_diagnosis.py coarse-kappa`.
    'added_by_one': 'omission',
    'omitted_by_one': 'omission',
}
COARSE_CLASSES = ['agreement', 'divergence', 'omission']

# The two classes that name one undirected event from opposite ends. Neither is decidable
# without saying WHICH side holds the surplus material, so both carry a mandatory
# `surplus_side` (H2192).
ASYMMETRIC_CLASSES = ('added_by_one', 'omitted_by_one')

PROVIDERS = {
    'deepseek': {'base': 'https://api.deepseek.com/v1', 'key_env': 'DEEPSEEK_API_KEY'},
    'openrouter': {'base': 'https://openrouter.ai/api/v1', 'key_env': 'OPENROUTER_API_KEY'},
}

DEFAULT_SEED = 1844
PILOT_N = 2000
SPIKE_N = 50

SYSTEM = '''You are a comparative philologist of the Rigveda, adjudicating how pairs of
scholarly translators rendered the SAME stanza. You are not translating and not judging
quality; you are classifying the relationship between two renderings.

Return ONE JSON object and nothing else -- no prose, no markdown fence.

Shape:
{"pairs": {"<translator_a>|<translator_b>": {"class": "<one of the five>", "why": "<=15 words",
                                             "surplus_side": "<translator id, or null>"}}}

`surplus_side` is REQUIRED whenever the class is "added_by_one" or "omitted_by_one", and must
be one of the two translator ids in that pair key. For every other class it is null. Those two
classes describe the SAME configuration -- one rendering carries material the other lacks --
read from opposite ends, so a class name alone does not say which translator holds the surplus.
Without the side the label is undecidable; with it the two names are distinguishable.

The five classes (choose exactly one per pair):

- "agreement": the two renderings assert the same content. Different wording and different
  target languages are EXPECTED and do not by themselves make it anything else.
- "lexical_variant": same referent and same reading, different word choice -- e.g. rendering
  the same office as "Priester" vs "Bevollmaechtigter". The scholars would not disagree if
  asked; only their diction differs.
- "semantic_shift": a real interpretive difference. The two readings are NOT interchangeable:
  a different grammatical construal, a different referent, a different sense of an ambiguous
  word. This is the class that marks a genuine scholarly disagreement.
The last two are DIRECTIONAL and are judged from the FIRST translator named in the pair key
("<translator_a>"). The direction is what separates them; do not choose between them by feel.

- "omitted_by_one": translator_a leaves untranslated material that translator_b renders -- an
  epithet, a clause, a proper name silently dropped. `surplus_side` is translator_b, the one
  who HAS the material.
- "added_by_one": translator_a supplies material with no counterpart in translator_b -- an
  explanatory gloss, a supplied subject, a parenthesised or bracketed expansion treated as
  text. `surplus_side` is translator_a.

So: surplus on the SECOND-named translator is "omitted_by_one"; surplus on the FIRST-named
translator is "added_by_one". Both occur often. If you find yourself never using one of them,
you are reading the direction off your own preference rather than off the two texts.

Rules that override any instinct to be helpful:
- Judge the RENDERINGS as given. Do not consult your own knowledge of the Sanskrit to decide
  who is right; the question is how the two texts relate to each other.
- Cross-language pairs (German vs Russian vs English) are the normal case. Translationese,
  word order and idiom are not "semantic_shift".
- Prefer "agreement" when the difference is only diction; prefer "semantic_shift" only when a
  scholar reading both would say they disagree about what the stanza means.
- If both renderings are present, never answer "omitted_by_one" or "added_by_one" for the whole
  stanza; use them for a dropped or supplied element within an otherwise-parallel rendering.
- Supplied material is often, though not always, marked: Elizarenkova and Geldner parenthesise
  words they add, Jamison-Brereton use both parentheses and brackets, Griffith's Victorian
  padding carries no delimiter at all. A marker is evidence, its absence is not counter-evidence.
- Emit a key for EVERY pair listed in the user message, and no others.'''


# --------------------------------------------------------------------- loading
def load_stanzas(path=STANZA_PATH):
    rows = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def stratified_sample(rows, n, seed=DEFAULT_SEED):
    """Stratified by mandala, proportional to stanza count, deterministically seeded
    (IMPLEMENTATION step 7 marked default). Largest-remainder allocation so the parts
    sum to exactly n."""
    by_mandala = collections.defaultdict(list)
    for r in rows:
        by_mandala[r['mandala']].append(r)
    total = len(rows)
    quotas, remainders = {}, []
    for m in sorted(by_mandala):
        exact = n * len(by_mandala[m]) / total
        quotas[m] = int(exact)
        remainders.append((exact - int(exact), m))
    short = n - sum(quotas.values())
    for _, m in sorted(remainders, reverse=True)[:short]:
        quotas[m] += 1
    rng = random.Random(seed)
    picked = []
    for m in sorted(by_mandala):
        pool = sorted(by_mandala[m], key=lambda r: (r['hymn'], r['stanza']))
        k = min(quotas[m], len(pool))
        picked.extend(rng.sample(pool, k))
    picked.sort(key=lambda r: (r['mandala'], r['hymn'], r['stanza']))
    return picked


# ------------------------------------------------------------- deterministic arm
def deterministic_pairs(stanza):
    """{pair_key: label} for every pair decidable without a model (step 7: the
    `absent_from_source` sub-case must not cost a token)."""
    out = {}
    for a, b in PAIRS:
        sa = stanza['translations'][a]['status']
        sb = stanza['translations'][b]['status']
        missing_a = sa in ('absent_from_source', 'empty')
        missing_b = sb in ('absent_from_source', 'empty')
        if missing_a or missing_b:
            out['%s|%s' % (a, b)] = {
                'class': 'omitted_by_one',
                'method': 'deterministic',
                'why': 'stanza %s in %s' % (
                    sa if missing_a else sb, a if missing_a else b),
                'missing_side': a if missing_a else b,
                # H2192: the same direction the model arm now has to supply. Here it is a
                # fact about the source, not a judgment: the side that still has the stanza
                # is the side holding the surplus material.
                'surplus_side': b if missing_a else a,
            }
    return out


# ------------------------------------------------------------------- model arm
def build_user_message(stanza, wanted_pairs):
    lines = ['Rigveda %s (mandala %d, hymn %d, stanza %d).' % (
        stanza['location'], stanza['mandala'], stanza['hymn'], stanza['stanza']), '']
    lines.append('Renderings:')
    for key in TRANSLATORS:
        t = stanza['translations'][key]
        if t['status'] != 'present':
            continue
        text = (t['text'] or '').replace('\n', ' / ')
        lines.append('- %s [%s]: %s' % (key, TRANSLATOR_LABEL[key], text))
    lines.append('')
    lines.append('Classify exactly these %d pair(s):' % len(wanted_pairs))
    for pk in wanted_pairs:
        lines.append('- %s' % pk)
    return '\n'.join(lines)


def normalise_class(value):
    v = (value or '').strip().lower().replace('-', '_').replace(' ', '_')
    return v if v in FIVE_CLASSES else None


def normalise_side(value, pair_key):
    """The `surplus_side` a model returned, resolved against the pair it belongs to.

    Returns (side_or_None, note). Accepts the full translator id or a bare surname, since a
    model asked for `griffith_en_1896` will sometimes answer `Griffith`. Anything that does
    not resolve to one of THIS pair's two translators is rejected rather than coerced --
    same posture the class enum already takes with out-of-enum values (H1901's `class: null`).
    """
    a, b = pair_key.split('|')
    raw = (value or '').strip().lower()
    if not raw:
        return None, 'missing'
    if raw in (a, b):
        return raw, None
    hits = [t for t in (a, b) if t.split('_')[0] == raw]
    if len(hits) == 1:
        return hits[0], None
    return None, 'unresolved: %r' % value


def type_one_stanza(client, stanza):
    """-> (record, call_telemetry). Deterministic pairs never reach the model."""
    det = deterministic_pairs(stanza)
    wanted = [pk for pk in PAIR_KEYS if pk not in det]
    rec = {
        'location': stanza['location'], 'mandala': stanza['mandala'],
        'hymn': stanza['hymn'], 'stanza': stanza['stanza'],
        'pairs': dict(det),
    }
    if not wanted:
        return rec, None
    text, call = client.chat(SYSTEM, build_user_message(stanza, wanted), stanza['location'])
    if text is None:
        rec['error'] = 'transport: %s' % call.get('error')
        return rec, call
    try:
        obj, repair = ds_arm.extract_json(text)
    except ValueError as e:
        rec['error'] = 'unparseable: %s' % e
        return rec, call
    if repair:
        rec['repair'] = repair
    got = obj.get('pairs') or {}
    for pk in wanted:
        entry = got.get(pk) or {}
        cls = normalise_class(entry.get('class'))
        if cls is None:
            rec['pairs'][pk] = {'class': None, 'method': 'model',
                                'why': 'unclassified: %r' % entry.get('class')}
        else:
            row = {'class': cls, 'method': 'model', 'why': (entry.get('why') or '')[:160]}
            if cls in ASYMMETRIC_CLASSES:
                # H2192: an asymmetric label without a side is not a weaker label, it is an
                # undecidable one -- `added_by_one` and `omitted_by_one` name one event from
                # opposite ends. Record the gap on the row instead of accepting a coin flip.
                side, note = normalise_side(entry.get('surplus_side'), pk)
                row['surplus_side'] = side
                if note:
                    row['surplus_side_note'] = note
            else:
                row['surplus_side'] = None
            rec['pairs'][pk] = row
    return rec, call


# ------------------------------------------------------------------------ runner
def make_client(provider, model, env_file, max_tokens=2048):
    spec = PROVIDERS[provider]
    key = os.environ.get(spec['key_env']) or ds_arm.load_env_file(env_file).get(spec['key_env'])
    if not key:
        sys.exit('%s not found in the environment or --env-file %r. This arm needs it; '
                 'the other arm can still run.' % (spec['key_env'], env_file))
    return ds_arm.DeepSeek(spec['base'], key, model, max_tokens)


def run_arm(rows, out_path, arm, provider, model, env_file, workers, resume):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    done = set()
    if resume and os.path.exists(out_path):
        with open(out_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    done.add(json.loads(line)['location'])
        print('resume: %d rows already typed in %s' % (len(done), out_path))
    todo = [r for r in rows if r['location'] not in done]
    client = make_client(provider, model, env_file)

    lock = threading.Lock()
    written = [0]
    fh = open(out_path, 'a' if done else 'w', encoding='utf-8', newline='\n')

    def work(stanza):
        rec, _ = type_one_stanza(client, stanza)
        rec['arm'] = arm
        rec['provider'] = provider
        rec['model'] = model
        with lock:
            fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
            fh.flush()
            written[0] += 1
            if written[0] % 25 == 0 or written[0] == len(todo):
                print('  typed %d/%d (%s)' % (written[0], len(todo), arm))

    try:
        _pool(todo, work, workers)
    finally:
        fh.close()

    cost = client.cost()
    print('arm %s (%s / %s): %d stanzas typed -> %s' % (arm, provider, model, len(todo), out_path))
    print('  cost: %s in(miss) + %s in(hit) + %s out tokens = $%.4f'
          % (cost['cache_miss_in_tokens'], cost['cache_hit_in_tokens'],
             cost['out_tokens'], cost['usd']))
    errors = sum(1 for c in client.calls if c.get('error'))
    if errors:
        print('  transport failures: %d call(s)' % errors)
    return cost


def _pool(items, fn, workers):
    if not items:
        return
    it = iter(items)
    guard = threading.Lock()

    def loop():
        while True:
            with guard:
                try:
                    item = next(it)
                except StopIteration:
                    return
            fn(item)

    threads = [threading.Thread(target=loop, daemon=True) for _ in range(max(1, workers))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ------------------------------------------------------------------- reporting
def _labels(path):
    """{(location, pair_key): (class, method)} over one arm's output."""
    out = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for pk, entry in rec['pairs'].items():
                out[(rec['location'], pk)] = (entry.get('class'), entry.get('method'))
    return out


def distribution(path):
    fine = collections.Counter()
    coarse = collections.Counter()
    by_method = collections.Counter()
    unclassified = 0
    for (_, _), (cls, method) in _labels(path).items():
        by_method[method] += 1
        if cls is None:
            unclassified += 1
            continue
        fine[cls] += 1
        coarse[COARSE_MAP[cls]] += 1
    return fine, coarse, by_method, unclassified


def cmd_report(a):
    fine, coarse, by_method, unclassified = distribution(a.inp)
    total = sum(fine.values())
    print('divergence distribution -- %s' % a.inp)
    print('  labelled pairs: %d (%d unclassified)' % (total, unclassified))
    print('  by method: %s' % dict(by_method))
    print('  five-class:')
    for c in FIVE_CLASSES:
        print('    %-16s %6d  %5.1f%%' % (c, fine[c], 100.0 * fine[c] / total if total else 0))
    print('  coarse (K3 projection):')
    for c in COARSE_CLASSES:
        print('    %-16s %6d  %5.1f%%' % (c, coarse[c], 100.0 * coarse[c] / total if total else 0))
    return 0


def cohens_kappa(pairs):
    """pairs: iterable of (label_a, label_b). Returns (kappa, observed_agreement, n)."""
    pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
    n = len(pairs)
    if not n:
        return float('nan'), float('nan'), 0
    agree = sum(1 for x, y in pairs if x == y) / n
    ca = collections.Counter(x for x, _ in pairs)
    cb = collections.Counter(y for _, y in pairs)
    expected = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    if expected >= 1.0:
        return float('nan'), agree, n
    return (agree - expected) / (1 - expected), agree, n


def cmd_agree(a):
    """Spike S2: do two independently-trained models separate the fine classes?"""
    la, lb = _labels(a.a), _labels(a.b)
    shared = sorted(set(la) & set(lb))
    if not shared:
        sys.exit('no overlapping (location, pair) keys between the two arms')

    def arm_meta(path):
        with open(path, encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    return r.get('arm'), r.get('provider'), r.get('model')
        return None, None, None

    print('inter-arm agreement (spike S2)')
    print('  A: %s %s' % (a.a, arm_meta(a.a)))
    print('  B: %s %s' % (a.b, arm_meta(a.b)))
    print('  overlapping (stanza x pair) labels: %d' % len(shared))

    model_only = [k for k in shared if la[k][1] == 'model' and lb[k][1] == 'model']
    print('  of which model-decided on both sides: %d '
          '(the rest are deterministic and agree trivially)' % len(model_only))

    for name, keys in (('all pairs', shared), ('model-decided only', model_only)):
        fine = [(la[k][0], lb[k][0]) for k in keys]
        coarse = [(COARSE_MAP.get(x), COARSE_MAP.get(y)) for x, y in fine
                  if x is not None and y is not None]
        kf, af, nf = cohens_kappa(fine)
        kc, ac, nc = cohens_kappa(coarse)
        print('  [%s]' % name)
        print('    five-class : n=%4d  observed agreement %5.1f%%  kappa %.3f' % (nf, 100 * af, kf))
        print('    coarse     : n=%4d  observed agreement %5.1f%%  kappa %.3f' % (nc, 100 * ac, kc))

    fine = [(la[k][0], lb[k][0]) for k in model_only]
    conf = collections.Counter(fine)
    print('  confusion (model-decided, A rows x B cols), five-class:')
    header = '    %-16s' % '' + ''.join('%16s' % c[:15] for c in FIVE_CLASSES)
    print(header)
    for ra in FIVE_CLASSES:
        print('    %-16s' % ra + ''.join('%16d' % conf[(ra, rb)] for rb in FIVE_CLASSES))

    # The specific question S2 asks: are lexical_variant and semantic_shift separable?
    lv_ss = [(x, y) for x, y in fine
             if x in ('lexical_variant', 'semantic_shift') and y in ('lexical_variant', 'semantic_shift')]
    if lv_ss:
        k2, a2, n2 = cohens_kappa(lv_ss)
        print('  lexical_variant vs semantic_shift ONLY: n=%d  agreement %.1f%%  kappa %.3f'
              % (n2, 100 * a2, k2))
        print('  (this is the S2 verdict number -- kappa at or below ~0.2 means the two '
              'classes are not being distinguished, and the taxonomy collapses to coarse per K3)')
    else:
        print('  lexical_variant vs semantic_shift ONLY: no overlapping cases')
    return 0


# ------------------------------------------------------------------------ selftest
def selftest():
    stanza = {
        'location': '10.106.5', 'mandala': 10, 'hymn': 106, 'stanza': 5,
        'translations': {
            'grassmann_de_1876': {'status': 'present', 'text': 'A'},
            'geldner_de_1951': {'status': 'absent_from_source', 'text': None},
            'elizarenkova_ru_1989': {'status': 'present', 'text': 'B'},
            'griffith_en_1896': {'status': 'present', 'text': 'C'},
            'jamison_brereton_en_2014': {'status': 'present', 'text': 'D'},
        },
    }
    det = deterministic_pairs(stanza)
    # Every pair involving geldner is decided without a model; the others are not. With
    # five translators that is 4 of the 10 pairs, not 3 of 6 (H1910).
    assert len(det) == 4, det
    assert all(v['class'] == 'omitted_by_one' and v['method'] == 'deterministic'
               for v in det.values()), det
    assert all('geldner' in k for k in det), det
    assert 'grassmann_de_1876|elizarenkova_ru_1989' not in det

    # H2192 -- the direction the asymmetric classes cannot do without.
    for pk, row in det.items():
        a, b = pk.split('|')
        assert row['missing_side'] == 'geldner_de_1951', row
        assert row['surplus_side'] in (a, b) and row['surplus_side'] != row['missing_side'], row
    # Converse classes are ONE undirected event, so they share a coarse class. A coarse
    # projection that splits them moves under a semantically vacuous relabelling.
    assert COARSE_MAP['added_by_one'] == COARSE_MAP['omitted_by_one'] == 'omission'
    assert set(ASYMMETRIC_CLASSES) <= set(FIVE_CLASSES)
    assert all(COARSE_MAP[c] in COARSE_CLASSES for c in FIVE_CLASSES)

    # The prompt has to be directional, or the model has no way to tell the two apart and
    # falls back on one of them forever (0/12,000 in the H1844 pilot).
    assert 'surplus_side' in SYSTEM
    assert 'FIRST translator named in the pair key' in SYSTEM

    pk = 'grassmann_de_1876|griffith_en_1896'
    assert normalise_side('griffith_en_1896', pk) == ('griffith_en_1896', None)
    assert normalise_side('Griffith', pk) == ('griffith_en_1896', None)      # surname form
    assert normalise_side(None, pk) == (None, 'missing')
    assert normalise_side('geldner_de_1951', pk)[0] is None                  # not in THIS pair
    assert normalise_side('both', pk)[0] is None

    full = {'status': 'present', 'text': 'x'}
    allpresent = {'location': '1.1.1', 'mandala': 1, 'hymn': 1, 'stanza': 1,
                  'translations': {k: dict(full) for k in TRANSLATORS}}
    assert deterministic_pairs(allpresent) == {}

    assert len(TRANSLATORS) == 5
    assert len(PAIRS) == 10 and len(set(PAIR_KEYS)) == 10
    assert set(TRANSLATOR_LABEL) == set(TRANSLATORS)
    assert set(COARSE_MAP) == set(FIVE_CLASSES)
    assert normalise_class('Semantic Shift') == 'semantic_shift'
    assert normalise_class('lexical-variant') == 'lexical_variant'
    assert normalise_class('nonsense') is None

    # sampler: deterministic under a seed, proportional across mandalas, exact size
    rows = [{'location': '%d.1.%d' % (m, i), 'mandala': m, 'hymn': 1, 'stanza': i,
             'translations': {k: dict(full) for k in TRANSLATORS}}
            for m in range(1, 11) for i in range(1, 101)]
    s1 = stratified_sample(rows, 200, seed=7)
    s2 = stratified_sample(rows, 200, seed=7)
    s3 = stratified_sample(rows, 200, seed=8)
    assert len(s1) == 200
    assert [r['location'] for r in s1] == [r['location'] for r in s2], 'seed must be stable'
    assert [r['location'] for r in s1] != [r['location'] for r in s3], 'seed must matter'
    per = collections.Counter(r['mandala'] for r in s1)
    assert set(per) == set(range(1, 11)) and all(v == 20 for v in per.values()), per

    k, agree, n = cohens_kappa([('a', 'a'), ('b', 'b'), ('a', 'a'), ('b', 'b')])
    assert n == 4 and agree == 1.0 and abs(k - 1.0) < 1e-9
    k, agree, n = cohens_kappa([('a', 'b'), ('b', 'a')])
    assert agree == 0.0 and k < 0
    assert cohens_kappa([])[2] == 0

    print('rv_divergence_type selftest OK -- deterministic omission arm (Geldner 10.106.5 '
          'decides %d/%d pairs with no model), seeded stratified sampler, class '
          'normaliser, kappa' % (len(det), len(PAIRS)))
    return 0


# ---------------------------------------------------------------------------- cli
def _add_arm_args(p, default_out, default_n):
    p.add_argument('--arm', required=True, help='short arm name, written into every row')
    p.add_argument('--provider', choices=sorted(PROVIDERS), default='deepseek')
    p.add_argument('--model', default='deepseek-chat')
    p.add_argument('--env-file', default=os.path.join(HERE, '.env'))
    p.add_argument('--out', default=default_out)
    p.add_argument('--n', type=int, default=default_n)
    p.add_argument('--seed', type=int, default=DEFAULT_SEED)
    p.add_argument('--workers', type=int, default=6)
    p.add_argument('--resume', action='store_true')


def main():
    ap = argparse.ArgumentParser(description='RV divergence taxonomy (H1844 steps 7-9)')
    sub = ap.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('spike', help='S2 separability spike (default 50 stanzas)')
    _add_arm_args(sp, os.path.join(RUN_DIR, 'spike.jsonl'), SPIKE_N)

    pl = sub.add_parser('pilot', help='step 7 pilot (default 2,000 stanzas)')
    _add_arm_args(pl, PILOT_OUT, PILOT_N)

    fu = sub.add_parser('full', help='step 9 full run -- REQUIRES the voted step-8 gate')
    _add_arm_args(fu, FULL_OUT, 0)
    fu.add_argument('--gate-decisions', required=True,
                    help='path to the voted review-sheet decisions.json (R13: no gate, no run)')

    rp = sub.add_parser('report', help='class distribution of one arm')
    rp.add_argument('--in', dest='inp', required=True)

    ag = sub.add_parser('agree', help='spike S2: inter-arm agreement + kappa')
    ag.add_argument('--a', required=True)
    ag.add_argument('--b', required=True)

    sub.add_parser('selftest', help='deterministic asserts, no model, no network')

    a = ap.parse_args()
    if a.cmd == 'selftest':
        return selftest()
    if a.cmd == 'report':
        return cmd_report(a)
    if a.cmd == 'agree':
        return cmd_agree(a)

    rows = load_stanzas()
    if a.cmd == 'full':
        if not os.path.exists(a.gate_decisions):
            sys.exit('R13 STOP: the step-8 human gate has not been voted (%s missing). '
                     'The full run stays queued -- this is the marked default, not a failure.'
                     % a.gate_decisions)
        sample = rows
    else:
        sample = stratified_sample(rows, a.n, seed=a.seed)
    print('%s: %d stanzas selected (seed %d) of %d' % (a.cmd, len(sample), a.seed, len(rows)))
    run_arm(sample, a.out, a.arm, a.provider, a.model, a.env_file, a.workers, a.resume)
    return 0


if __name__ == '__main__':
    sys.exit(main())
