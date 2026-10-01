#!/usr/bin/env python
"""build_c2p2_dating_sheet.py — the eleven C2 phase-2 dating decisions as one review sheet.

H3790's curated per-work dating table
([research/C2P2_WORK_DATING_TABLE.md](../research/C2P2_WORK_DATING_TABLE.md),
data in [work_dating_table.json](work_dating_table.json)) leaves eleven questions that
evidence cannot settle: where named scholars hold materially different positions, or where
the project must choose a convention. The roadmap's C2 ruling is explicit that these become
decisions rather than being self-ruled, and the org rule is that a batch of decisions reaches
a human as ONE interactive sheet, never as a table in chat.

Each card proposes ONE reading in a full sentence. Approve = adopt it. Reject = take the
named alternative, which the reject-label select spells out — no bare option letters.

  python build_c2p2_dating_sheet.py [--out ../review/sanskritlexicography-c2p2-work-dating_11.html]

H3790 · Opus 5 (claude-opus-5) · 01-09-2026
"""
import html
import json
import os
import sys

from csl_pyutil import render_review_sheet
from csl_pyutil.evidence import EvidenceManifest
from sheet_screening import screening_block
from review_binding import stamp, write_lock
from review_sheet_standard import standard_config

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
SHEET_ID = 'c2p2-work-dating-2026-09-01'
GENERATED = '2026-09-01'

TABLE = os.path.join(HERE, 'work_dating_table.json')
MAP = os.path.join(HERE, 'ls_source_map.json')


def esc(s):
    return html.escape(str(s) if s is not None else '')


# Per decision: the fork in one sentence, the two readings as full sentences (never letters),
# the evidence a human needs to choose, the recommendation, and what would reverse it.
CARDS = {
    'C2P2-D1': {
        'title': 'Ṛgveda — which end of the composition span anchors a window',
        'fork': 'The Ṛgveda was composed over roughly five centuries and collected later. '
                'A window needs one number for its earliest bound.',
        'propose': 'Anchor ṚV at the start of the composition span, c. 1500 BCE, so that '
                   '«earliest» means the earliest the cited material could exist.',
        'reject_label': 'Anchor at the collection instead (c. 1000 BCE), so «earliest» means '
                        'the earliest the text as Böhtlingk-Roth read it existed',
        'evidence': [
            'Witzel 1995 places the hymns, principally the family books II–VII, at c. 1500–1200 BCE.',
            'Witzel 1997 places the saṃhitā as collected at c. 1200–1000 BCE.',
            'ls_source_map.json currently uses 1125 BCE — inside the span, but neither end of it.',
            'ṚV carries 56,218 citations, more than any other siglum: this bound propagates further '
            'than any other single choice in the table.',
        ],
        'recommend': 'Take the composition start (1500 BCE). An attestation window is a lower bound '
                     'on when the cited language existed, and the redaction date understates that.',
        'reverses': 'A decision that windows should describe the books Böhtlingk-Roth held rather '
                    'than the language they contain.',
    },
    'C2P2-D2': {
        'title': 'Mahābhārata and Rāmāyaṇa — full growth span, or a conventional point',
        'fork': 'Both epics grew over some eight centuries. Phase 1 gave each a single point '
                'date (80 CE and 70 CE), which is a date nobody defends for either.',
        'propose': 'Enter both epics as their full spans — MBh 400 BCE – 400 CE, Rām 400 BCE – '
                   '300 CE — so a window that rests on an epic visibly says «somewhere in eight '
                   'centuries» rather than pretending to a year.',
        'reject_label': 'Keep a single conventional point date per epic and record the span only '
                        'as a note',
        'evidence': [
            'Brockington 1998 gives roughly 400 BCE – 400 CE for the Mahābhārata\'s growth, with '
            'layers distinguishable on linguistic grounds.',
            'Hiltebeitel 2001 argues instead for a compressed composition around 150 BCE – 0 CE.',
            'MBH carries 67,238 citations and R another 37,806: together the two largest dated '
            'sources in the map.',
            'A span makes many windows very wide; a point makes them precise and wrong.',
        ],
        'recommend': 'Take the full spans. The project\'s whole honesty contract is that a window '
                     'is a bound, not a date; a fake point date is the one thing the contract '
                     'forbids.',
        'reverses': 'Evidence that a downstream consumer needs a single sortable number per work '
                    'and cannot carry an interval.',
    },
    'C2P2-D3': {
        'title': 'Pāṇini — mid-5th or mid-4th century BCE',
        'fork': 'The Aṣṭādhyāyī\'s date has a standing century of slack, and P carries 25,291 '
                'citations.',
        'propose': 'Carry Pāṇini as the range 500–350 BCE rather than committing to either end.',
        'reject_label': 'Commit to the 4th-century date (c. 350 BCE) as the project\'s working '
                        'position',
        'evidence': [
            'Cardona 1997 surveys the evidence; the surviving bracket is mid-5th to mid-4th century BCE.',
            'Scharfe 1977 places Pāṇini in the 4th century within the history of grammatical literature.',
            'ls_source_map.json uses 400 BCE, a midpoint of the two.',
            'Separately: the map labels P\'s period «Vedic (Brāhmaṇa–Upaniṣad)» while giving it Renou '
            'class II — an inconsistency inherited from phase 1 and not corrected by this table.',
        ],
        'recommend': 'Carry the range. Nothing downstream needs the extra precision, and the range '
                     'is what the survey literature actually supports.',
        'reverses': 'A citation-level use that must sort Pāṇini against a 5th-century work.',
    },
    'C2P2-D4': {
        'title': 'Yāska\'s Nirukta — pre-Pāṇinian, or later',
        'fork': 'Whether Yāska precedes Pāṇini moves the Nirukta by up to three centuries.',
        'propose': 'Carry NIR as 700–400 BCE, a range wide enough to hold both positions, and '
                   'do not treat it as a fixed pre-Pāṇinian anchor.',
        'reject_label': 'Adopt the early pre-Pāṇinian date (c. 700 BCE) as the project position',
        'evidence': [
            'Sarup 1920–27 places Yāska well before Pāṇini, around the 7th century BCE.',
            'Kahrs 1998 treats the nirvacana tradition as a continuum and is markedly more cautious '
            'about a single early date for the Nirukta as transmitted.',
            'NIR carries 3,678 citations — material, but far from the largest.',
        ],
        'recommend': 'Carry the range. The early date rests on the tradition rather than on '
                     'independent evidence.',
        'reverses': 'A study that specifically needs the Nirukta as a pre-Pāṇinian datum.',
    },
    'C2P2-D5': {
        'title': 'Yājñavalkya-Smṛti — Kane\'s early date or Olivelle\'s late one',
        'fork': 'Two standard authorities barely overlap: Kane puts it in the 1st–3rd century CE, '
                'Olivelle in the 4th–5th.',
        'propose': 'Follow Olivelle 2019 and carry YĀJÑ as 300–500 CE, later than Manu.',
        'reject_label': 'Follow Kane\'s History of Dharmaśāstra and keep the 1st–3rd century CE '
                        'placement',
        'evidence': [
            'Kane 1930–62 places the Yājñavalkya-Smṛti in the early centuries CE.',
            'Olivelle 2019 argues on textual and legal-historical grounds for the 4th–5th century, '
            'later than the Mānava-Dharmaśāstra.',
            'The project already follows Olivelle 2005 for Manu, so following Kane here would mean '
            'mixing two dharmaśāstra chronologies.',
            'YĀJÑ carries 4,004 citations.',
        ],
        'recommend': 'Follow Olivelle, for internal consistency with the Manu row and because his '
                     'is the later critical treatment.',
        'reverses': 'A specialist reading of the relative chronology that puts Yājñavalkya before Manu.',
    },
    'C2P2-D6': {
        'title': 'Amarakośa — the standard reference calls the date unsolved',
        'fork': 'Vogel 1979 says in as many words that Amarasiṃha\'s date «has not been solved to '
                'the present day». The map nevertheless gives 450 CE, and 16,156 citations rest on it.',
        'propose': 'Carry AK as the wide range 400–700 CE and label it contested, rather than '
                   'keeping a confident-looking 450.',
        'reject_label': 'Keep a single working date of 450 CE and note the uncertainty only in prose',
        'evidence': [
            'Vogel 1979: 309–310 — «The problem of his date has occupied the minds of Sanskritists '
            'since Paolino da San Bartolomeo (1748–1805) but has not been solved to the present day.»',
            'The indigenous tradition placing Amarasiṃha among Vikramāditya\'s nine jewels «would '
            'have made him a contemporary of the astronomer Varāhamihira, who lived in the 6th century» '
            '(Vogel 1979: 310).',
            'This quote is re-readable without a library: Vogel is held in this repository.',
            'AK is the fourth-largest dated source in the map.',
        ],
        'recommend': 'Take the wide range. This is the clearest case in the table of a '
                     'confident-looking number with no scholarly warrant behind it.',
        'reverses': 'A later study that actually settles Amarasiṃha\'s date.',
    },
    'C2P2-D7': {
        'title': 'Kālidāsa — the Gupta consensus, or the minority early date',
        'fork': 'Four sigla (Kumārasambhava, Meghadūta, Raghuvaṃśa, Abhijñānaśākuntala) move '
                'together on one author\'s date.',
        'propose': 'Follow the Gupta consensus and carry all four as 375–470 CE.',
        'reject_label': 'Treat the Vikramāditya-era early date (1st century BCE) as live and widen '
                        'all four ranges to hold it',
        'evidence': [
            'Lienhard 1984 places Kālidāsa in the Gupta period, c. 400–450 CE.',
            'Warder\'s Indian Kāvya Literature surveys the competing placements including the '
            'minority Vikramāditya attachment.',
            'The four sigla carry 2,692 + 2,363 + 9,728 + 6,587 = 21,370 citations between them.',
            'Phase 1 already used 420 CE for all four, which is inside the Gupta consensus.',
        ],
        'recommend': 'Follow the Gupta consensus. The early date is a minority position resting on '
                     'the same Vikramāditya legend that Vogel treats sceptically for Amarasiṃha.',
        'reverses': 'Nothing currently in view; this is the least live of the eleven.',
    },
    'C2P2-D8': {
        'title': 'Suśruta-Saṃhitā — early core or later redaction as the anchor',
        'fork': 'The Suśruta is a stratified medical text: an old core, a later Uttaratantra, and '
                'a redaction. Phase 1 anchored it at the redaction (400 CE).',
        'propose': 'Carry SUŚR as 200 BCE – 500 CE, spanning core to redaction, so a window resting '
                   'on it does not silently claim the whole text is 5th-century.',
        'reject_label': 'Keep the redaction date (c. 400 CE) as the single anchor',
        'evidence': [
            'Meulenbeld 1999–2002 describes an early core reaching back to the last centuries BCE, '
            'an Uttaratantra added later, and a redaction attributed to Nāgārjuna.',
            'SUŚR carries 12,450 citations, and PWG\'s citations do not distinguish the strata.',
            'The C2P1 hand-check sample shows two senses whose entire window is «400…400» from '
            'Suśruta alone — a false precision the span would remove.',
        ],
        'recommend': 'Take the span, on the same reasoning as the epics: PWG cites the work, not a '
                     'stratum, so the window cannot be narrower than the work.',
        'reverses': 'A citation-level mapping that could tell Suśruta strata apart — none exists today.',
    },
    'C2P2-D9': {
        'title': 'Purāṇas — does the project date them at all',
        'fork': 'Rocher\'s standing point is that a Purāṇa is a continuously re-edited text and '
                'cannot be dated as a whole. Three sigla (VP, MĀRK. P, BHĀG. P) are affected.',
        'propose': 'Keep dated ranges for the three Purāṇas but mark them explicitly as '
                   'redaction-band estimates carrying Rocher\'s caveat, not composition dates.',
        'reject_label': 'Treat the Purāṇas as undated for windowing purposes, the way Spr. and '
                        'ŚKDR. would be under D10',
        'evidence': [
            'Rocher 1986 is the standard reference and its caution is methodological, not a gap in '
            'the evidence.',
            'Hardy 1983 nevertheless supports a 9th–10th century South Indian placement for the '
            'Bhāgavata specifically.',
            'The three carry 3,677 + 6,419 + 30,483 = 40,579 citations; BHĀG. P alone is the '
            'third-largest dated source and sets many windows\' latest bound.',
            'Dropping them would push 30k+ citations into the undated bucket.',
        ],
        'recommend': 'Keep them with the caveat. Rocher\'s point argues against precision, not '
                     'against any estimate, and the coverage cost of dropping them is severe.',
        'reverses': 'A finding that Purāṇa citations in PWG are systematically drawn from late '
                    'recensions.',
    },
    'C2P2-D10': {
        'title': 'Spr. and ŚKDR. — two sigla that cannot date anything',
        'fork': '«Spr.» is Böhtlingk\'s own 1863–1873 anthology and «ŚKDR.» a Calcutta compilation '
                'of 1821–1858. Both were given ordinary point dates (600 CE and 1830 CE) in phase 1 '
                'and both therefore set window bounds that mean nothing about the language.',
        'propose': 'Exclude both from window computation entirely, keeping them in the store as '
                   'citations with dating_valid false.',
        'reject_label': 'Keep both in the window but flag every affected window as carrying a '
                        'known-invalid bound',
        'evidence': [
            'Indische Sprüche is the PWG editor\'s own anthology; its verses span the whole of '
            'Sanskrit literature, so the anthology\'s date bounds nothing (Sternbach 1974).',
            'The Śabdakalpadruma was printed in Böhtlingk-Roth\'s own lifetime; its 1830 date is a '
            'publication fact, not a language fact.',
            'Measured on phase 1\'s store: 11,771 of 43,990 windows (26.8%) contain one of the two — '
            '7,508 cite ŚKDR., 4,653 cite Spr.',
            '2,873 windows have NO other dated work: excluding the two makes those windows vanish '
            'rather than shrink.',
            '9,082 windows have their latest bound set by one of the two.',
        ],
        'recommend': 'Exclude. A window with a false bound is worse than a missing window, and the '
                     '2,873 that would vanish were never carrying information in the first place.',
        'reverses': 'A downstream consumer that needs maximal window coverage and can tolerate a '
                    'flagged bad bound.',
    },
    'C2P2-D11': {
        'title': 'Siglum identity — one work cited under several sigla',
        'fork': 'BHAG and GĪT are both the Bhagavadgītā. R, R. GORR and R. SCHL are three printed '
                'editions of one Rāmāyaṇa. Phase 1 counts each siglum as a separate dated work.',
        'propose': 'Collapse them for counting: n_dated_works should count WORKS, so the Gītā '
                   'counts once and the Rāmāyaṇa once however many editions a sense cites.',
        'reject_label': 'Keep counting sigla, and rename the field so it says sigla rather than works',
        'evidence': [
            'Gorresio 1843–1858 and Schlegel 1829–1846 are 19th-century editions of the Bengal and '
            'Northern recensions; PWG cites them because its editors read them.',
            'The dates are identical across each group, so bounds do not change — only n_dated_works '
            'does, and it is used as a confidence signal.',
            'Affected volumes: BHAG 2,584 + GĪT 1,207; R 37,806 + R. GORR 7,145 + R. SCHL 246.',
            'A sense citing R and R. GORR currently reports two dated works and looks better '
            'corroborated than one citing R alone.',
        ],
        'recommend': 'Collapse for counting. The field is read as «how many independent works '
                     'attest this», and two editions of one epic are not two witnesses.',
        'reverses': 'A use of n_dated_works purely as a citation-density proxy, where sigla are the '
                    'right unit.',
    },
}


def sort_key(did):
    tail = did.rsplit('-D', 1)[-1]
    return (int(tail) if tail.isdigit() else 0, did)


def bullets(items):
    return '<ul style="margin:0;padding-left:18px">%s</ul>' % ''.join(
        '<li style="margin-bottom:4px">%s</li>' % esc(x) for x in items)


def build_item(did, card, table, source_map):
    works = table['works']
    sigla = sorted(s for s, r in works.items() if r.get('decide') == did)
    rows = []
    for s in sigla:
        r = works[s]
        rows.append('<li><b>%s</b> — %s · curated %s…%s · phase-1 point %s · %s citations</li>' % (
            esc(s), esc(r['name']), esc(r['earliest']), esc(r['latest']),
            esc(r['map_date']), '{:,}'.format(source_map[s]['citations'])))
    refs = sorted({src['ref'] for s in sigla for src in works[s]['sources']})
    bib = ''.join('<li><b>%s</b> — %s</li>' % (esc(k), esc(table['sources'][k]['citation']))
                  for k in refs)

    # V13 identity gate: no reviewer sees a bare PWG siglum. Every siglum this card
    # moves is expanded in the question itself, in the fixed «· SIGLUM = Work» form
    # the gate's pattern reads.
    identity = ' '.join('· %s = %s' % (esc(s), esc(works[s]['name'])) for s in sigla)

    question = ('<b>%s</b>'
                '<div class="muted" style="margin-top:6px;font-weight:normal">%s</div>'
                '<div style="margin-top:8px">Approve = <b>%s</b></div>'
                '<div class="muted" style="margin-top:8px;font-weight:normal">'
                'Sigla in this card %s</div>'
                % (esc(card['title']), esc(card['fork']), esc(card['propose']), identity))

    panels = [
        ('What the evidence says', bullets(card['evidence'])),
        ('Recommendation',
         '<div>%s</div><div class="muted" style="margin-top:6px">Would be reversed by: %s</div>'
         % (esc(card['recommend']), esc(card['reverses']))),
        ('Sigla this decision moves (%d)' % len(sigla),
         '<ul style="margin:0;padding-left:18px">%s</ul>' % ''.join(rows)),
        ('Sources cited on these rows', '<ul style="margin:0;padding-left:18px">%s</ul>' % bib),
    ]
    return {
        'id': did,
        'filt': 'contested' if any(works[s]['confidence'] == 'contested' for s in sigla) else 'convention',
        'title': card['title'],
        'badges': ['%d sigla' % len(sigla),
                   '{:,} citations'.format(sum(source_map[s]['citations'] for s in sigla))],
        'question': question,
        'panels': panels,
    }


def main():
    args = sys.argv[1:]
    out_path = os.path.normpath(os.path.join(
        HERE, '..', 'review', 'sanskritlexicography-c2p2-work-dating_11.html'))
    i = 0
    while i < len(args):
        if args[i] == '--out':
            out_path = args[i + 1]; i += 2
        else:
            raise SystemExit('unknown option: %s' % args[i])

    with open(TABLE, encoding='utf-8') as fh:
        table = json.load(fh)
    with open(MAP, encoding='utf-8') as fh:
        source_map = json.load(fh)

    missing = sorted(set(table['decisions']) - set(CARDS))
    if missing:
        raise SystemExit('no card written for decision(s): %s' % ', '.join(missing))
    stray = sorted(set(CARDS) - set(table['decisions']))
    if stray:
        raise SystemExit('card(s) for decisions absent from the table: %s' % ', '.join(stray))

    works = table['works']
    items = [build_item(d, CARDS[d], table, source_map)
             for d in sorted(table['decisions'], key=sort_key)]

    # V9 evidence manifest (H1889): say what was joined onto these cards and what was
    # deliberately left out, so the sheet cannot ask a human what the repo already answers.
    manifest = EvidenceManifest(SHEET_ID, [it['id'] for it in items],
                                repo_root=os.path.normpath(os.path.join(HERE, '..', '..')))
    manifest.declare_joined(
        'RussianTranslation/src/work_dating_table.json',
        ['earliest', 'latest', 'confidence', 'sources', 'map_date_conflict', 'decide'])
    manifest.declare_joined(
        'RussianTranslation/src/ls_source_map.json',
        ['date', 'citations', 'name', 'genre', 'period', 'renou'])
    manifest.declare_omitted_path(
        'RussianTranslation/src/pwg_sense_attestation_window.jsonl',
        'Read read-only to measure the D10 impact figures quoted on that card. The per-sense '
        'rows are not per-decision evidence, and H3790 forbids re-deriving this store.')
    manifest.declare_omitted_path(
        'RussianTranslation/research/C2P2_WORK_DATING_TABLE.md',
        'The human render of work_dating_table.json, which is joined above; joining the memo '
        'too would double-count the same facts.')
    manifest.declare_omitted(
        'page-level verification of the reference-only sources',
        'Only Vogel 1979 is held in this repository. The other handbooks are cited by author, '
        'year and title but not checked against the printed page from here — that residual is '
        'stated on the table, and no card turns on a page number.')

    config = {
        'sheet_id': SHEET_ID,
        'title': 'C2 phase 2 — the eleven dating decisions the evidence cannot settle',
        'subtitle': ('Curated per-work dating table for PWG\'s 45 cited works (H3790). Each card '
                     'proposes one reading in a full sentence; approving adopts it, rejecting takes '
                     'the named alternative. Nothing here is a claim about when a SENSE emerged.'),
        'footer': ('Approve = adopt the proposal as the project\'s working position. Reject = take '
                   'the alternative named in the select. Every range in the underlying table carries '
                   'a scholarly citation; a date without one would be a gap, not a guess.'),
        'approve_label': 'Adopt the proposal',
        'reject_label': 'Take the alternative',
        'reject_labels': [(d, CARDS[d]['reject_label'])
                          for d in sorted(table['decisions'], key=sort_key)],
        'filters': [('contested', 'scholars disagree'), ('convention', 'project convention')],
        'generated': GENERATED,
        # V13 (H2854). The pattern reads only the «· SIGLUM = Work» identity line each
        # question ends with, so a single letter like `P` or `R` cannot match loose prose.
        'identity_gate': {
            'patterns': [r'(?<=· )[^=·]+?(?= = )'],
            'labels': {s: works[s]['name'] for s in works},
        },
        # The SLP1-in-human-text detector fires on any Latin word containing `f` or `z`,
        # both of which are legal SLP1 characters. Everything allowed here is a scholar's
        # surname, an ordinary English word, or the standard abbreviation for the
        # Mahābhārata — none of it is transliteration.
        'preflight': {
            'allow_slp1_tokens': ('Alf', 'Harrassowitz', 'MBh', 'Scharfe', 'Siegfried',
                                  'Witzel', 'confidence', 'confident', 'conflicts',
                                  'information'),
        },
    }
    config.update(standard_config(
        save_as='RussianTranslation\\review\\%s_decisions.json' % SHEET_ID))

    doc = render_review_sheet(
        items, config, extras=True, manifest=manifest,
        screening=screening_block(
            deterministic=0, lookup=0, agent=0, human=len(items),
            evidence_path='RussianTranslation/research/C2P2_WORK_DATING_TABLE.md',
            rules=['Every evidence-decidable row was applied to work_dating_table.json and '
                   'reported, not voted: the seven map-date conflicts (AMAR, GĪT. GOV, KATHĀS, '
                   'RĀJAN, Spr, SĀH. D, VOP) are corrections carrying a citation, and no card '
                   'asks about them.',
                   'The eleven cards here are the residue: where named scholars disagree, or '
                   'where the project must pick a convention no evidence can decide.']))
    doc, chash = stamp(doc)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(doc)
    write_lock(SHEET_ID, chash, [it['id'] for it in items], GENERATED, source_html=out_path)
    print('wrote %d cards -> %s (sheet_id %s)' % (len(items), out_path, SHEET_ID))


if __name__ == '__main__':
    main()
