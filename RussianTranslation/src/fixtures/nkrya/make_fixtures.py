#!/usr/bin/env python3
"""Regenerate the offline NKRYa selftest fixtures (H5261).

The fixtures are the official example responses from the ruscorpora/public-api docs
(docs/about-api/word-portrait/use-cases/{sketches,frequency}.md; concordance shape from
usage-examples/concordance.md), cut down to what the selftest reads, and written as
cache entries keyed exactly as nkrya_client.request_key() keys a live request. They
are doc-shaped, NOT live corpus data: no value here may be cited as NKRYa evidence.

  python src/fixtures/nkrya/make_fixtures.py

The sketch collocates below are copied from sketches.md (checkout of 23-09-2026).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
import nkrya_client as nk  # noqa: E402

# sketches.md, relation amod_S_A for «слово» (10 collocates, dice) + first nsubj_S_V row
AMOD = [("честный", 10.3028), ("последний", 9.53909), ("божий", 8.68628),
        ("добрый", 8.57147), ("ласковый", 8.44075), ("ключевой", 8.16321),
        ("русский", 8.07674), ("следующий", 7.87569), ("простой", 7.86013),
        ("единый", 7.85749)]
NSUBJ = [("звучать", 8.70832), ("означать", 8.08745), ("прозвучать", 7.42895)]


def colloc(rows):
    return [{"collocate": {"valString": {"v": w}},
             "metrics": [{"name": "dice", "value": d}]} for w, d in rows]


def portrait_payload(lemma, pos, rtype):
    return {"lemma": lemma, "corpus": {"type": "MAIN"}, "resultType": [rtype],
            "seed": nk.SEED, "pos": pos}


def word(text, hit=False):
    return {"type": "WORD" if text.strip() else "PLAIN", "text": text,
            "displayParams": {"hit": True} if hit else {}}


def snippet(tokens):
    return {"snippets": [{"sequences": [{"words": [word(t, h) for t, h in tokens]}]}]}


def write(endpoint, payload, method, response):
    key = nk.request_key(endpoint, payload)
    rec = {"request": {"endpoint": endpoint, "method": method, "payload": payload},
           "fetched_utc": "doc-example (ruscorpora/public-api), not live",
           "response": response}
    with open(os.path.join(HERE, key + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return key


def main():
    for name in os.listdir(HERE):
        if name.endswith(".json"):
            os.remove(os.path.join(HERE, name))
    keys = []
    keys.append(write("/word-portrait/", portrait_payload("слово", "S", "PORTRAIT_SKETCH"),
                      "GET", {"possiblePos": ["S"], "sketchData": {"lex": "слово", "collocates": [
                          {"collocations": colloc(AMOD), "sketchSynRelation": "amod_S_A"},
                          {"collocations": colloc(NSUBJ), "sketchSynRelation": "nsubj_S_V"}]}}))
    keys.append(write("/word-portrait/", portrait_payload("кошка", "S", "PORTRAIT_FREQUENCY"),
                      "GET", {"possiblePos": ["S", "V"],
                              "frequencyData": {"ipm": 44.0418, "category": 3}}))
    q = {"corpus": {"type": "MAIN"}, "lexGramm": nk.pair_query("чёрный", "кошка"),
         "params": {"pageParams": {"page": 0, "docsPerPage": 2, "snippetsPerDoc": 1},
                    "seed": nk.SEED}}
    doc = lambda title, toks: {"info": {"title": title}, "snippetGroups": [snippet(toks)]}
    keys.append(write("/lex-gramm/concordance", q, "POST", {
        "queryStats": {"textCount": 98, "wordUsageCount": 137},
        "groups": [{"docs": [
            doc("Doc-shaped example A (1958)",
                [("Мимо", 0), (" ", 0), ("прошла", 0), (" ", 0), ("чёрная", 1), (" ", 0),
                 ("кошка", 1), (".", 0)]),
            doc("Doc-shaped example B (2003)",
                [("Там", 0), (" ", 0), ("сидела", 0), (" ", 0), ("чёрная", 1), (" ", 0),
                 ("кошка", 1), (".", 0)])]}]}))
    print("wrote %d fixtures: %s" % (len(keys), ", ".join(keys)))


if __name__ == "__main__":
    main()
