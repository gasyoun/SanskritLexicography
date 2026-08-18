# -*- coding: utf-8 -*-
"""Write a review sheet as a PACKSET — parent index plus pack pages (H3098).

One helper, called by every generator that wants packs, so the stamp/lock/write
order lives in exactly one place. Getting that order wrong is how an audit trail
quietly stops meaning anything: the parent must be hashed and NOT stamped (it is
an index with no export), every pack must be stamped BEFORE it is hashed into
the lock, and the lock must be written from the same documents that were saved
to disk — not from a re-render.

Layout, matching the vote hub's own convention
(``vote/sheets/<name>.html`` beside ``vote/sheets/<name>/pack-NN.html``)::

    <out_dir>/<stem>.html            parent index
    <out_dir>/<stem>/pack-01.html    first pack
    <out_dir>/<stem>/pack-02.html    …

A sheet at or under ``pack_size`` is NOT a packset: it writes the single file it
always did, and takes the ordinary single-sheet lock. Splitting a sheet that
fits costs a click and buys nothing.
"""
import io
import os

from csl_pyutil import render_review_sheet_packset

from review_binding import stamp, write_lock, write_packset_lock

__all__ = ["emit_sheet"]


def emit_sheet(items, config, out_path, *, screening, manifest=None,
               generated=None, locks_dir=None, gate=None, pack_size=0,
               hub_name=None, force=False):
    """Render, stamp, write and lock a sheet — as a packset when it earns one.

    ``pack_size`` 0 (the default) keeps the historical single-file behaviour
    exactly, so a generator opting in changes nothing for anyone who does not
    pass the flag.

    Returns ``(paths, lock_path, n_packs)`` where ``paths`` is every HTML file
    written, parent first.
    """
    generated = generated or config["generated"]
    sheet_id = config["sheet_id"]

    if not pack_size or len(items) <= pack_size:
        from csl_pyutil import render_review_sheet
        doc = render_review_sheet(items, config, extras=True,
                                  screening=screening, manifest=manifest)
        doc, chash = stamp(doc)
        _write(out_path, doc)
        lock = write_lock(sheet_id, chash, [it["id"] for it in items], generated,
                          locks_dir=locks_dir, gate=gate, source_html=out_path,
                          force=force)
        return [out_path], lock, 0

    cfg = dict(config)
    cfg["pack_size"] = pack_size
    stem = hub_name or os.path.splitext(os.path.basename(out_path))[0]
    out = render_review_sheet_packset(items, cfg, extras=True, screening=screening,
                                      manifest=manifest, hub_name=stem)
    if out["parent"] is None:                       # defensive: pack_size ≥ len(items)
        return emit_sheet(items, config, out_path, screening=screening,
                          manifest=manifest, generated=generated,
                          locks_dir=locks_dir, gate=gate, pack_size=0, force=force)

    # Stamp every pack first: the lock hashes the documents that go to disk.
    stamped = [stamp(p)[0] for p in out["packs"]]

    out_dir = os.path.dirname(os.path.abspath(out_path))
    pack_dir = os.path.join(out_dir, stem)
    os.makedirs(pack_dir, exist_ok=True)

    paths = [out_path]
    _write(out_path, out["parent"])
    for n, doc in enumerate(stamped, 1):
        p = os.path.join(pack_dir, "pack-%02d.html" % n)
        _write(p, doc)
        paths.append(p)

    lock = write_packset_lock(sheet_id, out["parent"], stamped, generated,
                              locks_dir=locks_dir, gate=gate,
                              source_html=out_path, force=force)
    return paths, lock, len(stamped)


def _write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
