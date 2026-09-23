#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4527_bot_binomial_census.py - blast radius of the H4527 markup-strip fix in
prompt_rule_audit.looks_foreign_literal (23-09-2026), read-only, zero calls.

The fix strips markup tags from a braced {%...%} gloss before the foreign-literal
classifiers run, so {%<bot>Hibiscus abelmoschus</bot>%} is recognised as a Latin binomial
kept verbatim instead of an untranslated German gloss (kast_ur_i~~h0_zz_pw).

This script walks every {%...%} span of the PW and PWG sources (csl-orig v02/pw/pw.txt and
v02/pwg/pwg.txt; no-PWG `~~h0_zz_pw` cards such as kast_ur_i come from PW), keeps the spans
that carry markup, and classifies each one twice: with both H4527 strips as shipped
(prompt_rule_audit.MARKUP_TAG and pwg_mask.looks_botany_binomial) and without them (the
pre-H4527 functions patched back in). The gate class (foreign / german / other) and the
masker class (pwg_mask gloss_lang) are reported separately. It reports every
span whose class moved, grouped by direction and tag. A GERMAN -> FOREIGN move is the
relaxation's whole blast radius: those are the only glosses whose verbatim echo in the
Russian the gate now lets through.

Usage: python h4527_bot_binomial_census.py [--source PATH ...] [--json OUT] [--examples N]
"""
import argparse
import collections
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prompt_rule_audit as pra  # noqa: E402
import pwg_mask as pm  # noqa: E402

NEVER = re.compile(r'(?!x)x')
TAG_NAME = re.compile(r'<([A-Za-z]+)')
CSL_ORIG = os.environ.get('CSL_ORIG', os.path.expanduser('~/Documents/GitHub/csl-orig'))


def old_botany_binomial(content):
    """pwg_mask.looks_botany_binomial before H4527 (no tag strip)."""
    value = (content or '').strip()
    return bool(pm.BINOMIAL.match(value)) and not pm._has_german_markers(value)


def classify(gloss, context):
    if pra.looks_foreign_literal(gloss, context):
        return 'foreign'
    if pra.looks_german_gloss(gloss, context):
        return 'german'
    return 'other'


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', action='append', help='repeatable; default: PW + PWG')
    ap.add_argument('--json')
    ap.add_argument('--examples', type=int, default=15)
    args = ap.parse_args(argv)
    sources = args.source or [os.path.join(CSL_ORIG, 'v02', d, d + '.txt') for d in ('pw', 'pwg')]
    report = {'sources': [census(path, args.examples) for path in sources]}
    print(json.dumps(report, ensure_ascii=False, indent=1))
    if args.json:
        with open(args.json, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(report, f, ensure_ascii=False, indent=1)
            f.write('\n')
    return 0


def census(path, n_examples):
    fixed_tag, fixed_bin = pra.MARKUP_TAG, pm.looks_botany_binomial
    spans = tagged = 0
    mask_moves = collections.Counter()
    moves = collections.Counter()
    moves_by_tag = collections.Counter()
    examples = collections.defaultdict(list)
    with open(path, encoding='utf-8') as f:
        for line in f:
            if '{%' not in line:
                continue
            for i, m in enumerate(pra.BRACED_GLOSS.finditer(line)):
                spans += 1
                gloss = m.group(1).strip()
                if not fixed_tag.search(gloss):
                    continue
                tagged += 1
                context = pra.gloss_context(line, i)
                plain = pm.plain_context(context)
                pra.MARKUP_TAG, pm.looks_botany_binomial = fixed_tag, fixed_bin
                new = classify(gloss, context)
                new_mask = pm.classify_pct_detail(gloss, plain)['gloss_lang']
                pra.MARKUP_TAG, pm.looks_botany_binomial = NEVER, old_botany_binomial
                old = classify(gloss, context)
                old_mask = pm.classify_pct_detail(gloss, plain)['gloss_lang']
                pra.MARKUP_TAG, pm.looks_botany_binomial = fixed_tag, fixed_bin
                if old_mask != new_mask:
                    mask_moves['%s->%s' % (old_mask, new_mask)] += 1
                if old == new:
                    continue
                key = '%s->%s' % (old, new)
                moves[key] += 1
                for tag in sorted(set(TAG_NAME.findall(gloss))):
                    moves_by_tag[(key, tag)] += 1
                if len(examples[key]) < n_examples:
                    examples[key].append(gloss[:120])

    return {
        'source': os.path.basename(path),
        'braced_spans': spans,
        'braced_spans_with_markup': tagged,
        'masker_gloss_lang_moves': dict(mask_moves),
        'class_moves': dict(moves),
        'class_moves_by_tag': {'%s %s' % k: v for k, v in sorted(moves_by_tag.items())},
        'examples': dict(examples),
    }


if __name__ == '__main__':
    sys.exit(main())
