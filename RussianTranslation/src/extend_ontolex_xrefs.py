#!/usr/bin/env python
"""H1350 W1.8 -- additive OntoLex sidecar: attach W1.7's <ab>s.</ab> xref edges.

ADDITIVE ONLY (the fence, verbatim: "the German lemma/text nodes are never
altered, only new sibling properties added"). Rather than deep-editing the
900-line export_lod.py de-lexicon exporter under this pass's time budget,
this script emits a SEPARATE small Turtle graph of `pwglex:seeAlso` triples
from an existing `entry/<key1>/de` IRI (minted by the unmodified exporter,
same iri_local() encoding reused here so the IRIs collide correctly) to a
`lemma/<target>` IRI for every resolve_xrefs.py edge whose source key1 has an
entry in the base graph. Loads as an additional graph alongside
pwg_de_lexicon.ttl; does not require re-running or modifying the base export.

    python extend_ontolex_xrefs.py --base-ttl <path> --base-iri <iri>
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import resolve_xrefs  # noqa: E402 -- reused, unmodified
from export_lod import iri_local, esc  # noqa: E402 -- reused IRI/literal encoding


def entries_in(base_ttl_path):
    """key1 -> set of entry IRI suffixes ('', '-2', '-3', ...) present in the base graph."""
    pat = re.compile(r'<[^>]*entry/([^ ]+)/de> a ontolex:LexicalEntry')
    found = set()
    with open(base_ttl_path, encoding='utf-8') as f:
        for line in f:
            m = pat.search(line)
            if m:
                found.add(m.group(1))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base-ttl', required=True)
    ap.add_argument('--base-iri', default='https://w3id.org/sanskrit-lexicon/pwg-ru/')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    entry_ids = entries_in(args.base_ttl)
    # map iri_local(key1) (bare, no homograph suffix) -> the full entry ids sharing it
    by_bare = {}
    for eid in entry_ids:
        bare = eid.split('-')[0]
        by_bare.setdefault(bare, []).append(eid)

    edges, _ = resolve_xrefs.extract()
    triples = []
    for e in edges:
        bare = iri_local(e['k1'])
        for eid in by_bare.get(bare, []):
            triples.append((eid, e['target']))

    out_path = args.out or os.path.join(os.path.dirname(args.base_ttl), 'pwg_de_lexicon_xrefs_h1350.ttl')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('# H1350 W1.8 -- additive xref sidecar (pwglex:seeAlso), layered onto pwg_de_lexicon.ttl\n')
        f.write('# generator: RussianTranslation/src/extend_ontolex_xrefs.py, source edges: resolve_xrefs.py (W1.7)\n')
        f.write('@prefix pwglex: <%svocab#> .\n' % args.base_iri)
        f.write('@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .\n\n')
        for eid, target in triples:
            f.write('<%sentry/%s/de> pwglex:seeAlso <%slemma/%s> .\n'
                     % (args.base_iri, eid, args.base_iri, iri_local(target)))
    print(f'wrote {out_path} ({len(triples)} pwglex:seeAlso triples over {len(set(t[0] for t in triples))} entries)')


if __name__ == '__main__':
    main()
