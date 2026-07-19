#!/usr/bin/env python
"""foreign_literal_guards.py — shared Latin/French preserved-literal patterns.

B&R (and the derived PWG/PW/SCH cards) deliberately leave certain glosses untranslated
verbatim: Latin euphemisms (esp. indelicate ones, e.g. "inire feminam") and French or
scientific-Latin terms. Both the RU gate (`prompt_rule_audit.py`) and the EN gate
(`audit_window_en.py`) need to recognize these so a correctly-preserved literal is never
mistaken for untranslated German/English residue. Single source of truth so a fix to one
gate's word list is not silently missing from the other's.
"""
import re

# Latin and Romance glosses B&R deliberately leave untranslated (esp. indelicate
# euphemisms written in Latin, e.g. "inire feminam"). These must NOT be flagged as
# untranslated German/English residue -- the convention keeps them verbatim.
LATIN_WORDS = re.compile(
    r'\b(?:inire|feminam?|legere|inveteratus|convenire|coitus|coire|coeundi|'
    r'membrum|virile|penis|pudenda|futuere|mingere|venus|venere|in\s+coitu|'
    r'cum|quasi|scilicet|sic|idem|vide|sequi|obsequi)\b', re.I)

FRENCH_WORDS = re.compile(
    r"(?:\bl['’]|\b(?:une?|les?|des|du|aux?|plus|tr[eè]s|homme|femme|basse|"
    r"extraction|chose|terre|qui|dans|pour|avec|sans)\b)", re.I)

# Ambiguous single tokens that legitimately belong to BOTH the German short-word set
# (RU's GERMAN_GLOSS_WORDS / EN's DE_WORDS) and ordinary French vocabulary -- "des" is a
# German genitive/plural article ("des Todes") AND a French partitive/plural article
# ("des chevaux"). A bare hit on one of these alone, with no other unambiguous German
# marker present, is not reliable evidence of German residue when the surrounding text
# also carries other French markers (mirrors the RU "du" collision fixed 2026-07-03 for
# FRENCH_WORDS vs German "du").
AMBIGUOUS_DE_FR_WORDS = frozenset({'des'})

# FRENCH_WORDS minus "des"/"du" -- a French CONFIRMATION marker, used to decide whether a
# lone ambiguous hit ("des") sits in French context rather than German. Must exclude
# "des"/"du" itself, or checking "does this text look French" would trivially match on the
# very token being disambiguated (FRENCH_WORDS includes "des"/"du" for prompt_rule_audit's
# own foreign-vs-German classification, which is guarded the other way -- see
# looks_foreign_literal's "not GERMAN_GLOSS_WORDS.search(...)").
FRENCH_CONTEXT_WORDS = re.compile(
    r"(?:\bl['’]|\b(?:une?|les?|aux?|plus|tr[eè]s|homme|femme|basse|"
    r"extraction|chose|terre|qui|dans|pour|avec|sans)\b)", re.I)

# ---------------------------------------------------------------------------
# H1302: German PROSE-residue function words that leaked untranslated into the OUTPUT
# field (RU or EN) OUTSIDE protected markup -- citation "zu"/"bei", "mit dem <ab>acc.</ab>",
# "so v. a.", grammatical connectives ("und", "oder", "mit"), "mit Ergänzung von". German
# residue is a defect in BOTH output languages, so this list is the single shared source of
# truth for the RU gate (prompt_rule_audit.GERMAN_RESIDUE / GERMAN_GLOSS_WORDS) and the EN gate
# (audit_window_en.DE_WORDS). LANG_PARITY: SHARED (german_prose_residue_h1302).
#
# EN_SAFE excludes German/English homographs (so, als, aus, am, in, ein, kein, wie) that would
# false-positive on ordinary English text -- the EN gate unions only these. The RU gate can use
# the FULL set because none of them are legitimate Russian.
GERMAN_PROSE_RESIDUE_TOKENS = (
    'der die das den dem des dessen dieses diese dieser '
    'und oder aber auch wohl vielleicht nicht noch nur so als '
    'ein eine einer eines einem einen kein keine wie woraus du '
    'mit ohne von für bei beim nach unter statt im am zum zur aus gegen '
    'zu ziehen häufiger könnte später Ende Jmd jmdm jmdn'
).split()
# German-only tokens with no common English homograph -- safe to add to the EN residue gate.
GERMAN_PROSE_RESIDUE_EN_SAFE = (
    'und oder der des dem den dessen mit ohne von für bei beim nach unter statt '
    'zum zur gegen zu ziehen häufiger könnte später vielleicht wohl'
).split()

GERMAN_PROSE_RESIDUE = re.compile(
    r'\b(?:' + '|'.join(GERMAN_PROSE_RESIDUE_TOKENS) + r')\b', re.I)
GERMAN_PROSE_RESIDUE_EN = re.compile(
    r'\b(?:' + '|'.join(GERMAN_PROSE_RESIDUE_EN_SAFE) + r')\b', re.I)
