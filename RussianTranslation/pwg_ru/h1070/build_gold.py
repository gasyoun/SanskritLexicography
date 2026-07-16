#!/usr/bin/env python
r"""build_gold.py - merge the H1070 Fable rulings into worksheet.jsonl -> en_gold_adjudication.jsonl.

Adjudicator: Fable 5 (claude-fable-5), 17-07-2026. Rubric (H1070): ruling in
{correct, acceptable-variant, wrong-sense, register-mismatch}; ground truth = the PWG
German (FU1 locked decision 6); MW = adversary cross-check only. RULINGS below is the
authoritative per-row judgment record - rows absent from it are 'correct' with the
default reason. Dots per /gold-adjudicate: blue = clear call, yellow = ruled but close.

Spot-checks against raw wf_output.en.*.json (2026-07-17): r005 resolved as a sample-frame
split artifact (tail lives in sibling sense caus-1-cause-to-enjoy - no omission);
r102 / r119 / r155 defects CONFIRMED present in the raw english fields.
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_REASON = 'EN renders the German gloss(es) faithfully; MW cross-check consistent.'

# uid: (ruling, dot, classes, reason)
RULINGS = {
    # ---- pilot tranche (Sonnet 4.6) ----
    'r005': ('correct', 'blue', ['frame-split-note'],
             'Suspected tail omission (geniessen lassen + MEGH./BHATT. citations) is a sample-frame artifact: the tail is translated in sibling split sense caus-1-cause-to-enjoy of the same card. No omission.'),
    'r011': ('acceptable-variant', 'yellow', ['addition-minor'],
             '"to be mutually inconsistent" unfolds "sich gegenseitig widersprechen" beyond the literal gloss; same semantic claim for the sAMvatsarAH context, so variant not error.'),
    'r016': ('acceptable-variant', 'yellow', ['term-weak'],
             '"dahinfahren" (chariots let loose, RV 9,22,1) rendered flat as "to travel away, go forth"; MW\'s "rush on" is sharper. Motion sense preserved.'),
    'r018': ('acceptable-variant', 'yellow', ['nws-prefix-metadata'],
             'EN prepends "8. [NWS: SJS 3 : 86]" numbering+source tag absent from the DE row - the FINDINGS-84 stylistic [NWS:] class; content itself faithful.'),
    'r021': ('acceptable-variant', 'yellow', ['de-residue-crossref'],
             'Entire row is the German cross-ref "s. u. d. W." left untranslated (S7\'s untranslated-editorial-note class).'),
    'r022': ('acceptable-variant', 'yellow', ['de-residue'],
             '"<ab>insbes.</ab> especially" doubles the German abbreviation with its translation; meaning intact.'),
    'r025': ('wrong-sense', 'blue', ['addition', 'mw-tm-contamination', 'de-residue'],
             'EN adds "(of a heavenly body)" - an MW-style domain parenthetical the German does not contain (S7 unfaithful case 3, the one confirmed MW-TM leak); "u. s. w." also left in German.'),
    'r031': ('acceptable-variant', 'yellow', ['de-residue-crossref'],
             'Cross-ref row "Vgl. ... fgg." left entirely untranslated.'),
    'r050': ('acceptable-variant', 'yellow', ['term-minor'],
             '"ist ... zu verbinden" (editorial: construe as one compound) rendered "is to be read with" - S7\'s known minor term slip, recurring here.'),
    'r056': ('acceptable-variant', 'yellow', ['nws-prefix-metadata'],
             '"25. [NWS: BHSD : 442...]" prefix added vs the DE row; BHSD content itself faithfully carried.'),
    'r058': ('acceptable-variant', 'yellow', ['de-residue-crossref'],
             'Cross-ref row "s. parimAd fg." untranslated.'),
    'r060': ('acceptable-variant', 'yellow', ['de-residue-crossref'],
             'Cross-ref row "Vgl. prayatitavya fgg." untranslated.'),
    'r063': ('acceptable-variant', 'yellow', ['de-residue-nws-hash'],
             'NWS source wraps the German gloss "hingelangen zu (Akk)" inside {#..#} Sanskrit markers, so the pipeline protects it verbatim - German gloss reaches EN untranslated. Systematic NWS-row class.'),
    'r065': ('acceptable-variant', 'yellow', ['de-residue-nws-hash'],
             'Same NWS {#..#}-wrapped German class as r063 (Grassmann gloss list untranslated); the unwrapped remainder is translated excellently.'),
    # soft notes on correct pilot rows
    'r020': ('correct', 'blue', ['doublet-soft'], 'geborsten -> "burst, cracked": synonym doubling, no drift.'),
    'r035': ('correct', 'blue', ['de-residue-soft'], 'Substance translated; German abbrevs Z./st. retained inside <ab> tags (preserve-class tokens).'),
    'r049': ('correct', 'blue', ['mw-homonym-note'], 'Faithful throughout; MW quote is the ud-gA "rise" homonym (lookup artifact), MW\'s sing sense sits under ud-gai.'),
    'r067': ('correct', 'blue', ['register-soft'], '"Schol. zu P." -> "Schol. to P." where house usage elsewhere is "on"; forms card otherwise exact.'),
    # ---- fu1 tranche (Sonnet 5) ----
    'r078': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref row "Vgl. ujjayana fgg. ..." untranslated.'),
    'r087': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref row "vgl. pratispaSa..." untranslated.'),
    'r088': ('acceptable-variant', 'yellow', ['de-residue-connectives', 'markup-quotes'],
             'Grammar-commentary translated well, but citation-apparatus connectives left German (PAT. zu P., ders. zu 147 bei GOLD.) and {%..%} wrappers became ASCII quotes.'),
    'r089': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref "Vgl. aBisaMbanDa." untranslated.'),
    'r095': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref "Vgl. icCA, icCu." untranslated.'),
    'r097': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref "Vgl. acCAvAka, acCokti." untranslated.'),
    'r101': ('acceptable-variant', 'yellow', ['ls-loss-window-boundary', 'grammar-minor'],
             'Leading <ls>KULL.</ls> present in DE dropped from EN (window-boundary citation loss, 22->21 ls tags); "der sprach zu ihnen" (demonstrative) rendered "who spoke to them" (relative). Senses all correct.'),
    'r102': ('wrong-sense', 'yellow', ['omission-san-token'],
             'CONFIRMED in raw: the <F> footnote drops {#uc#} from "glauben wir zu {#uc#} ziehen zu muessen" -> "must be drawn in" with no target root, gutting the editorial claim. Also evidence the {#..#} token guard did not fire on footnote content.'),
    'r105': ('correct', 'blue', ['mw-verbatim-agree'],
             'EN = "to impel, incite; animate, promote"; MW has the identical wording - expected, MW descends from PW; the German (antreiben, erregen; beleben, foerdern) licenses each gloss independently. Not contamination.'),
    'r109': ('acceptable-variant', 'yellow', ['addition-latin-explication'],
             'Latin euphemism "qui semen inmisit" correctly preserved but an English explication "(one who has emitted semen)" added - unlicensed, defeats the decency convention.'),
    'r118': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref "Vgl. pratyudyAtar." untranslated.'),
    'r119': ('wrong-sense', 'blue', ['term-mistranslation-polyseme'],
             'CONFIRMED in raw: "samayam ... einen Vergleich vorschlagen" = propose a settlement/pact (samaya!); EN "to propose a comparison" picks the wrong sense of polysemous Vergleich. One wrong gloss in an otherwise excellent ~25-idiom row.'),
    'r126': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref "Vgl. uktapratyukta..." untranslated.'),
    'r127': ('acceptable-variant', 'yellow', ['addition-disambiguator'],
             '"verstreichen" -> "to elapse, to pass (of time)": the parenthetical disambiguates the English polyseme rather than adding content; German quotation "Von Sternen" correctly kept German inside the delete-instruction.'),
    'r136': ('acceptable-variant', 'yellow', ['addition-epistemic-hedge'],
             '"zu lesen" (Boehtlingk asserts the reading) rendered "should probably be read" - unlicensed hedge softens the editorial stance. All four glosses otherwise faithful.'),
    'r143': ('acceptable-variant', 'yellow', ['addition-crossref-explication'],
             '"Mit vi in 2. viSruti" -> "With vi, see under 2. viSruti": "see under" added; practical cross-ref intent preserved.'),
    'r149': ('acceptable-variant', 'yellow', ['term-weak', 'register-calque', 'de-residue'],
             '"stockend" (of fluids, SUSHR.: congealed/stagnant) rendered "halting"; "trocken gelegt" calqued "laid dry" (= drained); "<ab>Gegens.</ab>" retained beside its translation.'),
    'r150': ('acceptable-variant', 'yellow', ['structure-gloss-anchor'],
             'Gloss "machen" ("to make:") re-anchored before KATHAS. 23,94 instead of after it, attaching the gloss to the wrong example; each gloss itself correct.'),
    'r155': ('wrong-sense', 'blue', ['term-mistranslation-homograph'],
             'CONFIRMED in raw: "surAM sunoti so v. a. braut" (= brews liquor, verb brauen) rendered "{%betroth%}" - homograph trap braut(verb)/Braut(bride). Flagrant semantic error; markup intact so no deterministic gate sees it.'),
    'r170': ('acceptable-variant', 'yellow', ['de-residue-crossref'], 'Cross-ref "s. upavAsana." untranslated.'),
    # soft notes on correct fu1 rows
    'r079': ('correct', 'blue', ['markup-brace-degrade'], 'Meaning exact; {%..%} wrapper degraded to plain {..}.'),
    'r094': ('correct', 'blue', ['register-soft'], '"(lauter Synonyme)" -> "(pure synonyms)" calque; long pass-row otherwise excellent.'),
    'r096': ('correct', 'blue', ['markup-quotes'], 'Glosses right; {%..%} became ASCII quotes.'),
    'r098': ('correct', 'blue', ['mw-ours-better'], '"zur Wohnstatt waehlen" -> "to choose as a dwelling place"; MW\'s "to dwell in" is weaker than the German requires.'),
    'r100': ('correct', 'blue', ['term-apparatus-soft'], 'Giant row faithful; "nach iti cet" -> "according to" slightly misreads positional "nach".'),
    'r111': ('correct', 'blue', ['mw-verbatim-agree'], 'MW "to reach up to, reach, attain" near-verbatim - PW lineage, German licenses it.'),
    'r146': ('correct', 'blue', ['markup-page-marker'], 'Faithful; [Page4-0279] marker dropped from EN.'),
    'r151': ('correct', 'blue', ['term-apparatus-soft'], '8-gloss chain faithful; "LINGA-P. bei MUIR" -> "with MUIR" (should be "in").'),
}


def main():
    rows = [json.loads(l) for l in open(os.path.join(HERE, 'worksheet.jsonl'), encoding='utf-8') if l.strip()]
    out = os.path.join(HERE, 'en_gold_adjudication.jsonl')
    with open(out, 'w', encoding='utf-8') as f:
        for r in rows:
            ruling, dot, classes, reason = RULINGS.get(
                r['uid'], ('correct', 'blue', [], DEFAULT_REASON))
            g = dict(r)
            g.pop('mw', None)  # quote lives in worksheet.jsonl; keep gold compact
            g.update({'ruling': ruling, 'dot': dot, 'classes': classes,
                      'ruling_reason': reason,
                      'adjudicator': 'Fable 5 (claude-fable-5)', 'date': '2026-07-17'})
            f.write(json.dumps(g, ensure_ascii=False) + '\n')
    print('wrote %s (%d rows, %d explicit rulings)' % (out, len(rows), len(RULINGS)))


if __name__ == '__main__':
    main()
