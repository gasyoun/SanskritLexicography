#!/usr/bin/env python3
"""Offline-first Sanskrit e-text scanner — H8429 adoption move 3.

Ports the CLLG-Scanner *pattern* (import -> document -> mask -> local OCR ->
resumable per-page cache -> review -> structured TEI) to printed Sanskrit.
Original code; no CLLG source copied. DEFAULT and SMOKE are local-only.

_Created: 18-11-2026 · Last updated: 18-11-2026_
_Dr. Mārcis Gasūns_
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import shutil
import socket
import sys
import tempfile
import unicodedata
import urllib.request
from pathlib import Path

import engines
import pattern as P


class NetworkAccessError(RuntimeError):
    """Raised when code tries to open a socket inside the local-only guard."""


@contextlib.contextmanager
def offline_guard():
    """Fail closed if anything in the block attempts a network connection."""
    def deny(*_a, **_k):
        raise NetworkAccessError("local-only contract: network access attempted")
    saved = (socket.socket.connect, socket.socket.connect_ex,
             socket.create_connection, urllib.request.urlopen,
             urllib.request.urlretrieve)
    socket.socket.connect = deny            # type: ignore[assignment]
    socket.socket.connect_ex = deny         # type: ignore[assignment]
    socket.create_connection = deny         # type: ignore[assignment]
    urllib.request.urlopen = deny           # type: ignore[assignment]
    urllib.request.urlretrieve = deny       # type: ignore[assignment]
    try:
        yield
    finally:
        (socket.socket.connect, socket.socket.connect_ex,
         socket.create_connection, urllib.request.urlopen,
         urllib.request.urlretrieve) = saved


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() and (parent / "CHANGELOG.md").exists():
            return parent
    raise P.PatternError("cannot locate repository root")


def default_sample() -> Path:
    """A real printed Monier-Williams page (p. 277) already in the estate."""
    p = repo_root() / "EntryAnatomy" / "assets" / "mw_kala_p277.jpg"
    if not p.is_file():
        raise P.PatternError(f"real-print smoke fixture missing: {p}")
    return p


# ------------------------------------------------------------------- commands
def cmd_import(args) -> int:
    project = Path(args.project)
    if project.exists() and list(project.glob("pages/page_*.png")) and not args.force:
        raise P.PatternError(f"{project} already has pages; pass --force to re-import")
    data = P.new_project(args.kind, args.source, dpi=args.dpi, script=args.script,
                         lang=args.lang, psm=args.psm, backend=args.backend)
    with offline_guard():
        if args.kind == "pdf":
            sel = P.render_pdf(args.source, project, pages=args.pages, dpi=args.dpi)
        elif args.kind == "images":
            sel = P.import_images(args.source, project, pages=args.pages)
        elif args.kind == "alto":
            xml = Path(args.source).read_text(encoding="utf-8")
            lines = P.parse_alto_lines(xml)
            sel = P.parse_selection(args.pages, 1)
            if not args.alto_image:
                raise P.PatternError("alto import needs --alto-image <page image>")
            shutil.copyfile(args.alto_image, P.page_path(project, sel[0]))
            data["pages"] = [{"n": sel[0], "alto_lines": lines}]
        else:
            raise P.PatternError(f"unknown source kind: {args.kind}")
        if args.kind != "alto":
            data["pages"] = [{"n": n, "mask": [], "status": "imported"} for n in sel]
    if args.title:
        data["bibliography"]["title"] = args.title
    if args.author:
        data["bibliography"]["author"] = args.author
    if args.source_citation:
        data["bibliography"]["source"] = args.source_citation
    P.save_project(project, data)
    print(json.dumps({"project": str(project), "pages": [p["n"] for p in data["pages"]],
                      "kind": args.kind}, ensure_ascii=False))
    return 0


def cmd_ocr(args) -> int:
    data = P.load_project(args.project)
    engine = data["engine"]
    backend = args.backend or engine["backend"]
    targets = P.parse_selection(args.pages, len(data["pages"]))
    result = []
    with offline_guard() if backend == "tesseract" else contextlib.nullcontext():
        for n in targets:
            if P.cache_path(args.project, n).exists() and not args.force:
                result.append({"page": n, "status": "cached"})
                continue
            masks = next((p.get("mask", []) for p in data["pages"] if p["n"] == n), [])
            src = P.page_path(args.project, n)
            if masks:
                src = P.apply_mask(src, masks, P.masked_path(args.project, n))
            if backend == "tesseract":
                raw = engines.ocr_tesseract(src, lang=args.lang or engine["lang"],
                                            psm=args.psm or engine["psm"])
                lines = P.lines_from_tsv(raw)
            elif backend == "vlm":
                raw = engines.ocr_vlm(src, accept_network=args.remote,
                                      consent=args.accept_network or "")
                lines = list(enumerate([t for t in raw.splitlines() if t.strip()], 1))
            else:
                raise P.PatternError(f"unknown backend: {backend}")
            P.write_page_cache(args.project, n, lines)
            data["engine"]["backend"] = backend
            data["engine"]["remote_opt_in"] = backend == "vlm"
            for p in data["pages"]:
                if p["n"] == n:
                    p["status"] = "ocr-local" if backend == "tesseract" else "ocr-remote"
            result.append({"page": n, "status": "ocr", "lines": len(lines)})
    P.save_project(args.project, data)
    P.combine(args.project)
    print(json.dumps({"pages": result, "backend": backend}, ensure_ascii=False))
    return 0


def cmd_export(args) -> int:
    tei = P.tei_export(args.project)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        P.tei_check(args.project, out)
        print(json.dumps({"check": "OK", "file": str(out), "bytes": len(tei.encode())}))
        return 0
    out.write_text(tei, encoding="utf-8")
    print(json.dumps({"written": str(out), "bytes": len(tei.encode()),
                      "wellformed": P.xml_wellformed(tei),
                      "devanagari": P.dev_count(tei)}))
    return 0


def cmd_smoke(args) -> int:
    """End-to-end on a REAL printed Sanskrit page, local-only, with a receipt."""
    sample = Path(args.sample) if args.sample else default_sample()
    if not sample.is_file():
        raise P.PatternError(f"smoke sample not found: {sample}")
    # Work dir is repo-local by default: some hosts fence /tmp from tesseract's
    # file reads, so a system-temp page image can be "not found" though present.
    work = Path(args.work) if args.work else Path(
        tempfile.mkdtemp(prefix="h8429-smoke-", dir=str(repo_root())))
    keep = bool(args.keep or args.work)
    try:
        inbox = work / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(sample, inbox / "page_0001.jpg")
        project = work / "project"
        data = P.new_project("images", str(sample), dpi=300, lang="san", psm=6)
        data["bibliography"] = {
            "title": "Monier-Williams, Sanskrit-English Dictionary, printed p. 277 (smoke)",
            "author": "M. Monier-Williams",
            "source": "Real printed page — EntryAnatomy/assets/mw_kala_p277.jpg (estate asset)",
        }
        P.save_project(project, data)
        with offline_guard():
            sel = P.import_images(inbox, project)
            data["pages"] = [{"n": n, "mask": [], "status": "imported"} for n in sel]
            P.save_project(project, data)
            raw = engines.ocr_tesseract(P.page_path(project, 1), lang="san", psm=6)
            lines = P.lines_from_tsv(raw)
            P.write_page_cache(project, 1, lines)
            P.combine(project)
            tei = P.tei_export(project)
        tei_path = work / "scan.tei.xml"
        tei_path.write_text(tei, encoding="utf-8")
        # --- canaries / acceptance -----------------------------------------
        assert P.xml_wellformed(tei), "TEI is not well-formed XML"
        assert '<pb n="1"/>' in tei, "missing page break"
        assert tei.count("<lb ") >= 20, f"too few line anchors: {tei.count('<lb ')}"
        dev = P.dev_count(tei)
        assert dev >= 100, f"Devanagari canary too low: {dev}"
        assert unicodedata.normalize("NFC", tei) == tei, "output is not NFC"
        P.tei_check(project, tei_path)
        assert P.tei_export(project) == tei, "export is not deterministic"
        assert P.orig_path(project, 1).is_file(), "first-pass cache missing"
        receipt = {
            "handoff": "H8429", "date": "18-11-2026",
            "sample": str(sample.relative_to(repo_root())),
            "sample_sha256": hashlib.sha256(sample.read_bytes()).hexdigest(),
            "backend": "tesseract (local)", "lang": "san", "psm": 6,
            "pages": 1, "line_anchors": tei.count("<lb "),
            "devanagari_chars": dev, "nfc": True, "wellformed": True,
            "byte_parity": True, "network_calls": 0,
            "verdict": "PASS",
        }
        rp = Path(args.receipt) if args.receipt else work / "smoke_receipt.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    finally:
        if not keep:
            shutil.rmtree(work, ignore_errors=True)


def cmd_selftest(_args) -> int:
    """Offline positive + negative controls; stdlib+tesseract-free."""
    checks: list[tuple[str, bool, str]] = []

    def ck(name: str, cond: bool, detail: str = "") -> None:
        checks.append((name, bool(cond), detail))

    with tempfile.TemporaryDirectory(prefix="h8429-selftest-") as td:
        root = Path(td)
        # 1. page selection — positive + negative
        ck("selection_positive", P.parse_selection("1-3,5", 5) == [1, 2, 3, 5])
        try:
            P.parse_selection("1-9", 3)
            ck("selection_negative", False, "out-of-range page accepted")
        except P.PatternError:
            ck("selection_negative", True)

        # 2. offline guard refuses a connection attempt
        try:
            with offline_guard():
                socket.create_connection(("127.0.0.1", 9), timeout=0.2)
            ck("offline_guard", False, "socket was allowed")
        except (NetworkAccessError, RuntimeError):
            ck("offline_guard", True)

        # 3. TSV line grouping — positive + negative (empty -> no lines)
        tsv = ("level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
               "5\t1\t1\t1\t1\t1\t10\t5\t20\t10\t92\tकाल\n"
               "5\t1\t1\t1\t1\t2\t35\t5\t20\t10\t91\tअर्थ\n"
               "5\t1\t1\t1\t2\t1\t10\t25\t20\t10\t90\tधर्म\n")
        lines = P.lines_from_tsv(tsv)
        ck("tsv_group", lines == [(1, "काल अर्थ"), (2, "धर्म")], repr(lines))
        ck("tsv_empty", P.lines_from_tsv(tsv.split("\n")[0] + "\n") == [])

        # 4. NFC on the page cache round-trip
        proj = root / "proj"
        P.save_project(proj, P.new_project("images", "synthetic"))
        P.write_page_cache(proj, 1, [(1, "क" + "\u093e")])  # decomposed AA
        got = P.read_page_cache(P.cache_path(proj, 1))
        ck("nfc_cache", got == [(1, "का")], repr(got))

        # 5. mask geometry — positive + negative
        from PIL import Image
        img = root / "in.png"
        Image.new("RGB", (40, 20), "black").save(img)
        masked = P.apply_mask(img, [[0, 0, 10, 10]], root / "masked.png")
        ck("mask_positive", Image.open(masked).getpixel((2, 2)) == (255, 255, 255))
        try:
            P.apply_mask(img, [[0, 0, 0, 5]], root / "bad.png")
            ck("mask_negative", False, "zero-size mask accepted")
        except P.PatternError:
            ck("mask_negative", True)

        # 6. ALTO parsing — positive + negative
        alto = ('<alto><Layout><Page><PrintSpace><TextBlock>'
                '<TextLine HPOS="1" VPOS="2" WIDTH="9" HEIGHT="4">'
                '<String CONTENT=" क "/><String CONTENT="अर्थ"/></TextLine>'
                '<TextLine HPOS="1" VPOS="20"><String CONTENT="   "/></TextLine>'
                '</TextBlock></PrintSpace></Page></Layout></alto>')
        al = P.parse_alto_lines(alto)
        ck("alto_positive", len(al) == 1 and al[0]["text"] == "क अर्थ", repr(al))
        ck("alto_negative", P.parse_alto_lines("<alto/>") == [])

        # 7. TEI export + byte-parity + tamper negative
        data = P.load_project(proj)
        data["pages"] = [{"n": 1, "mask": []}, {"n": 2, "mask": []}]
        data["page_divs"] = {"1": [("book:I", "1")], "2": [("book:I", "1")]}
        data["bibliography"] = {"title": "Synthetic", "author": "T", "source": "fixture"}
        P.save_project(proj, data)
        P.write_page_cache(proj, 1, [(1, "काल"), (2, "अर्थ-"), (3, "धर्म")])
        P.write_page_cache(proj, 2, [(1, "धर्म")])
        tei = P.tei_export(proj)
        outp = root / "scan.tei.xml"
        outp.write_text(tei, encoding="utf-8")
        ck("tei_wellformed", P.xml_wellformed(tei))
        ck("tei_anchor", '<pb n="1"/>' in tei and '<pb n="2"/>' in tei)
        ck("tei_citestructure", "<citeStructure" in tei and 'unit="pb"' in tei)
        ck("tei_break_no", 'break="no"' in tei)
        ck("tei_div", '<div type="book" n="I"' in tei or 'type="book"' in tei)
        ck("tei_parity", P.tei_check(proj, outp))
        outp.write_text(tei + "\n", encoding="utf-8")
        try:
            P.tei_check(proj, outp)
            ck("tei_tamper", False, "drift not detected")
        except P.PatternError:
            ck("tei_tamper", True)

        # 8. remote opt-in refuses by default
        try:
            engines.ocr_vlm(root / "x.png")
            ck("remote_refusal", False, "remote OCR ran without consent")
        except engines.NetworkOptInRequired:
            ck("remote_refusal", True)

    failed = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}{(' :: ' + detail) if detail and not ok else ''}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} controls PASS")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    imp = sub.add_parser("import", help="PDF/images/ALTO -> local page PNGs + project.json")
    imp.add_argument("--source", required=True)
    imp.add_argument("--kind", choices=("pdf", "images", "alto"), required=True)
    imp.add_argument("--project", required=True)
    imp.add_argument("--pages", help="1-based selection, e.g. 1-3,5")
    imp.add_argument("--dpi", type=int, default=300)
    imp.add_argument("--lang", default="san")
    imp.add_argument("--script", default="devanagari")
    imp.add_argument("--psm", type=int, default=6)
    imp.add_argument("--backend", default="tesseract", choices=("tesseract", "vlm"))
    imp.add_argument("--alto-image", help="page image for ALTO import")
    imp.add_argument("--title"); imp.add_argument("--author"); imp.add_argument("--source-citation")
    imp.add_argument("--force", action="store_true")
    imp.set_defaults(func=cmd_import)

    ocr = sub.add_parser("ocr", help="local OCR (default) with resumable page cache")
    ocr.add_argument("--project", required=True)
    ocr.add_argument("--pages"); ocr.add_argument("--backend", choices=("tesseract", "vlm"))
    ocr.add_argument("--lang"); ocr.add_argument("--psm", type=int)
    ocr.add_argument("--force", action="store_true")
    ocr.add_argument("--remote", action="store_true", help="EXPLICIT opt-in for VLM")
    ocr.add_argument("--accept-network", help="must equal DATA_LEAVES_THIS_MACHINE")
    ocr.set_defaults(func=cmd_ocr)

    exp = sub.add_parser("export", help="deterministic TEI P5 with pb/lb/citeStructure")
    exp.add_argument("--project", required=True); exp.add_argument("--out", required=True)
    exp.add_argument("--check", action="store_true")
    exp.set_defaults(func=cmd_export)

    sm = sub.add_parser("smoke", help="end-to-end on a real printed Sanskrit page (local-only)")
    sm.add_argument("--sample"); sm.add_argument("--work"); sm.add_argument("--receipt")
    sm.add_argument("--keep", action="store_true")
    sm.set_defaults(func=cmd_smoke)

    st = sub.add_parser("selftest", help="offline positive/negative controls")
    st.set_defaults(func=cmd_selftest)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (P.PatternError, engines.EngineError, engines.NetworkOptInRequired,
            NetworkAccessError, AssertionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
