#!/usr/bin/env python
"""Compile the translatable wrapper-prose for a merged headword — language-aware.

The merged card is no longer PWG-only German: the supplement chain adds PW / SCH /
PWKVN (German) and the NWS "Kleines Zitat", whose sub-sources are written in
GERMAN (Geldner, Graßmann, Vishva Bandhu, Meyer…), ENGLISH (MW, Olivelle, Keller,
Hoernle, BHSD, Sircar…) AND FRENCH (Renou, Padoux, Caland, Rivelex…). Assuming
"German" for the whole card would mistranslate the English/French glosses.

This tool emits, per headword, the exact prose that must go to Russian — one unit
per sense / NWS sub-source — each tagged with its source language(s), with the
untranslatable parts (Sanskrit {#…#}/IAST, sigla <ls>, grammar <lex>/Subst/Adj,
the owner citation) pulled out into `keep`. Sanskrit, sigla and grammar are NEVER
translated (the project's format invariant); only the natural-language gloss is.

  python compile_translatable.py one   <key>          print the manifest
  python compile_translatable.py write <key> [key...]  -> pilot/translate/<safe>.{json,md}
  python compile_translatable.py langs <key>           per-NWS-entry language tally
"""
import os, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import glob, time
from safe_filename import safe_name, decode_safe_name
import nws_split as NS

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, 'pilot', 'input')
OUT = os.path.join(HERE, 'pilot', 'translate')

# ---------------------------------------------------------------- language ID
FR_CH, DE_CH = set('àâçéèêëîïôûùœ'), set('äöüßÄÖÜ')
FR_W = set('le la les un une des du de au aux et ou qui que dans avec sans sur '
           'pour par cas idée racine sort place forme nature comme entre type '
           'sens point tire quelconque participation parenté affinité être'.split())
DE_W = set('der die das und oder von zu zur zum im am ein eine einer eines dem '
           'den auch nicht bei nach über als wie anteil teil gott feuer speise '
           'wort silbe zweck sache grad partei erbtheil antheil zugewiesener '
           'besitzt vergeben gold himmel wasser unsterblich aufgabe feind '
           'gesammtheit zubringung besitz'.split())
EN_W = set('the of a an and with for or in to part share fire food name water '
           'gold giving consisting being into after received especially a lot '
           'meaning thing object aim goal degree shoulder numerator fraction '
           'inheritance booty earnest territorial cooked draw lots'.split())


# suffix morphology — resolves the short cue-less glosses (scurrilous, freilaufend)
EN_SUF = ('ous', 'ing', 'ness', 'less', 'ful', 'ity', 'ical', 'ically', 'ed',
          'tion', 'sion')
DE_SUF = ('ung', 'heit', 'keit', 'lich', 'isch', 'schaft', 'end', 'bar', 'ungen',
          'erei', 'keiten')
FR_SUF = ('eur', 'aire', 'ique', 'isme', 'ée', 'ées', 'ité')

# NWS sub-source -> source language (the author IS the strongest signal). Used as a
# prior only when the gloss text itself is inconclusive. Vishva Bandhu / NṚV mix
# languages, so they are deliberately left to text detection.
OWNER_LANG = {
    'MW': 'en', 'Olivelle': 'en', 'Keller': 'en', 'Hoernle': 'en', 'BHSD': 'en',
    'Sircar': 'en', 'Halbfass': 'en', 'Gerow': 'en', 'Ensink': 'en', 'Rao': 'en',
    'Rocher': 'en', 'Vedic Hymns': 'en', 'Edgerton': 'en',
    'Geldner': 'de', 'Graßmann': 'de', 'Grassmann': 'de', 'Meyer': 'de',
    'Windisch': 'de', 'Hellwig': 'de', 'Kümmel': 'de', 'Krick': 'de',
    'Rivelex': 'de', 'WdaR': 'de', 'SIjNS': 'de', 'Sarma': 'en',
    'Renou': 'fr', 'Padoux': 'fr', 'Caland': 'fr', 'TAK': 'fr',
}


def detect(text, owner=None):
    """-> sorted list of language codes with positive evidence (de/fr/en). Uses the
    NWS sub-source author as a prior when the gloss text alone is inconclusive."""
    toks = re.findall(r"[A-Za-zÀ-ÿĀ-ỿ'\-]+", text)
    low = [t.lower() for t in toks]
    de = sum(t in DE_W for t in low) + 2 * sum(c in DE_CH for c in text)
    fr = sum(t in FR_W for t in low) + 2 * sum(c in FR_CH for c in text)
    en = sum(t in EN_W for t in low)
    if '(MW)' in text or 'Lex(MW' in text:        # Monier-Williams gloss = English
        en += 2
    for t in low:
        en += sum(t.endswith(s) for s in EN_SUF)
        de += sum(t.endswith(s) for s in DE_SUF)
        fr += sum(t.endswith(s) for s in FR_SUF)
    # German capitalises common nouns mid-clause — a weak German signal
    de += 0.5 * sum(1 for i, t in enumerate(toks)
                    if i and t[:1].isupper() and len(t) > 3 and t.lower() not in DE_W)
    score = {'de': de, 'fr': fr, 'en': en}
    hi = max(score.values())
    if hi == 0:
        prior = OWNER_LANG.get(NS.owner_surname(owner)) if owner else None
        return [prior] if prior else ['en?']
    keep = [k for k, v in score.items() if v >= max(1, hi * 0.5)]
    return sorted(keep, key=lambda k: -score[k])


# ---------------------------------------------------------------- masking
GRAM = re.compile(r'\b(Subst|Adj|Adv|Indekl|PostP)\b\s*(mfn|ifc|m\.?|n\.?|f\.?)?'
                  r'|\b(mfn|ifc|NPr|Pl|Sg|Du|Akk|Lok|Dat|Gen|Instr|Nom|Vok)\b:?')
INLINE_SA = re.compile(r'\{#.*?#\}|<is>.*?</is>')
LS = re.compile(r'<ls\b[^>]*>.*?</ls>|<ab\b[^>]*>.*?</ab>|<lex\b[^>]*>.*?</lex>'
                r'|<[^>]+>')
PCT = re.compile(r'\{%(.*?)%\}', re.S)
# a {%…%} span that is purely lowercase IAST (a Sanskrit headword like aṃśa,
# kenāṃśena) is NOT a German gloss — keep it verbatim, never translate it
IAST_ONLY = re.compile(r'^[a-zāīūṛṝḷḹṅñṭḍṇśṣṃḥ/\-\s]+$')
SA_DIA = re.compile(r'[āīūṛṝḷḹṅñṭḍṇśṣṃḥ]')


def is_sanskrit(span):
    return bool(IAST_ONLY.match(span.strip()) and SA_DIA.search(span))
# internal reference: a siglum/work-name followed by numbers (ṚV 7,32,12 ; KA 3.5.13)
REF = re.compile(r'[A-ZÀ-ÖŚṚṢṬĀ][\wĀ-ỿ’.()\-]*(?:\s+[\dIVXLC])[\d.,;\s()IVXLC/–-]*')


def mask_nws_gloss(gloss, owner):
    """Strip grammar, sigla and the owner cite from an NWS gloss -> (prose, keep)."""
    keep = []
    g = gloss
    if owner:                                       # drop the trailing owner cite
        g = re.sub(re.escape(owner.split(' (s.v')[0]).replace(r'\ ', r'\s*')
                   + r'.*$', '', g).rstrip(' .')
    for m in INLINE_SA.findall(g):
        keep.append(m)
    g = INLINE_SA.sub(' ', g)
    for m in GRAM.findall(re.sub(r'\s+', ' ', g)):
        pass
    g = GRAM.sub(' ', g)
    # pull internal references (kept verbatim, never translated)
    for m in REF.finditer(g):
        s = m.group(0).strip(' .,;')
        if s and not s.isalpha():
            keep.append(s)
    g = REF.sub(' ', g)
    g = re.sub(r'\[\s*s\.\s*v\.[^\]]*\]', ' ', g)    # [s.v. …] editor pointers
    g = re.sub(r'[(\[]\s*[)\]]', ' ', g)             # empty () [] left by masking
    g = re.sub(r'\s+([.,;])', r'\1', re.sub(r'\s+', ' ', g))
    g = re.sub(r'([.,;])\1+', r'\1', g).strip(' .,;')
    return g, keep


# ---------------------------------------------------------------- layers
def read_raw(key):
    for nm in (safe_name(key), key):
        p = os.path.join(INP, nm + '.raw.txt')
        if os.path.exists(p):
            return open(p, encoding='utf-8').read()
    return ''


def read_portrait(key):
    for nm in (safe_name(key), key):
        p = os.path.join(INP, nm + '.portrait.json')
        if os.path.exists(p):
            return json.load(open(p, encoding='utf-8'))
    return []


def layer_blocks(raw):
    """-> list of (role, body) for each '=== LAYER: … ===' section."""
    parts = re.split(r'=== LAYER:\s*(.*?)\s*===\n', raw)
    out = []
    for i in range(1, len(parts), 2):
        out.append((parts[i].split('—')[0].split('(')[0].strip(), parts[i + 1].strip()))
    return out


def units(key):
    raw, port = read_raw(key), read_portrait(key)
    U = []
    # 1) PWG — German glosses straight from the parsed portrait
    for rec in port:
        for s in rec.get('senses', []):
            g = (s.get('gloss_de') or '').strip()
            if s['n'] == '0' or not s.get('equivalents_de') and not g:
                continue
            txt = '; '.join(s['equivalents_de']) if s.get('equivalents_de') else g
            U.append({'layer': 'PWG', 'ref': s['n'] + (s['sub'] or ''),
                      'lang': ['de'], 'text': txt, 'keep': []})
    # 2) PW / SCH / PWKVN — German {%…%} spans (+ bare German is flagged, rare)
    for role, body in layer_blocks(raw):
        code = role.split()[0].upper()
        if code not in ('PW', 'SCH', 'PWKVN'):
            continue
        for g in PCT.findall(body):
            g = g.strip().rstrip(':')
            if not g or g.startswith('{'):
                continue
            if is_sanskrit(g):                       # Sanskrit headword in {%…%}, keep verbatim
                U.append({'layer': code, 'ref': '', 'lang': ['sa'],
                          'text': '', 'keep': [g]})
                continue
            U.append({'layer': code, 'ref': '', 'lang': ['de'], 'text': g, 'keep': []})
    # 3) NWS — per sub-source entry, language-detected
    frag = NS.nws_fragment(key)
    if frag:
        for e in NS.split(frag):
            owner = e['owners'][0] if e['owners'] else ''
            prose, keep = mask_nws_gloss(e['gloss'], owner)
            lang = detect(prose, owner) if prose else ['none']  # only sigla/Sanskrit left
            U.append({'layer': 'NWS', 'ref': ' / '.join(e['owners']) or '?',
                      'lemma': e['lemma'], 'lang': lang,
                      'text': prose, 'keep': keep})
    return U


def manifest(key):
    return {'key': key, 'safe': safe_name(key), 'units': units(key)}


# ---------------------------------------------------------------- outputs
def to_md(man):
    L = ['# %s — translatable content (%d units)' % (man['key'], len(man['units'])),
         '', 'Source languages per unit are detected; only this prose goes to '
         'Russian. Sanskrit, sigla and grammar in `keep` stay verbatim.', '']
    cur = None
    for u in man['units']:
        if u['layer'] != cur:
            cur = u['layer']
            L += ['', '## %s' % cur, '',
                  '| ref | lang | to translate | keep |', '|---|---|---|---|']
        keep = ' · '.join(u['keep'])[:60]
        L.append('| %s | %s | %s | %s |' % (
            u['ref'][:32], ','.join(u['lang']),
            u['text'].replace('|', '\\|')[:120], keep.replace('|', '\\|')))
    return '\n'.join(L) + '\n'


def write(keys):
    os.makedirs(OUT, exist_ok=True)
    for key in keys:
        man = manifest(key)
        base = os.path.join(OUT, safe_name(key))
        json.dump(man, open(base + '.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        open(base + '.md', 'w', encoding='utf-8').write(to_md(man))
        langs = sorted({l for u in man['units'] for l in u['lang']})
        print('  %-8s %3d units  langs=%s -> %s.{json,md}'
              % (key, len(man['units']), ','.join(langs), safe_name(key)))


def all_keys():
    fs = sorted(glob.glob(os.path.join(INP, '*.raw.txt')))
    return [decode_safe_name(os.path.basename(f)[:-len('.raw.txt')]) for f in fs]


def run_all(emit_md=False):
    """Compile every input headword -> pilot/translate/<safe>.json (+md if asked).
    Writes a coverage/language summary; resilient to per-card errors."""
    os.makedirs(OUT, exist_ok=True)
    keys = all_keys()
    from collections import Counter
    lang_units, cards_with, errors = Counter(), Counter(), []
    nws_cards = tot_units = 0
    t0 = time.time()
    for i, key in enumerate(keys):
        try:
            man = manifest(key)
        except Exception as e:                       # never let one card kill the batch
            errors.append((key, repr(e)[:120]))
            continue
        base = os.path.join(OUT, safe_name(key))
        json.dump(man, open(base + '.json', 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        if emit_md:
            open(base + '.md', 'w', encoding='utf-8').write(to_md(man))
        us = man['units']
        tot_units += len(us)
        has_nws = any(u['layer'] == 'NWS' for u in us)
        nws_cards += has_nws
        seen = set()
        for u in us:
            for l in u['lang']:
                lang_units[l] += 1
                seen.add(l)
        for l in seen:
            cards_with[l] += 1
        if (i + 1) % 1000 == 0:
            print('  ... %d/%d (%.0fs)' % (i + 1, len(keys), time.time() - t0))
    rep = ['# a-section translatable-content compile — summary',
           '', '- cards compiled: **%d** (%d errors)' % (len(keys) - len(errors), len(errors)),
           '- cards with an NWS layer: **%d**' % nws_cards,
           '- total translatable units: **%d**' % tot_units,
           '- elapsed: %.0fs' % (time.time() - t0), '',
           '## language spread (per unit / per card)', '',
           '| lang | units | cards |', '|---|---|---|']
    for l in ['de', 'en', 'fr', 'sa', 'none', 'en?']:
        rep.append('| %s | %d | %d |' % (l, lang_units.get(l, 0), cards_with.get(l, 0)))
    if errors:
        rep += ['', '## errors (first 30)', '']
        rep += ['- `%s` — %s' % (k, e) for k, e in errors[:30]]
    open(os.path.join(OUT, '_SUMMARY.md'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    print('\n'.join(l for l in rep if not l.startswith('|') or l.startswith('| lang')))
    print('  wrote %d manifests -> %s  (summary: _SUMMARY.md)'
          % (len(keys) - len(errors), OUT))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'one'
    keys = sys.argv[2:] or ['aMSa']
    if cmd == 'one':
        print(to_md(manifest(keys[0])))
    elif cmd == 'write':
        write(keys)
    elif cmd == 'all':
        run_all(emit_md='--md' in sys.argv)
    elif cmd == 'langs':
        for u in units(keys[0]):
            if u['layer'] == 'NWS':
                print('  %-34s %-8s %s' % (u['ref'][:34], ','.join(u['lang']),
                                           u['text'][:70]))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
