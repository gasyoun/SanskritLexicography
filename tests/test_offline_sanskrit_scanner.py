"""H8429 — offline Sanskrit scanner pattern pins (local-only, no network)."""
from __future__ import annotations

import argparse
import hashlib
import json
import socket
from pathlib import Path

import pytest

from conftest import REPO, load_module

sc = load_module("tools/offline_sanskrit_scanner/scanner.py")
P = sc.P
E = sc.engines


TSV = ("level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n"
       "5\t1\t1\t1\t1\t1\t10\t5\t20\t10\t92\tकाल\n"
       "5\t1\t1\t1\t1\t2\t35\t5\t20\t10\t91\tअर्थ\n"
       "5\t1\t1\t1\t2\t1\t10\t25\t20\t10\t90\tधर्म\n")


def test_page_selection_positive_and_negative():
    assert P.parse_selection("1-3,5", 5) == [1, 2, 3, 5]
    assert P.parse_selection(None, 3) == [1, 2, 3]
    with pytest.raises(P.PatternError):
        P.parse_selection("1-9", 3)


def test_tesseract_tsv_to_anchored_lines():
    assert P.lines_from_tsv(TSV) == [(1, "काल अर्थ"), (2, "धर्म")]
    assert P.lines_from_tsv(TSV.split("\n")[0] + "\n") == []


def test_alto_geometry_parse():
    xml = ('<alto><Layout><Page><PrintSpace><TextBlock>'
           '<TextLine HPOS="1" VPOS="2" WIDTH="9" HEIGHT="4">'
           '<String CONTENT=" क "/><String CONTENT="अर्थ"/></TextLine>'
           '</TextBlock></PrintSpace></Page></Layout></alto>')
    lines = P.parse_alto_lines(xml)
    assert lines == [{"left": 1, "top": 2, "width": 9, "height": 4,
                      "text": "क अर्थ"}]
    assert P.parse_alto_lines("<alto/>") == []


def test_offline_guard_blocks_sockets():
    with pytest.raises(sc.NetworkAccessError):
        with sc.offline_guard():
            socket.create_connection(("127.0.0.1", 9), timeout=0.1)


def test_tei_export_parity_nfc_and_hierarchy(tmp_path):
    proj = tmp_path / "proj"
    data = P.new_project("images", "synthetic")
    data["pages"] = [{"n": 1, "mask": []}, {"n": 2, "mask": []}]
    data["page_divs"] = {"1": [("book:I", "1")], "2": [("book:I", "1")]}
    data["bibliography"] = {"title": "Fixture", "author": "T", "source": "test"}
    P.save_project(proj, data)
    P.write_page_cache(proj, 1, [(1, "क" + "\u093e"), (2, "अर्थ-"), (3, "धर्म")])
    P.write_page_cache(proj, 2, [(1, "काल")])
    tei = P.tei_export(proj)
    assert P.xml_wellformed(tei)
    assert 'unit="pb"' in tei and '<pb n="1"/>' in tei and '<pb n="2"/>' in tei
    assert 'break="no"' in tei
    assert '<div type="book"' in tei
    assert P.dev_count(tei) > 0
    assert __import__("unicodedata").normalize("NFC", tei) == tei
    out = tmp_path / "scan.tei.xml"
    out.write_text(tei, encoding="utf-8")
    assert P.tei_check(proj, out)
    out.write_text(tei + "\n", encoding="utf-8")
    with pytest.raises(P.PatternError):
        P.tei_check(proj, out)


def test_remote_backend_refuses_without_explicit_consent(tmp_path):
    with pytest.raises(E.NetworkOptInRequired):
        E.ocr_vlm(tmp_path / "page.png")


def test_committed_smoke_receipt_canary():
    receipt = json.loads((REPO / "tools/offline_sanskrit_scanner/"
                          "SMOKE_RECEIPT_18-11-2026.json").read_text(encoding="utf-8"))
    sample = REPO / receipt["sample"]
    assert sample.is_file()
    assert hashlib.sha256(sample.read_bytes()).hexdigest() == receipt["sample_sha256"]
    assert receipt["verdict"] == "PASS" and receipt["network_calls"] == 0
    assert receipt["line_anchors"] >= 20 and receipt["devanagari_chars"] >= 100
    assert receipt["backend"] == "tesseract (local)"


@pytest.mark.skipif(not E.tesseract_available(), reason="local tesseract not installed")
def test_real_print_smoke_end_to_end(capsys):
    rc = sc.cmd_smoke(argparse.Namespace(sample=None, work=None, receipt=None, keep=False))
    assert rc == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["verdict"] == "PASS" and receipt["network_calls"] == 0
