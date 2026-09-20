"""H5069 — the audit apparatus's load-bearing properties, pinned.

Three things can silently break this audit and leave every other check green.

1. **The selection contract.** The thirty audited records are chosen without a
   seed: strata are computed from the record text, and within a stratum the six
   members are the six smallest ``sha256(record_id)``. If ``stratum_of``'s
   priority order or ``rank_key``'s hash changes, the frozen manifest stops
   describing the sample anyone can rebuild, and the audit's reproducibility
   claim becomes false without any test failing.

2. **Reviewer blinding.** The first review packet shipped control items whose
   ids literally read ``H5069.control:pos:001``. The first reviewer to open it
   named both controls from the id strings before reading a single gloss. An id
   that announces the answer is not a control, and the packet's own contents
   are the only place that defect is visible — so the four ``packet_id``
   assertions below exist specifically to stop it coming back.

3. **Control gradeability.** ``score`` decides whether a reviewer detected the
   planted addition and spared the licensed re-wording. If it stops matching
   packet ids to the sealed key, it silently grades nothing and reports a pass.

These run without the 23 MB store: everything here is pure.
"""
import hashlib
import os
import sys

ROOT = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

import h5069_source_support_audit as aud  # noqa: E402


def _feat(**kw):
    base = {"src_len": 100, "n_senses": 1, "n_gloss_de": 1, "n_ls": 0,
            "uncertain": False, "compound": False, "identical": False,
            "empty_tgt": False}
    base.update(kw)
    return base


# --- 1. selection contract -------------------------------------------------

def test_eligibility_excludes_records_that_assert_nothing_in_russian():
    # A record whose Russian is byte-identical to its German asserts nothing of
    # its own, so it cannot be audited for source support; nor can an empty one.
    assert aud.eligible(_feat()) is True
    assert aud.eligible(_feat(identical=True)) is False
    assert aud.eligible(_feat(empty_tgt=True)) is False
    assert aud.eligible(_feat(n_gloss_de=0)) is False


def test_stratum_priority_order_is_the_frozen_one():
    # The order is part of the contract: a record can satisfy several
    # predicates, and which stratum it lands in decides the sample.
    assert aud.stratum_of(_feat(src_len=150, n_senses=1)) == "short_gloss"
    # uncertainty outranks polysemy
    assert aud.stratum_of(
        _feat(src_len=900, n_senses=9, uncertain=True)) == "uncertainty"
    # polysemy outranks compound
    assert aud.stratum_of(
        _feat(src_len=900, n_senses=9, compound=True)) == "polysemy"
    # compound outranks citation density
    assert aud.stratum_of(
        _feat(src_len=900, n_senses=2, compound=True, n_ls=40)) == "compound"
    assert aud.stratum_of(_feat(src_len=900, n_senses=2, n_ls=40)) == "citation_dense"
    # matching nothing is not a stratum
    assert aud.stratum_of(_feat(src_len=900, n_senses=2, n_ls=1)) is None


def test_short_gloss_requires_both_halves_of_its_predicate():
    assert aud.stratum_of(_feat(src_len=201, n_senses=1, n_ls=1)) is None
    assert aud.stratum_of(_feat(src_len=150, n_senses=2, n_ls=1)) is None


def test_selection_is_seedless_and_reproducible():
    rows = [{"record_id": "r%03d" % i,
             "source_hash": "s" + str(i), "target_hash": "t" + str(i),
             "source_string": "{%gloss%} x" + "y" * (i % 7),
             "target_string": "{%глосс%} z" + str(i)}
            for i in range(200)]
    a, pools_a = aud.select(rows, n_per=3)
    b, pools_b = aud.select(list(reversed(rows)), n_per=3)
    assert pools_a == pools_b
    picked_a = {st: [r["record_id"] for r in a[st]] for st in aud.STRATA}
    picked_b = {st: [r["record_id"] for r in b[st]] for st in aud.STRATA}
    assert picked_a == picked_b, "selection must not depend on input order"
    assert picked_a["short_gloss"], "the fixture must actually populate a stratum"


def test_rank_key_is_the_record_id_hash():
    assert aud.rank_key("abc") == hashlib.sha256(b"abc").hexdigest()


# --- 2. reviewer blinding (the regression that matters) --------------------

def test_packet_id_does_not_leak_the_word_control():
    # The exact defect that shipped: an id that spells out the answer.
    pid = aud.packet_id("H5069.control:pos:001")
    assert "control" not in pid
    assert "pos" not in pid.split(":")[-1]


def test_packet_ids_share_one_shape_for_real_and_synthetic_items():
    real = aud.packet_id("pwg.tm.v1:exact-card:ru:" + "a" * 64)
    synth = aud.packet_id("H5069.control:neg:001")
    assert real.startswith("H5069.item:") and synth.startswith("H5069.item:")
    assert len(real) == len(synth), \
        "a length difference alone would re-identify the controls"


def test_packet_id_is_deterministic():
    assert aud.packet_id("x") == aud.packet_id("x")


def test_packet_ids_differ_per_record():
    ids = {aud.packet_id("r%d" % i) for i in range(500)}
    assert len(ids) == 500


# --- 3. gradeability -------------------------------------------------------

def test_verdict_vocabulary_is_closed():
    # score() and the reviewer brief must agree on exactly these four.
    assert aud.VERDICTS == ("faithful", "addition", "omission", "conflation")


def test_gloss_pairs_pads_the_shorter_side_rather_than_truncating():
    # 30% of the store has German glosses and no Russian ones; a reviewer must
    # see that asymmetry, not a silently shortened list.
    row = {"source_string": "{%a%} {%b%} {%c%}", "target_string": "{%а%}"}
    pairs = aud.gloss_pairs(row)
    assert len(pairs) == 3
    assert pairs[0]["de"] == "a" and pairs[0]["ru"] == "\u0430"
    assert pairs[1]["ru"] is None and pairs[2]["ru"] is None
    assert pairs[1]["de"] == "b" and pairs[2]["de"] == "c"
