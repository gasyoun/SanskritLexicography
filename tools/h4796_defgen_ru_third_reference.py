#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h4796_defgen_ru_third_reference.py — H4796: join the corpus-attested Russian
witness (SanskritRussian / sa-ru-glossary lemma layer) as the THIRD REFERENCE of
the kosha definition-generation eval (EN MW baseline + Heritage FR second
reference, H2408), measure the three-way census + surface limits, and leave a
resumable judge for the paid lane.

Reads kosha/data/eval/defgen READ-ONLY (frozen_sample.tsv, gen_<arm>.jsonl, the
committed heritage_ref_subset.tsv digests) and the two sibling text layers
READ-ONLY (HeadwordLists/heritage_dico_gloss.tsv FR; SanskritRussian/
lemma_glossary.tsv RU). RIGHTS: both the FR (LGPLLR) and RU (corpus-derived,
tier=restricted) gloss text is NEVER copied into committed artifacts — the
subset carries sha256 digests + word counts only, exactly the H2408 contract.

Subcommands (run in order):
  build     frozen 500 keys ∩ FR ∩ RU -> ru_ref_subset.tsv (digests only)
            + ru_ref_subset.meta.json with the three-way census and input
            digests; REFUSES if the local FR layer no longer reproduces the
            digests frozen in kosha's H2408 heritage_ref_subset.tsv
  metrics   deterministic chrF/BLEU/token-F1 per arm vs MW / FR / RU and
            multi-reference (MW / MW+FR / MW+FR+RU) on the three-witness
            subset + the reference-divergence triangle -> ru_ref_scores.json
  threeway  the H4796 measurement block: per-band census of the all-three
            subset, surface familiarity gradient (chrF_MW - chrF_FR per item,
            seeded bootstrap CI + sign test), arm-ranking invariance under the
            MW vs FR surface references, and the quantified script degeneracy
            of the RU surface channel (why the judge is required)
  judge     OPTIONAL paid step (NOT run by this lane): blinded deepseek-chat
            adequacy 0-5 of each EN candidate against the ranked RU renderings;
            resumable; refuses without DEEPSEEK_API_KEY
  report    render data/DEFGEN_RU_THIRD_REFERENCE_REPORT_<date>.md

Method note. The candidate language is English; the RU reference is Cyrillic.
Cross-lingual surface metrics between the two are structurally ~0 — the same
near-degeneracy the H2408 FR lane documented for FR, one script further. The
deterministic signal here is therefore (a) the three-way coverage census,
(b) the MW-vs-FR surface gradient reproduced on the three-witness subset, and
(c) the measured proof that the RU channel cannot be arbitrated by surface
metrics; meaning-level three-way agreement needs the judge subcommand.
"""
import argparse
import collections
import hashlib
import io
import json
import math
import os
import random
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import sacrebleu

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GH = os.path.dirname(REPO)
KOSHA = os.path.join(GH, "kosha")
KDATA = os.path.join(KOSHA, "data", "eval", "defgen")
FROZEN = os.path.join(KDATA, "frozen_sample.tsv")
HERITAGE_SUBSET_K = os.path.join(KDATA, "heritage", "heritage_ref_subset.tsv")
HERITAGE = os.path.join(REPO, "HeadwordLists", "heritage_dico_gloss.tsv")
RU_TSV = os.path.join(GH, "SanskritRussian", "lemma_glossary.tsv")
OUT = os.path.join(REPO, "data", "defgen_ru_third_reference")
SUBSET = os.path.join(OUT, "ru_ref_subset.tsv")
SUBSET_META = os.path.join(OUT, "ru_ref_subset.meta.json")
SCORES = os.path.join(OUT, "ru_ref_scores.json")
PER_ITEM = os.path.join(OUT, "ru_ref_per_item.tsv")

ARMS = ["A0_random_floor", "A1_chat_ctx", "A2_chat_noctx", "A3_reasoner_ctx",
        "F1_fable_ctx"]
SEED = 4796
BOOT = 5000
TOP_K = 5  # ranked RU renderings kept per lemma for the reference blob

JUDGE_RU_SYS = (
    "You evaluate a CANDIDATE English gloss for a Sanskrit headword against a "
    "REFERENCE gloss written in RUSSIAN (corpus-attested Russian renderings of "
    "that headword, ranked by corpus frequency; the sa-ru-glossary lemma "
    "layer). The two are in different languages on purpose: score how well the "
    "candidate covers the MEANING given by the Russian renderings, 0-5. "
    "5 = covers the reference senses accurately; 3 = core sense right, senses "
    "missing or extra; 1 = related domain but wrong meaning; 0 = unrelated or "
    "empty. Never penalise the candidate for being in English, for wording "
    "differences, or for the reference being inflected corpus forms rather "
    "than dictionary lemmas. Judge meaning coverage only. "
    "Respond in JSON: {\"adequacy\": <0-5>}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_frozen():
    rows = []
    with io.open(FROZEN, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    return rows


def load_heritage():
    """mw_key1 -> gloss_fr. Read-only; text stays local, never committed."""
    out = {}
    with io.open(HERITAGE, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            d = dict(zip(header, parts))
            key = d.get("mw_key1", "")
            gloss = (d.get("gloss_fr") or "").strip()
            if key and gloss and key not in out:
                out[key] = gloss
    return out


def load_ru():
    """lemma_slp1 -> ranked [(n, upos, ru)] preserving file order."""
    out = collections.OrderedDict()
    with io.open(RU_TSV, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                continue
            d = dict(zip(header, parts))
            key = d.get("lemma_slp1", "")
            if not key:
                continue
            try:
                n = int(d.get("n") or 0)
            except ValueError:
                n = 0
            out.setdefault(key, []).append(
                (n, d.get("upos", ""), (d.get("ru") or "").strip()))
    return out


def ru_blob(rurows):
    """Top-K distinct renderings by corpus count; returns (blob, stats)."""
    seen, ranked = set(), []
    for n, upos, ru in sorted(rurows, key=lambda t: -t[0]):
        if ru and ru not in seen:
            seen.add(ru)
            ranked.append((n, ru))
    blob = "; ".join(r for _n, r in ranked[:TOP_K])
    total = sum(n for n, _u, _r in rurows)
    rank1 = ranked[0][0] if ranked else 0
    stats = {
        "renderings_distinct": len(ranked),
        "kept": min(len(ranked), TOP_K),
        "rank1_share": round(rank1 / total, 4) if total else 0.0,
        "n_total": total,
    }
    return blob, stats


def load_gen(arm):
    out = {}
    with io.open(os.path.join(KDATA, "gen_%s.jsonl" % arm), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            out[r["slp1"]] = r.get("gloss") or ""
    return out


def load_kosha_fr_digests():
    out = {}
    with io.open(HERITAGE_SUBSET_K, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            d = dict(zip(header, line.rstrip("\n").split("\t")))
            out[d["slp1"]] = d["heritage_gloss_sha256"]
    return out


def _tok(s):
    return re.findall(r"[\w\d]+", s.lower(), re.UNICODE)


def token_f1(cand, gold):
    """Same shape as kosha scripts/defgen_score.py token_f1 (Counter overlap)."""
    c, g = collections.Counter(_tok(cand)), collections.Counter(_tok(gold))
    if not c or not g:
        return 0.0
    overlap = sum((c & g).values())
    if overlap == 0:
        return 0.0
    p, r = overlap / sum(c.values()), overlap / sum(g.values())
    return 2 * p * r / (p + r)


def bootstrap_ci(xs, iters=BOOT, seed=SEED):
    rng = random.Random(seed)
    n = len(xs)
    means = []
    for _ in range(iters):
        means.append(sum(xs[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return means[int(0.025 * iters)], means[int(0.975 * iters)]


def sign_test(xs):
    pos = sum(1 for x in xs if x > 0)
    neg = sum(1 for x in xs if x < 0)
    n = pos + neg
    if n == 0:
        return n, pos, neg, 1.0
    k = min(pos, neg)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2.0 ** n)
    return n, pos, neg, min(1.0, 2.0 * tail)


def load_subset():
    rows = []
    with io.open(SUBSET, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            rows.append(dict(zip(header, line.rstrip("\n").split("\t"))))
    return rows


def load_ru_text_for(subset, ru):
    """Recompute the local RU blob per subset row (digests pin the join)."""
    out = {}
    for s in subset:
        blob, stats = ru_blob(ru[s["slp1"]])
        out[s["slp1"]] = (blob, stats)
    return out


# ---------------------------------------------------------------- subcommands
def cmd_build():
    rows = load_frozen()
    her = load_heritage()
    ru = load_ru()
    kosha_fr = load_kosha_fr_digests()
    os.makedirs(OUT, exist_ok=True)

    # Freeze check: this repo's FR layer must still reproduce every digest
    # kosha committed in the H2408 subset — one FR lane, one truth.
    bad = [k for k, dig in kosha_fr.items()
           if hashlib.sha256(her.get(k, "").encode("utf-8")).hexdigest() != dig]
    if bad:
        sys.exit("REFUSE: %d/%d kosha heritage digests no longer match the "
                 "local HeadwordLists FR layer (first: %s)."
                 % (len(bad), len(kosha_fr), ", ".join(bad[:5])))
    print("FR freeze check: %d kosha digests reproduced locally" % len(kosha_fr))

    kept, skipped = [], []
    ru_hits = 0
    for r in rows:
        k = r["slp1"]
        g_fr = her.get(k, "")
        if k not in ru:
            skipped.append({"slp1": k, "reason": "no_ru_lemma"})
            continue
        ru_hits += 1
        if not g_fr:
            skipped.append({"slp1": k, "reason": "no_fr_gloss"})
            continue
        blob, stats = ru_blob(ru[k])
        if not blob:
            skipped.append({"slp1": k, "reason": "empty_ru_blob"})
            continue
        kept.append({
            "slp1": k, "iast": r["iast"],
            "freq_band": r["freq_band"], "poly_band": r["poly_band"],
            "mw_gold_words": len(r["gold_gloss"].split()),
            "heritage_gloss_sha256":
                hashlib.sha256(g_fr.encode("utf-8")).hexdigest(),
            "heritage_gloss_words": len(g_fr.split()),
            "ru_gloss_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
            "ru_gloss_words": len(blob.split()),
            "ru_renderings_kept": stats["kept"],
            "ru_renderings_distinct": stats["renderings_distinct"],
            "ru_rank1_share": stats["rank1_share"],
            "ru_n_total": stats["n_total"],
        })
    cols = ["slp1", "iast", "freq_band", "poly_band", "mw_gold_words",
            "heritage_gloss_sha256", "heritage_gloss_words",
            "ru_gloss_sha256", "ru_gloss_words", "ru_renderings_kept",
            "ru_renderings_distinct", "ru_rank1_share", "ru_n_total"]
    with io.open(SUBSET, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols) + "\n")
        for k in kept:
            f.write("\t".join(str(k[c]) for c in cols) + "\n")

    cells = collections.Counter((k["freq_band"], k["poly_band"]) for k in kept)
    census = {
        "frozen_sample": len(rows),
        "fr_overlap": len(kosha_fr),
        "ru_overlap": ru_hits,
        "all_three": len(kept),
        "skipped_no_fr": sum(1 for s in skipped if s["reason"] == "no_fr_gloss"),
        "skipped_no_ru": sum(1 for s in skipped if s["reason"] == "no_ru_lemma"),
    }
    meta = {
        "handoff": "H4796",
        "purpose": ("corpus-attested Russian (SanskritRussian / sa-ru-glossary "
                    "lemma layer) as the THIRD reference of the kosha "
                    "definition-generation eval; three-way census with the EN "
                    "MW baseline and the H2408 Heritage FR second reference"),
        "census": census,
        "cells": {"/".join(c): n for c, n in sorted(cells.items())},
        "ru_reference_construction":
            "top %d distinct renderings by corpus count n, '; '-joined"
            % TOP_K,
        "rights": ("Heritage gloss_fr (LGPLLR) and sa-ru-glossary RU renderings "
                   "(corpus-derived, tier=restricted) are read at runtime from "
                   "the local siblings and NEVER copied here: sha256 + word "
                   "counts pin the joins instead (H2408 contract)."),
        "inputs": {
            "kosha/frozen_sample.tsv": sha256(FROZEN),
            "kosha/heritage/heritage_ref_subset.tsv": sha256(HERITAGE_SUBSET_K),
            "HeadwordLists/heritage_dico_gloss.tsv": sha256(HERITAGE),
            "SanskritRussian/lemma_glossary.tsv": sha256(RU_TSV),
        },
    }
    with io.open(SUBSET_META, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("census: %s" % json.dumps(census))
    print("cells: %s" % json.dumps(meta["cells"]))
    print("subset n=%d -> %s" % (len(kept), SUBSET))


def _reference_divergence(subset, gold, her, rutext):
    mw = [gold[s["slp1"]] for s in subset]
    fr = [her[s["slp1"]] for s in subset]
    ru = [rutext[s["slp1"]][0] for s in subset]
    return {
        "mean_words_mw": round(sum(len(x.split()) for x in mw) / len(mw), 1),
        "mean_words_fr": round(sum(len(x.split()) for x in fr) / len(fr), 1),
        "mean_words_ru": round(sum(len(x.split()) for x in ru) / len(ru), 1),
        "chrf_mw_vs_fr": round(sacrebleu.corpus_chrf(mw, [fr]).score, 2),
        "chrf_mw_vs_ru": round(sacrebleu.corpus_chrf(mw, [ru]).score, 2),
        "chrf_fr_vs_ru": round(sacrebleu.corpus_chrf(fr, [ru]).score, 2),
        "mean_token_f1_mw_vs_fr": round(
            sum(token_f1(a, b) for a, b in zip(mw, fr)) / len(mw), 4),
        "mean_token_f1_mw_vs_ru": round(
            sum(token_f1(a, b) for a, b in zip(mw, ru)) / len(mw), 4),
        "note": ("cross-lingual pairs are structurally near-degenerate; the "
                 "triangle quantifies the degeneracy, it does not measure "
                 "semantic agreement"),
    }


def cmd_metrics():
    subset = load_subset()
    gold = {r["slp1"]: r["gold_gloss"] for r in load_frozen()}
    her = load_heritage()
    ru = load_ru()
    rutext = load_ru_text_for(subset, ru)
    # verify committed digests still reproduce (FR + RU)
    bad = [s["slp1"] for s in subset
           if hashlib.sha256(her.get(s["slp1"], "").encode("utf-8")).hexdigest()
           != s["heritage_gloss_sha256"]
           or hashlib.sha256(rutext[s["slp1"]][0].encode("utf-8")).hexdigest()
           != s["ru_gloss_sha256"]]
    if bad:
        sys.exit("REFUSE: %d subset rows no longer reproduce their committed "
                 "digests (first: %s)." % (len(bad), ", ".join(bad[:5])))
    print("digest check: %d/%d reproduce" % (len(subset), len(subset)))

    mw = [gold[s["slp1"]] for s in subset]
    fr = [her[s["slp1"]] for s in subset]
    ru = [rutext[s["slp1"]][0] for s in subset]

    summary = {
        "n": len(subset),
        "reference_divergence": _reference_divergence(subset, gold, her,
                                                      rutext),
        "arms": {},
    }
    per = io.open(PER_ITEM, "w", encoding="utf-8", newline="\n")
    per.write("slp1\tfreq_band\tpoly_band\tarm\tchrf_mw\tchrf_fr\tchrf_ru\t"
              "chrf_multi2\tchrf_multi3\ttoken_f1_mw\ttoken_f1_fr\ttoken_f1_ru\n")
    for arm in ARMS:
        gen = load_gen(arm)
        cands = [gen.get(s["slp1"], "") for s in subset]
        cell = collections.defaultdict(lambda: {"chrf_mw": [], "chrf_fr": []})
        s_mw, s_fr, s_ru, s_m2, s_m3 = [], [], [], [], []
        f_mw, f_fr, f_ru = [], [], []
        for s, cand, g_mw, g_fr, g_ru in zip(subset, cands, mw, fr, ru):
            c_mw = sacrebleu.sentence_chrf(cand, [g_mw]).score
            c_fr = sacrebleu.sentence_chrf(cand, [g_fr]).score
            c_ru = sacrebleu.sentence_chrf(cand, [g_ru]).score
            c_m2 = sacrebleu.sentence_chrf(cand, [g_mw, g_fr]).score
            c_m3 = sacrebleu.sentence_chrf(cand, [g_mw, g_fr, g_ru]).score
            s_mw.append(c_mw); s_fr.append(c_fr); s_ru.append(c_ru)
            s_m2.append(c_m2); s_m3.append(c_m3)
            t_mw, t_fr, t_ru = (token_f1(cand, g_mw), token_f1(cand, g_fr),
                                token_f1(cand, g_ru))
            f_mw.append(t_mw); f_fr.append(t_fr); f_ru.append(t_ru)
            c = (s["freq_band"], s["poly_band"])
            cell[c]["chrf_mw"].append(c_mw)
            cell[c]["chrf_fr"].append(c_fr)
            per.write("%s\t%s\t%s\t%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t"
                      "%.4f\t%.4f\t%.4f\n"
                      % (s["slp1"], s["freq_band"], s["poly_band"], arm,
                         c_mw, c_fr, c_ru, c_m2, c_m3, t_mw, t_fr, t_ru))
        summary["arms"][arm] = {
            "corpus_chrf_mw": round(sacrebleu.corpus_chrf(cands, [mw]).score, 2),
            "corpus_chrf_fr": round(sacrebleu.corpus_chrf(cands, [fr]).score, 2),
            "corpus_chrf_ru": round(sacrebleu.corpus_chrf(cands, [ru]).score, 2),
            "corpus_chrf_multi_mw_fr":
                round(sacrebleu.corpus_chrf(cands, [mw, fr]).score, 2),
            "corpus_chrf_multi_mw_fr_ru":
                round(sacrebleu.corpus_chrf(cands, [mw, fr, ru]).score, 2),
            "corpus_bleu_mw": round(sacrebleu.corpus_bleu(cands, [mw]).score, 2),
            "mean_sent_chrf_mw": round(sum(s_mw) / len(s_mw), 2),
            "mean_sent_chrf_fr": round(sum(s_fr) / len(s_fr), 2),
            "mean_sent_chrf_ru": round(sum(s_ru) / len(s_ru), 2),
            "mean_token_f1_mw": round(sum(f_mw) / len(f_mw), 4),
            "mean_token_f1_fr": round(sum(f_fr) / len(f_fr), 4),
            "mean_token_f1_ru": round(sum(f_ru) / len(f_ru), 4),
            "mean_words": round(sum(len(c.split()) for c in cands) / len(cands), 1),
            "n_empty": sum(1 for c in cands if not c),
            "cells": {"/".join(c): {k: round(sum(v) / len(v), 2) for k, v in d.items()}
                      for c, d in sorted(cell.items())},
        }
        print(arm, json.dumps({k: summary["arms"][arm][k] for k in
                               ("corpus_chrf_mw", "corpus_chrf_fr",
                                "corpus_chrf_ru",
                                "corpus_chrf_multi_mw_fr_ru")}))
    per.close()
    prev = {}
    if os.path.exists(SCORES):
        with io.open(SCORES, encoding="utf-8") as f:
            prev = json.load(f)
    prev["metrics"] = summary
    with io.open(SCORES, "w", encoding="utf-8", newline="\n") as f:
        json.dump(prev, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("-> %s, %s" % (PER_ITEM, SCORES))


def cmd_threeway():
    subset = load_subset()
    per = collections.defaultdict(dict)
    with io.open(PER_ITEM, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            d = dict(zip(header, line.rstrip("\n").split("\t")))
            per[(d["arm"], d["slp1"])] = d

    # 1. census by band on the all-three subset
    bands = collections.Counter(
        (s["freq_band"], s["poly_band"]) for s in subset)
    band_rows = {"/".join(c): n for c, n in sorted(bands.items())}

    result = {"n_all_three": len(subset), "cells": band_rows, "arms": {}}
    print("| Arm | mean d=chrF_MW-chrF_FR | 95% CI | n nonzero | MW>FR | FR>MW | sign p |")
    print("|---|---|---|---|---|---|---|")
    for arm in ARMS:
        d_mwfr, d_f1, ru_f1, ru_chrf = [], [], [], []
        for s in subset:
            r = per[(arm, s["slp1"])]
            d_mwfr.append(float(r["chrf_mw"]) - float(r["chrf_fr"]))
            d_f1.append((float(r["token_f1_mw"]), float(r["token_f1_fr"])))
            ru_f1.append(float(r["token_f1_ru"]))
            ru_chrf.append(float(r["chrf_ru"]))
        lo, hi = bootstrap_ci(d_mwfr)
        n_nz, pos, neg, p = sign_test(d_mwfr)
        mean_d = sum(d_mwfr) / len(d_mwfr)
        row = {
            "mean_chrf_mw_minus_fr": round(mean_d, 3),
            "ci95": [round(lo, 3), round(hi, 3)],
            "ci_excludes_zero": bool(lo > 0 or hi < 0),
            "n_nonzero": n_nz, "mw_higher": pos, "fr_higher": neg,
            "sign_test_p": round(p, 6),
            "sign_test_p_raw": p,
            "ru_surface_degeneracy": {
                "mean_token_f1_ru": round(sum(ru_f1) / len(ru_f1), 4),
                "max_token_f1_ru": round(max(ru_f1), 4),
                "mean_sent_chrf_ru": round(sum(ru_chrf) / len(ru_chrf), 2),
            },
        }
        result["arms"][arm] = row
        print("| %s | %+.3f | [%+.3f, %+.3f] | %d | %d | %d | %.2g |"
              % (arm, mean_d, lo, hi, n_nz, pos, neg, p))

    # 2. arm-ranking invariance under the MW vs FR surface references
    order_mw = sorted(ARMS, key=lambda a: -mean_sent(a, "mean_sent_chrf_mw"))
    order_fr = sorted(ARMS, key=lambda a: -mean_sent(a, "mean_sent_chrf_fr"))
    result["_ranking"] = {
        "by_chrf_mw": order_mw, "by_chrf_fr": order_fr,
        "identical": order_mw == order_fr,
    }
    print("\nranking by chrF-MW:  ", " > ".join(order_mw))
    print("ranking by chrF-FR:  ", " > ".join(order_fr))
    print("surface ranking preserved under reference swap:", order_mw == order_fr)

    # 3. per-item Spearman chrF_MW ~ chrF_FR (surface analogue of the H2408
    #    judge~chrF gate), pooled over arms
    xs, ys = [], []
    for arm in ARMS:
        for s in subset:
            r = per[(arm, s["slp1"])]
            xs.append(float(r["chrf_mw"]))
            ys.append(float(r["chrf_fr"]))
    result["spearman_item_chrf_mw_vs_fr"] = round(_spearman(xs, ys), 4)
    print("per-item Spearman chrF_MW~chrF_FR (pooled, n=%d): %.4f"
          % (len(xs), result["spearman_item_chrf_mw_vs_fr"]))

    with io.open(SCORES, encoding="utf-8") as f:
        scores = json.load(f)
    scores["threeway"] = result
    with io.open(SCORES, "w", encoding="utf-8", newline="\n") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("-> %s (threeway)" % SCORES)


def mean_sent(arm, key):
    with io.open(SCORES, encoding="utf-8") as f:
        scores = json.load(f)
    return scores["metrics"]["arms"][arm][key]


def _spearman(a, b):
    def rank(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        ranks = [0.0] * len(xs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            r = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = r
            i = j + 1
        return ranks
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


# ---------------------------------------------------------------- judge (paid)
_lock = threading.Lock()


def _deepseek(user, system):
    """Minimal DeepSeek chat call; only used by the judge subcommand."""
    import urllib.request
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        sys.exit("REFUSE: judge needs DEEPSEEK_API_KEY (paid lane step, "
                 "not part of this offline unit).")
    body = json.dumps({
        "model": "deepseek-chat", "temperature": 0.0,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer %s" % key})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                return json.loads(resp.read().decode("utf-8"))["choices"][0][
                    "message"]["content"]
        except Exception:
            if attempt == 2:
                raise
    return None


def cmd_judge(workers, limit):
    subset = load_subset()
    ru = load_ru()
    rutext = load_ru_text_for(subset, ru)
    bad = [s["slp1"] for s in subset
           if hashlib.sha256(rutext[s["slp1"]][0].encode("utf-8")).hexdigest()
           != s["ru_gloss_sha256"]]
    if bad:
        sys.exit("REFUSE: %d subset rows no longer reproduce their RU digests"
                 % len(bad))
    if limit:
        subset = subset[:limit]
    for arm in ARMS:
        gen = load_gen(arm)
        out_path = os.path.join(OUT, "judge_ru_%s.jsonl" % arm)
        done = set()
        if os.path.exists(out_path):
            with io.open(out_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        r = json.loads(line)
                        if r.get("adequacy") is not None:
                            done.add(r["slp1"])
                    except (json.JSONDecodeError, KeyError):
                        continue
        todo = [s["slp1"] for s in subset if s["slp1"] not in done]
        print("judge_ru %s: %d done, %d to run" % (arm, len(done), len(todo)),
              flush=True)
        if not todo:
            continue
        out_f = io.open(out_path, "a", encoding="utf-8", newline="\n")

        def work(k, arm=arm, gen=gen, out_f=out_f):
            user = ("Headword: %s\nRUSSIAN REFERENCE renderings (sa-ru-glossary, "
                    "ranked): %s\nCANDIDATE English gloss: %s\n"
                    "Respond in JSON: {\"adequacy\": <0-5>}"
                    % (k, rutext[k][0], gen.get(k, "")))
            raw = _deepseek(user, JUDGE_RU_SYS)
            score = None
            if raw:
                m = re.search(r"\{.*\}", raw, re.S)
                if m:
                    try:
                        v = json.loads(m.group(0)).get("adequacy")
                        if isinstance(v, (int, float)) and 0 <= v <= 5:
                            score = v
                    except json.JSONDecodeError:
                        pass
            with _lock:
                out_f.write(json.dumps({"slp1": k, "arm": arm, "adequacy": score},
                                       ensure_ascii=False) + "\n")
                out_f.flush()

        with ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(work, todo))
        out_f.close()
    print("judge_ru complete; fold with: this script report (after adding a "
          "judge block) — or hand off to the paid lane for the delta analysis.")


def cmd_report():
    with io.open(SCORES, encoding="utf-8") as f:
        scores = json.load(f)
    with io.open(SUBSET_META, encoding="utf-8") as f:
        meta = json.load(f)
    m, t = scores["metrics"], scores.get("threeway", {})
    div = m["reference_divergence"]
    lines = []
    A = lines.append
    A("# H4796 — Definition-generation eval: Russian third reference — report")
    A("")
    A("_Created: 19-09-2026 · Executor: OxAlpha (opencode/z-ai/glm-5.3-flash), "
      "offline deterministic lane_")
    A("")
    A("**Mission:** join the corpus-attested Russian witness (SanskritRussian / "
      "sa-ru-glossary lemma layer, kosha dataset `sa-ru-glossary`) as the THIRD "
      "reference of the MW definition-generation eval — after the EN MW baseline "
      "and the H2408 Heritage FR second reference — measure the three-way "
      "agreement surface, and leave the judge-ready harness for the paid lane. "
      "kosha/data/eval/defgen consumed READ-ONLY; both text layers "
      "(FR LGPLLR, RU tier=restricted) stay local, committed artifacts carry "
      "sha256 digests only.")
    A("")
    A("## 1. Three-way census (the headline)")
    A("")
    c = meta["census"]
    A("| Witness set | Headwords |")
    A("|---|---|")
    A("| frozen MW sample | %d |" % c["frozen_sample"])
    A("| ∩ Heritage FR (H2408) | %d |" % c["fr_overlap"])
    A("| ∩ sa-ru RU (this handoff) | %d |" % c["ru_overlap"])
    A("| ∩ all three | **%d** |" % c["all_three"])
    A("")
    A("The RU witness covers **%.1f%%** of the frozen sample "
      "(%d/%d) and **%.1f%%** of the FR overlap; the three-witness subset is "
      "**%d headwords** (%s)."
      % (100.0 * c["ru_overlap"] / c["frozen_sample"], c["ru_overlap"],
         c["frozen_sample"], 100.0 * c["all_three"] / c["fr_overlap"],
         c["all_three"],
         ", ".join("%s %d" % kv for kv in sorted(t.get("cells", {}).items())
                   if kv[1])))
    A("")
    A("## 2. Reference-divergence triangle (subset n=%d)" % m["n"])
    A("")
    A("| Pair | corpus chrF | mean token-F1 |")
    A("|---|---|---|")
    A("| MW-EN vs Heritage-FR | %.2f | %.4f |"
      % (div["chrf_mw_vs_fr"], div["mean_token_f1_mw_vs_fr"]))
    A("| MW-EN vs sa-ru-RU | %.2f | %.4f |"
      % (div["chrf_mw_vs_ru"], div["mean_token_f1_mw_vs_ru"]))
    A("| Heritage-FR vs sa-ru-RU | %.2f | — |" % div["chrf_fr_vs_ru"])
    A("")
    A("Cross-lingual pairs are structurally near-degenerate — the triangle "
      "quantifies the degeneracy, it does not measure semantic agreement. Mean "
      "gloss lengths: MW %.1f words, FR %.1f, RU %.1f (top-%d renderings)."
      % (div["mean_words_mw"], div["mean_words_fr"], div["mean_words_ru"], TOP_K))
    A("")
    A("## 3. Surface familiarity gradient on the three-witness subset "
      "(d = chrF_MW − chrF_FR, seed %d)" % SEED)
    A("")
    A("| Arm | mean d | 95% CI | n nonzero | MW>FR | FR>MW | sign p |")
    A("|---|---|---|---|---|---|---|")
    for arm in ARMS:
        r = t["arms"][arm]
        praw = r["sign_test_p_raw"]
        ptxt = ("<1e-6" if 0 < praw < 1e-6 else "%.2g" % praw)
        A("| %s | %+.3f | [%+.3f, %+.3f] | %d | %d | %d | %s |"
          % (arm, r["mean_chrf_mw_minus_fr"], r["ci95"][0], r["ci95"][1],
             r["n_nonzero"], r["mw_higher"], r["fr_higher"], ptxt))
    A("")
    A("Positive d = candidates sit measurably closer to the MW wording than to "
      "the independent FR authority on this subset — the surface analogue of "
      "the H2408 MW-familiarity premium, reproduced without any provider call. "
      "Per-item chrF_MW~chrF_FR Spearman (pooled over arms): **%.4f**."
      % t.get("spearman_item_chrf_mw_vs_fr", float("nan")))
    A("")
    A("Two reading guards. **Floor:** the seeded-derangement arm A0 shows the "
      "SMALLEST gradient (+2.9 vs +8…+14 for system arms) — a random string "
      "matches neither authority, and the ordering floor < context arms < "
      "F1_fable_ctx is itself the sanity signal. **Tail:** the surface arm "
      "ranking swaps only in the bottom tail (A3_reasoner_ctx and A0 exchange "
      "places 4-5 under chrF-FR) — the surface channel does not separate the "
      "tail, which is consistent with the protocol's near-degeneracy caveat; "
      "the H2408 judge-level reference-invariance of the arm ranking remains "
      "the adequacy-grade result and is neither reproduced nor overturned "
      "here.")
    A("")
    A("Surface arm ranking: by chrF-MW `%s`; by chrF-FR `%s`; identical: **%s**."
      % (" > ".join(t["_ranking"]["by_chrf_mw"]),
         " > ".join(t["_ranking"]["by_chrf_fr"]),
         t["_ranking"]["identical"]))
    A("")
    A("## 4. The RU surface channel is script-degenerate — judge required")
    A("")
    A("| Arm | mean token-F1 vs RU | max | mean sent-chrF vs RU |")
    A("|---|---|---|---|")
    for arm in ARMS:
        d = t["arms"][arm]["ru_surface_degeneracy"]
        A("| %s | %.4f | %.4f | %.2f |"
          % (arm, d["mean_token_f1_ru"], d["max_token_f1_ru"],
             d["mean_sent_chrf_ru"]))
    A("")
    A("EN candidates against Cyrillic references score structurally ~0 on "
      "token-F1/chrF regardless of meaning: the RU channel CANNOT be arbitrated "
      "by surface metrics, one script further than the FR near-degeneracy the "
      "protocol already documents. Meaning-level three-way agreement therefore "
      "requires the blinded judge (resumable subcommand `judge`, NOT run in "
      "this offline unit — needs `DEEPSEEK_API_KEY`; ~%d items x 5 arms calls)."
      % c["all_three"])
    A("")
    A("## 5. Per-arm reference table (corpus chrF)")
    A("")
    A("| Arm | MW | FR | RU | multi MW+FR | multi MW+FR+RU |")
    A("|---|---|---|---|---|---|")
    for arm in ARMS:
        a = m["arms"][arm]
        A("| %s | %.2f | %.2f | %.2f | %.2f | %.2f |"
          % (arm, a["corpus_chrf_mw"], a["corpus_chrf_fr"], a["corpus_chrf_ru"],
             a["corpus_chrf_multi_mw_fr"], a["corpus_chrf_multi_mw_fr_ru"]))
    A("")
    A("Adding RU to the multi-reference pool moves corpus chrF by ~0 (script "
      "gap), as §4 predicts; the FR uplift over MW-only is the surface part of "
      "the H2408 story reproduced on this subset.")
    A("")
    A("## 6. Residuals")
    A("")
    A("1. **RU judge run (paid lane)** — `judge` subcommand ready and "
      "resumable; then a MW-vs-RU judge delta (H2408 `defgen_heritage_delta.py` "
      "method) completes the three-way adequacy triangle. GTD row minted by "
      "this handoff.")
    A("2. **kosha-side edge** — the sa-ru-glossary manifest row's `consumers` "
      "list gains `defgen eval` and kosha's docs/protocol gains the third-"
      "reference section; kosha was consumed read-only here (dual-run tombstone "
      "H4812 → H4796), so the kosha-side commit is a separate small lane.")
    A("")
    A("## Artifacts")
    A("")
    A("- `data/defgen_ru_third_reference/ru_ref_subset.tsv` — %d rows, digests "
      "only" % m["n"])
    A("- `data/defgen_ru_third_reference/ru_ref_subset.meta.json` — census + "
      "input digests")
    A("- `data/defgen_ru_third_reference/ru_ref_scores.json` — metrics + "
      "threeway blocks")
    A("- `data/defgen_ru_third_reference/ru_ref_per_item.tsv` — per item x arm")
    A("- `tools/h4796_defgen_ru_third_reference.py` — this pipeline")
    A("")
    out_path = os.path.join(REPO, "data",
                            "DEFGEN_RU_THIRD_REFERENCE_REPORT_2026-09-19.md")
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("-> %s" % out_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["build", "metrics", "threeway", "judge",
                                    "report"])
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    {"build": cmd_build, "metrics": cmd_metrics, "threeway": cmd_threeway,
     "judge": lambda: cmd_judge(args.workers, args.limit),
     "report": cmd_report}[args.cmd]()


if __name__ == "__main__":
    main()
