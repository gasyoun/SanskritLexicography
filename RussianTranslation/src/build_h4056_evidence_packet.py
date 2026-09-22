#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_h4056_evidence_packet.py — H4056 PWG evidence-demonstration packet.

The human ruling of 04-09-2026: voting is PREMATURE. First demonstrate (a)
Sanskrit vs Russian/German alignment quality, (b) actual TM use, (c) effective
use of the Sanskrit–Russian and teaching corpora — as evidence, and prove the
vote-to-store machinery in SCRATCH copies. This packet therefore:

* selects ten machine-eligible cards from the LIVE store with the real gates
  (decided-exclusion, German residue, machine flags D1/D3/D4, corpus-evidence
  quarantine, and the H3948 four-tier segmentation quarantine recomputed
  read-only) — the same predicates build_g5_review_sheet applies before a
  human would ever see a card;
* renders exactly the print-facing Russian plus the German source, citation
  apparatus, printed-page refs, machine verdicts (mechanical gates, corpus
  evidence, generation provenance) and a TM-lookup result per card;
* DISABLES every voting control and carries a visible «голосование не
  запрашивается» banner — the lock is minted with gate ``H4056-DEMO``, which
  ``apply_decisions`` PARKS: there is no production route for this packet;
* replays approve/reject/defer exports against SCRATCH copies of the review
  CSV and the store, proving stable-key routing, stale-hash refusal, and that
  the canonical store and every live surface stay byte-identical.

PUBLISH SAFETY (same as G5): the HTML embeds unpublished RU/DE from the
gitignored store → the sheet HTML is gitignored (``review/*_sheet.html``); the
committed deliverables are the metadata-only lock, this manifest, the replay
receipt and the report. No provider calls anywhere; the canonical store is
only ever read.

Run (from RussianTranslation/, in a checkout that resolves the store):
  python src/build_h4056_evidence_packet.py build [--n 10]
  python src/build_h4056_evidence_packet.py replay --manifest reports/H4056_evidence_packet_manifest.json
  python src/build_h4056_evidence_packet.py --selftest
"""
import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "pilot"))

import build_g5_review_sheet as g5              # noqa: E402 (pick, card_digest, render pieces)
import pwg_four_tier_store_impact as imp        # noqa: E402 (H3948 read-only recomputation)
from review_residue_gate import visible_german, machine_flags  # noqa: E402
from review_binding import stamp, write_lock, read_lock        # noqa: E402
from review_sheet_standard import pwg_entry_href, slp1_iast    # noqa: E402
from sheet_screening import screening_block                    # noqa: E402
from etym.card_advisory import load_crosswalk, advisory_html   # noqa: E402
from csl_pyutil import render_review_sheet                     # noqa: E402
import store_path                              # noqa: E402 (canonical store resolver)
import translation_memory as tm                # noqa: E402 (scratch TM build + lookup)
import validate_decisions                      # noqa: E402
import apply_decisions                         # noqa: E402
import run_batch                               # noqa: E402 (review-id minting, G5 columns)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

SHEET_ID = "h4056-evidence-packet-2026-09-05"
GENERATED = "2026-09-05"
GATE = "H4056-DEMO"          # apply_decisions PARKS anything that is not G5/G6
REVIEWER = "H4056-scratch-replay (agent, not human)"

REPORTS = os.path.join(RT, "reports")
MANIFEST_PATH = os.path.join(REPORTS, "H4056_evidence_packet_manifest.json")
RECEIPT_PATH = os.path.join(REPORTS, "H4056_scratch_replay_receipt.json")
REPORT_PATH = os.path.join(REPORTS, "H4056_evidence_packet_report.md")
DEFAULT_OUT = os.path.join(RT, "review", "h4056_evidence_packet_sheet.html")

NO_VOTE_CSS = """
/* H4056: voting is not requested — controls disabled */
button.vote, button.rate, button.dl, textarea.note,
.reject-label-select, .vote-state, .tally { display: none !important; }
.novote-banner { background:#4a1d1d; color:#ffe9e9; border:2px solid #b3555;
  border-radius:8px; padding:14px 18px; margin:14px 0; font-size:1.05em;
  line-height:1.5; }
.novote-banner strong { color:#fff; }
"""

NO_VOTE_BANNER = (
    '<div class="novote-banner" id="novote-banner">'
    '<strong>ЭТО НЕ ГОЛОСОВАНИЕ.</strong> Голосование не запрашивается — '
    'решение о запросе голосов будет принято человеком только после оценки '
    'доказательств выравнивания/корпусов/TM (H4056, 04-09-2026). Элементы '
    'управления голосованием отключены; apply-маршрут для этого листа '
    'заблокирован (gate %s). Пакет — демонстрация доказательств, а не запрос '
    'одобрения.</div>' % GATE)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_store(explicit=None):
    """H3948's candidate order (pwg-ru-data mirror first) — the canonical
    resolver alone points at the Windows main-tree copy, absent on this box."""
    return imp.find_store(explicit) or store_path.canonical_store(
        os.path.join(HERE, "pwg_ru_translated.jsonl"))


def load_store(path):
    rows = []
    with io.open(path, encoding="utf-8") as fh:
        for pos, line in enumerate(fh, 1):
            if line.strip():
                r = json.loads(line)
                r["_pos"] = pos
                rows.append(r)
    return rows


def review_id_of(row):
    return run_batch._store_review_id(row, row["_pos"])


def changed_key_set():
    """The H3948 four-tier segmentation quarantine, recomputed read-only."""
    old_maps, new_maps, records = imp.scan_corpus()
    changed, _per_id = imp.changed_keys(old_maps, new_maps)
    return changed, records


def screen(rows, changed):
    """The real eligibility funnel. Every excluded row is counted, none guessed."""
    funnel = {"rows": len(rows), "not_ai_translated": 0, "no_stable_identity": 0,
              "corpus_evidence_quarantine": 0, "de_missing": 0,
              "german_residue_or_machine_flags": 0,
              "h3948_segmentation_quarantine": 0,
              # H4119 P0: rows the lemma roll-up would have admitted while the SENSE
              # itself carries no evidence — counted, so the repair is auditable.
              "rollup_only_no_sense_evidence": 0}
    eligible = []
    for r in rows:
        if r.get("review_status") != "ai_translated":
            funnel["not_ai_translated"] += 1
            continue
        if not (r.get("subcard") and r.get("sense_tag") is not None):
            funnel["no_stable_identity"] += 1
            continue
        es = r.get("evidence_summary") or {}
        # H4119 P0. `evidence_summary` is the LEMMA roll-up — `annotate_evidence`
        # attaches one identical dict to every row sharing a `key1`, so
        # `supports_senses` admitted a sense on a SIBLING sense's evidence (8,584 of
        # 11,519 live rows are credited by the roll-up alone). The sense-level gate is
        # `row['evidence']`, the per-sense array; the roll-up keeps only its two
        # genuinely lemma-level roles, evidence_status and contradicts.
        sense_evidence = r.get("evidence") or []
        if not (es.get("evidence_status") == "ok" and not es.get("contradicts")):
            funnel["corpus_evidence_quarantine"] += 1
            continue
        if not sense_evidence:
            funnel["rollup_only_no_sense_evidence"] += 1
            continue
        ru, de = r.get("ru") or "", r.get("de") or ""
        if not de:
            funnel["de_missing"] += 1
            continue
        if visible_german(ru) or machine_flags(ru, de):
            funnel["german_residue_or_machine_flags"] += 1
            continue
        if r.get("key1") in changed:
            funnel["h3948_segmentation_quarantine"] += 1
            continue
        eligible.append(r)
    funnel["eligible"] = len(eligible)
    return funnel, eligible


def tm_demo(chosen, scratch_dir, store_path_):
    """Build the card TM FROM the store into scratch, then look each card up.

    The lookup IS the actual TM mechanic (content-addressed on the masked raw
    source, denylist applied): a hit means the same source re-arriving today
    resolves from TM with zero provider calls."""
    tm_out = os.path.join(scratch_dir, "translation_memory.scratch.ru.json")
    tm.build(store_path_, "ru", out=tm_out)
    deny = tm.load_denylist()
    results = {}
    for r in chosen:
        raw = (r.get("provenance") or {}).get("input_raw_sha256")
        hit = tm.lookup("ru", raw, tm=tm_out) if raw else None
        addr = "ru:%s" % raw if raw else None
        results[review_id_of(r)] = {
            "address": addr,
            "result": "hit" if hit else "miss",
            "denied": bool(addr and addr in deny["addresses"]),
            "trust_level": (hit or {}).get("trust_level"),
            "reuse_policy": (hit or {}).get("reuse_policy"),
        }
    return tm_out, results, len(deny["addresses"])


def verdict_panel(r, changed, tm_res):
    """The machine-verdict panel: mechanical gates, identity, corpus evidence,
    generation provenance, TM result. No human judgment anywhere on it."""
    es = r.get("evidence_summary") or {}
    prov = r.get("provenance") or {}

    def row(k, v):
        return "<tr><td>%s</td><td>%s</td></tr>" % (k, v)

    # H4119 P0: the SENSE's own evidence is `row['evidence']`; `supports_senses` is a
    # LEMMA roll-up shared by every sense of this key1 and must be labelled as such.
    sense_ev = r.get("evidence") or []
    supports = es.get("supports_senses") or []
    silent = es.get("silent") or []

    def _ev_html(items):
        if not items:
            return "— (у этого значения собственных свидетельств нет)"
        return "; ".join(
            "<b>%s</b> — %s%s" % (
                e.get("source"), e.get("relation"),
                (": «%s»" % e["gloss_ref"]) if e.get("gloss_ref") else "")
            for e in items)
    bits = ["<h4>Машинный вердикт и доказательства (не оценка человека)</h4>",
            "<table class=\"verdict\">"]
    bits.append(row("Механические ворота", "немецкий след: нет · машинные флаги D1/D3/D4: нет"
                    " · сегментация H3948: key1 вне изменённого набора (%d key1)"
                    % len(changed)))
    bits.append(row("Устойчивая идентичность",
                    "<code>%s</code> (печатный омоним h=%s, sense_tag=%s)"
                    % (r.get("subcard"), r.get("h"), r.get("sense_tag"))))
    bits.append(row("Печатная страница", str(r.get("page") or "н/д")))
    bits.append(row("Свидетельства ЭТОГО значения (по-сенсовые)", _ev_html(sense_ev)))
    bits.append(row("Сводка по ЛЕММЕ (не по значению; общая для всех значений "
                    "этого key1)",
                    ("поддержали ≥1 значение леммы: %s" % ", ".join(supports))
                    if supports else "—"))
    bits.append(row("Молчащие источники (уровень леммы)",
                    ", ".join(silent) if silent else "—"))
    bits.append(row("Противоречия корпусов", "нет" if not es.get("contradicts")
                    else json.dumps(es.get("contradicts"), ensure_ascii=False)))
    bits.append(row("Генерация (провенанс)",
                    "%s · %s · %s" % (prov.get("model_version") or prov.get("model"),
                                      prov.get("generator"),
                                      prov.get("generated_at"))))
    bits.append(row("TM-адрес источника",
                    "<code>%s…</code>" % (tm_res["address"] or "—")[:44]))
    bits.append(row("Результат TM-lookup",
                    ("HIT — переиспользуется без вызова провайдера (trust=%s, "
                     "policy=%s, denylist применён)" % (tm_res["trust_level"],
                                                        tm_res["reuse_policy"]))
                    if tm_res["result"] == "hit" else
                    "miss (карточка не в TM этого контура)"))
    bits.append(row("Дайджест содержимого", "<code>%s</code>" % g5.card_digest(
        r.get("ru") or "", r.get("de") or "")))
    bits.append("</table>")
    return "".join(bits)


def disable_voting(doc):
    """Deterministic string surgery: banner + CSS + keyboard-hint replacement."""
    doc = doc.replace("</style>", NO_VOTE_CSS + "</style>", 1)
    doc = doc.replace("<body>", "<body>" + NO_VOTE_BANNER, 1)
    doc = re.sub(r"Keyboard:.*?</footer>",
                 "Голосование не запрашивается: элементы управления отключены "
                 "(H4056).</footer>", doc, count=1, flags=re.S)
    return doc


def cmd_build(args):
    store_p = resolve_store(args.store)
    if not os.path.exists(store_p):
        raise SystemExit("store not found: %s" % store_p)
    store_sha = sha256_of(store_p)
    rows = load_store(store_p)
    changed, records = changed_key_set()
    funnel, eligible = screen(rows, changed)
    if len(eligible) < args.n:
        raise SystemExit(
            "only %d machine-eligible cards available (< %d requested) — "
            "exact zero/short diagnosis required, gates NOT weakened"
            % (len(eligible), args.n))
    chosen = g5.pick([{"review_id": review_id_of(r), "key1": r.get("key1") or "?",
                       "ru": r.get("ru") or ""} for r in eligible], args.n)
    by_id = {review_id_of(r): r for r in eligible}
    chosen = [by_id[c["review_id"]] for c in chosen]

    scratch = tempfile.mkdtemp(prefix="h4056_build_")
    tm_out, tm_results, deny_n = tm_demo(chosen, scratch, store_p)

    etym_cw = load_crosswalk()
    items, digests = [], {}
    for r in chosen:
        rid = review_id_of(r)
        ru, de = r.get("ru") or "", r.get("de") or ""
        digests[rid] = g5.card_digest(ru, de)
        root = (r.get("provenance") or {}).get("root") or r.get("key1") or ""
        tags = g5.cardrender.card_tags(ru)
        left, right, store_markup = g5.card_split_surfaces(ru, de, tags)
        right += advisory_html(r.get("key1") or root, etym_cw, iast=r.get("iast"))
        right += verdict_panel(r, changed, tm_results[rid])
        items.append({
            "id": rid, "filt": r.get("stratum") or "na", "facets": tags,
            "title": r.get("iast") or slp1_iast(r.get("key1") or ""),
            "title_href": pwg_entry_href(root),
            "badges": [g5._SOURCE_TYPE_RU.get(r.get("source_type"),
                                              r.get("source_type") or "?"),
                       g5._stratum_ru(r.get("stratum") or "na")],
            "question": ("Демонстрационная карточка: печатный русский вид + "
                         "немецкий источник + свидетельства. Голова не оценивается, "
                         "голос не запрашивается."),
            "panels": [], "left": left, "right": right,
            "store_markup": store_markup,
        })
    strata = sorted({it["filt"] for it in items})
    facets = g5.facet_config(items) or None
    n_deterministic = sum(v for k, v in funnel.items()
                          if k not in ("rows", "eligible"))
    config = {
        "sheet_id": SHEET_ID, "split_layout": True,
        "title": "H4056 · пакет доказательств PWG (не голосование)",
        "subtitle": ("%d карточек из %d машинно-годных (ворота: решено/немецкий/"
                     "машфлаги/корпусная карантин/H3948-сегментация; воронка: %s) — "
                     "демонстрация выравнивания, корпусов и TM. ГОЛОСОВАНИЕ НЕ "
                     "ЗАПРАШИВАЕТСЯ." % (len(items), funnel["eligible"],
                                         json.dumps(funnel, ensure_ascii=False))),
        "footer": ("Пакет доказательств H4056: печатный русский вид слева от "
                   "немецкого источника, машинные вердикты и TM-lookup на каждой "
                   "карточке. Управление голосованием отключено; любой экспорт "
                   "этого листа не имеет производственного маршрута (gate %s)."
                   % GATE),
        "approve_label": "н/д", "reject_label": "н/д",
        "filters": [(s, g5._stratum_ru(s)) for s in strata],
        "facets": facets,
        "facet_count_label": "показано {shown} из {total}",
        "facet_reset_label": "снять все пометы",
        "generated": GENERATED,
        "extra_css": g5.cardrender.EXTRA_CSS,
    }
    sc = screening_block(
        deterministic=n_deterministic, lookup=0, agent=0, human=len(items),
        evidence_path="RussianTranslation/reports/H4056_evidence_packet_manifest.json",
        rules=["already_decided_excluded", "visible_german_residue",
               "machine_flags_D1_D3_D4", "corpus_evidence_quarantine",
               "h3948_segmentation_quarantine"])
    doc = render_review_sheet(items, config, extras=True, screening=sc)
    doc = disable_voting(doc)
    doc, chash = stamp(doc)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    lock_path = write_lock(SHEET_ID, chash, [it["id"] for it in items],
                           GENERATED, gate=GATE, source_html=args.out)
    lock = json.load(io.open(lock_path, encoding="utf-8"))
    lock["item_digests"] = digests
    lock["h4056"] = {"purpose": "evidence demonstration; voting NOT requested",
                     "store_sha256": store_sha,
                     "tm_scratch_build": os.path.basename(tm_out)}
    with io.open(lock_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(lock, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    manifest = {
        "schema": "h4056-evidence-packet-manifest/v1",
        "handoff": "H4056",
        "sheet_id": SHEET_ID,
        "generated": GENERATED,
        "executor": "OxAlpha (opencode/z-ai/glm-5.3-flash)",
        "voting_requested": False,
        "lock_gate": GATE,
        "store": {"path": store_p, "sha256": store_sha, "rows": len(rows)},
        "corpus_records": records,
        "h3948_segmentation_quarantine": {
            "changed_key1": len(changed),
            "method": "pwg_four_tier_store_impact.scan_corpus/changed_keys, read-only"},
        "funnel": funnel,
        "selection": "build_g5_review_sheet.pick round-robin over sorted roots, n=%d" % args.n,
        "tm": {"method": "translation_memory.build from the store into scratch; "
                         "lookup content-addressed; canonical denylist applied read-only",
               "denylist_addresses": deny_n,
               "hits": sum(1 for v in tm_results.values() if v["result"] == "hit"),
               "misses": sum(1 for v in tm_results.values() if v["result"] == "miss")},
        "cards": [{"review_id": review_id_of(r),
                   "key1": r.get("key1"), "subcard": r.get("subcard"),
                   "sense_tag": r.get("sense_tag"), "h": r.get("h"),
                   "iast": r.get("iast"),
                   "digest16": digests[review_id_of(r)],
                   "tm": tm_results[review_id_of(r)]["result"]}
                  for r in chosen],
        "artifacts": {
            "html": {"path": os.path.abspath(args.out),
                     "content_hash": chash,
                     "committed": False,
                     "reason": "embeds unpublished store RU/DE (default-deny)"},
            "lock": os.path.relpath(lock_path, RT)},
        "provider_calls": 0,
        "canonical_store_writes": 0,
    }
    os.makedirs(REPORTS, exist_ok=True)
    with io.open(MANIFEST_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("packet: %d cards -> %s\n  %s\n  lock -> %s\n  manifest -> %s"
          % (len(items), args.out, chash, lock_path, MANIFEST_PATH))
    return 0


# ------------------------------------------------------------------ replay
G5_FIELDS = ["review_id", "severity", "ord", "key1", "key2", "review_status",
             "key_match", "placeholders_ok", "reason", "attested", "ru",
             "reviewer_id", "decision", "edit", "notes"]


def _export(path, sheet_id, chash, decided, reviewer=REVIEWER):
    doc = {"sheet_id": sheet_id,
           "generated": GENERATED,
           "decided": len([d for d in decided if d.get("decision")]),
           "content_hash": chash,
           "reviewer": reviewer,
           "items": decided}
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def cmd_replay(args):
    """Scratch-only vote-to-store replay: routing, stale refusal, no prod writes."""
    checks = []

    def check(cond, label):
        checks.append((bool(cond), label))
        print(("  ok   " if cond else "  FAIL ") + label)

    manifest = json.load(io.open(args.manifest, encoding="utf-8"))
    sheet_id = manifest["sheet_id"]
    store_p = manifest["store"]["path"]
    chash = manifest["artifacts"]["html"]["content_hash"]
    ids = [c["review_id"] for c in manifest["cards"]]
    lock = read_lock(sheet_id)
    check(lock is not None and lock["content_hash"] == chash,
          "committed lock binds the packet generation")
    check(lock.get("gate") == GATE, "lock gate is %s (no production route)" % GATE)

    prod_sha_before = sha256_of(store_p)
    scratch = tempfile.mkdtemp(prefix="h4056_replay_")
    locks_dir = os.path.join(scratch, "locks")
    os.makedirs(locks_dir, exist_ok=True)
    shutil.copy(os.path.join(locks_dir_default(), sheet_id + ".lock.json"),
                os.path.join(locks_dir, sheet_id + ".lock.json"))
    store_copy = os.path.join(scratch, "pwg_ru_translated.jsonl")
    shutil.copy(store_p, store_copy)
    review_csv = os.path.join(scratch, "_review_queue.csv")

    rows = load_store(store_copy)
    by_id = {review_id_of(r): r for r in rows}
    with io.open(review_csv, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=G5_FIELDS)
        w.writeheader()
        for rid in ids:
            r = by_id[rid]
            w.writerow({
                "review_id": rid, "severity": "", "ord": "",
                "key1": r.get("key1") or "", "key2": r.get("key2") or "",
                "review_status": r.get("review_status") or "",
                "key_match": "True" if run_batch._row_key_match(r) else "False",
                "placeholders_ok": "True" if run_batch._row_placeholders_ok(r) else "False",
                "reason": "", "attested": "", "ru": r.get("ru") or "",
                "reviewer_id": "", "decision": "", "edit": "", "notes": ""})

    # Three synthetic exports: approve / reject / defer, one third each.
    decisions = (["approve"] * 3 + ["reject"] * 3 + ["defer"] * (len(ids) - 6))
    items = [{"id": rid, "decision": d,
              "note": "scratch-replay (%s)" % d if d == "reject" else ""}
             for rid, d in zip(ids, decisions)]
    good = _export(os.path.join(scratch, "decisions_good.json"),
                   sheet_id, chash, items)

    # 1. the default route must PARK — this packet has no production apply path.
    os.environ["PWG_RU_STORE"] = store_copy
    try:
        rc_park = apply_decisions.main([good, "--locks-dir", locks_dir])
    finally:
        os.environ.pop("PWG_RU_STORE", None)
    check(rc_park == 2, "default route PARKS (gate %s, rc=2, nothing written)" % GATE)

    # 2. explicit G5 route in scratch: validate → merge → run_batch validate_review.
    os.environ["PWG_RU_STORE"] = store_copy
    try:
        rc_g5 = apply_decisions.main([good, "--locks-dir", locks_dir,
                                      "--gate", "G5", "--review-csv", review_csv])
    finally:
        os.environ.pop("PWG_RU_STORE", None)
    check(rc_g5 == 0, "explicit G5 route applies in scratch (rc=0)")
    with io.open(review_csv, encoding="utf-8-sig", newline="") as fh:
        merged = {r["review_id"]: r for r in csv.DictReader(fh)}
    routed = all(merged[rid]["decision"] ==
                 apply_decisions.G5_DECISION_MAP[d]
                 and merged[rid]["reviewer_id"] == REVIEWER
                 for rid, d in zip(ids, decisions))
    check(routed, "stable-key routing: every review_id carries exactly its "
                  "approve→approved / reject→reject / defer→needs_review")

    # 3. stale-hash negative control: tampered export must be refused untouched.
    csv_before = sha256_of(review_csv)
    stale_items = [dict(it, decision="approve") for it in items]
    stale = _export(os.path.join(scratch, "decisions_stale.json"),
                    sheet_id, "sha256:" + "f" * 64, stale_items)
    try:
        validate_decisions.validate(stale, locks_dir=locks_dir, quiet=True)
        rejected = False
    except validate_decisions.Reject as e:
        rejected = "content_hash mismatch" in str(e)
    check(rejected, "stale export refused: content_hash mismatch")
    check(sha256_of(review_csv) == csv_before,
          "rejected export changed nothing (review CSV byte-identical)")

    # 4. production surfaces untouched.
    check(sha256_of(store_p) == prod_sha_before,
          "canonical store byte-identical after the replay")
    check(scratch.startswith(tempfile.gettempdir()),
          "replay ran entirely in scratch (%s)" % scratch)

    receipt = {
        "schema": "h4056-scratch-replay-receipt/v1",
        "handoff": "H4056",
        "sheet_id": sheet_id,
        "reviewer_in_exports": REVIEWER,
        "n_ids": len(ids),
        "n_checks": len(checks),
        "n_passed": sum(1 for ok, _ in checks if ok),
        "all_passed": all(ok for ok, _ in checks),
        "checks": [{"ok": ok, "label": label} for ok, label in checks],
        "scratch_dir": scratch,
        "store_sha256_after": prod_sha_before,
    }
    os.makedirs(REPORTS, exist_ok=True)
    with io.open(RECEIPT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print("receipt -> %s" % RECEIPT_PATH)
    if not receipt["all_passed"]:
        return 1
    return 0


def locks_dir_default():
    return os.path.join(RT, "review", "locks")


def _selftest():
    import review_binding as rb
    ok = True

    def check(cond, label):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + label)
        ok = ok and bool(cond)

    # 0. H4119 P0 — the eligibility gate is the SENSE's own evidence array, never the
    #    lemma roll-up, and the panel labels the roll-up as lemma-level.
    _rollup = {"evidence_status": "ok", "contradicts": [], "silent": [],
               "supports_senses": ["koch"], "present": []}
    _base = {"review_status": "ai_translated", "subcard": "agni~~h0", "sense_tag": "1",
             "key1": "agni", "de": "Feuer", "evidence_summary": _rollup}
    with_sense = dict(_base, ru="огонь",
                      evidence=[{"source": "koch", "relation": "provides",
                                 "gloss_ref": "огонь, пламя", "match": "lemma"}])
    rollup_only = dict(_base, ru="бог огня", evidence=[])
    fun, elig = screen([with_sense, rollup_only], changed=set())
    check(len(elig) == 1 and elig[0] is with_sense,
          "screen admits only the sense carrying its OWN evidence")
    check(fun["rollup_only_no_sense_evidence"] == 1,
          "screen counts the roll-up-only row instead of silently admitting it")
    _tm = {"address": "ru:abc", "result": "miss", "denied": False,
           "trust_level": None, "reuse_policy": None}
    panel = verdict_panel(with_sense, set(), _tm)
    check("Свидетельства ЭТОГО значения" in panel,
          "panel renders the per-sense evidence array")
    check("Сводка по ЛЕММЕ" in panel, "panel labels the roll-up as lemma-level")
    check("koch</b> — provides" in panel, "panel shows the sense's relation, not a bare code")
    check("собственных свидетельств нет" in verdict_panel(rollup_only, set(), _tm),
          "a roll-up-only sense is shown as having no evidence of its own")

    # 1. disable_voting removes the visible controls from a rendered fixture.
    ru, de = g5._FIXTURE_CARDS[0]
    items = [{"id": "fix:0", "filt": "na", "title": "t", "badges": [],
              "question": "q", "facets": g5.cardrender.card_tags(ru),
              "panels": g5.card_panels(ru, de)}]
    cfg = {"sheet_id": "selftest-h4056", "title": "t", "subtitle": "s",
           "footer": "f", "approve_label": "A", "reject_label": "R",
           "filters": [("na", "na")], "generated": GENERATED}
    sc = screening_block(deterministic=0, lookup=0, agent=0, human=1,
                         evidence_path="x", rules=[])
    doc = render_review_sheet(items, cfg, extras=True, screening=sc)
    doc = disable_voting(doc)
    check(".novote-banner" in doc and "ЭТО НЕ ГОЛОСОВАНИЕ" in doc,
          "the no-vote banner is visibly present")
    check("button.vote, button.rate, button.dl, textarea.note" in doc,
          "vote/download/note controls are CSS-disabled")
    check("Keyboard: <kbd>" not in doc, "the voting keyboard hint is gone")
    check('class="vote approve"' in doc,
          "the emitter markup stays inspectable in the source (honest disable, "
          "not deletion)")

    # 2. the packet gate PARKS in apply_decisions — no production route.
    with tempfile.TemporaryDirectory() as td:
        _, chash = stamp(rb._MINI)
        write_lock("selftest-h4056", chash, ["a|1", "b|2"], GENERATED,
                   locks_dir=td, gate=GATE, force=True)
        exp = os.path.join(td, "e.json")
        _export(exp, "selftest-h4056", chash,
                [{"id": "a|1", "decision": "approve", "note": ""},
                 {"id": "b|2", "decision": None, "note": ""}])
        env = os.environ.pop("PWG_RU_STORE", None)
        try:
            rc = apply_decisions.main([exp, "--locks-dir", td])
        finally:
            if env is not None:
                os.environ["PWG_RU_STORE"] = env
        check(rc == 2, "an export bound to a %s lock parks (rc=2)" % GATE)

    # 3. a stale-hash export is refused by the validator.
    with tempfile.TemporaryDirectory() as td:
        _, chash = stamp(rb._MINI)
        write_lock("selftest-h4056", chash, ["a|1", "b|2"], GENERATED,
                   locks_dir=td, gate="G5", force=True)
        stale = os.path.join(td, "stale.json")
        _export(stale, "selftest-h4056", "sha256:" + "0" * 64,
                [{"id": "a|1", "decision": "approve", "note": ""},
                 {"id": "b|2", "decision": None, "note": ""}])
        try:
            validate_decisions.validate(stale, locks_dir=td, quiet=True)
            check(False, "stale-hash export refused")
        except validate_decisions.Reject as e:
            check("content_hash mismatch" in str(e), "stale-hash export refused")

    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build")
    b.add_argument("--n", type=int, default=10)
    b.add_argument("--store", default=None)
    b.add_argument("--out", default=DEFAULT_OUT)
    r = sub.add_parser("replay")
    r.add_argument("--manifest", default=MANIFEST_PATH)
    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.cmd == "build":
        return cmd_build(args)
    if args.cmd == "replay":
        return cmd_replay(args)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
