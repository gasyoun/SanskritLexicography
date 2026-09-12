#!/usr/bin/env python
"""cdsl_index.py -- key->byte-offset SQLite index sidecar for csl-orig sources (H4408).

Every per-headword tool in this estate used to re-parse the 66-69MB csl-orig
dictionaries from scratch (AUDIT: Uprava reports/BATCH_CHUNK_GAP_AUDIT_08-09-2026.md);
the worst case re-read the whole 69MB pwg.txt once PER record. This module gives
them ONE committed alternative:

  * builder : `python cdsl_index.py build pwg` (or `--all`) -- ONE streaming
              binary pass over the dict, writing `<dict>.idx` (SQLite) under
              data/cdsl_index/ (derived artifacts; gitignored, rebuilt on demand).
  * reader  : `CdslIndex` -- by-L-id and by-key1 record lookup + a lazy
              whole-dict record iterator, all served from the sidecar without
              materializing the source.

Sidecar row = (l_id, key1, byte_offset, byte_len) where the byte span covers the
`<L>` header line through the last body line (the `<LEND>` line is excluded), so
`record_text()` reproduces a direct whole-file parse byte-for-byte (spot-check
below proves it on the real pwg/mw sources).

Staleness: the index stores the source's size+mtime_ns; `open_index()` rebuilds
automatically when either moved. csl-orig itself is NEVER written by this tool.

    python cdsl_index.py build pwg [--force]
    python cdsl_index.py build --all
    python cdsl_index.py spot-check pwg 20      # sidecar vs direct parse parity
    python cdsl_index.py selftest               # hermetic fixture test
"""
import os
import re
import sqlite3
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSL_ORIG = os.environ.get(
    'CSL_ORIG_V02',
    os.path.join(HERE, '..', '..', 'csl-orig', 'v02'))
IDX_DIR = os.path.join(HERE, '..', 'data', 'cdsl_index')

LID_RE = re.compile(rb'^<L>(\S+?)<pc>', re.M)
KEY1_RE = re.compile(rb'<k1>([^<]*)')

LINE = 1 << 16


def source_path(name):
    """'pwg' -> .../csl-orig/v02/pwg/pwg.txt"""
    d = os.path.join(DEFAULT_CSL_ORIG, name)
    return os.path.join(d, name + '.txt')


def index_path(name):
    return os.path.join(os.path.normpath(IDX_DIR), name + '.idx')


def build(source, idx=None, force=False):
    """ONE streaming pass over `source`; returns number of records indexed.

    Skips when the sidecar is fresh (same source size+mtime) unless --force.
    Duplicate L-ids: last occurrence wins, matching a direct-parse dict build.
    """
    if not os.path.exists(source):
        raise SystemExit('cdsl_index: source not found: %s' % source)
    idx = idx or index_path(os.path.splitext(os.path.basename(source))[0])
    st = os.stat(source)
    if not force and os.path.exists(idx):
        try:
            con = sqlite3.connect(idx)
            row = con.execute("select v from meta where k='source_stat'").fetchone()
            con.close()
            if row and row[0] == '%d:%d' % (st.st_size, st.st_mtime_ns):
                return -1                                   # fresh, skipped
        except sqlite3.Error:
            pass                                            # corrupt -> rebuild
    os.makedirs(os.path.dirname(idx), exist_ok=True)
    tmp = idx + '.building'
    con = sqlite3.connect(tmp)
    con.execute('pragma journal_mode=off')
    con.execute('create table meta(k text primary key, v text)')
    con.execute('create table records('
                'l_id text primary key, key1 text, '
                'byte_offset integer, byte_len integer)')
    con.execute('create index records_key1 on records(key1)')
    bom = b''
    n = 0
    rec_start = None
    with open(source, 'rb') as f:
        first = f.read(3)
        if first == b'\xef\xbb\xbf':
            bom = first                                     # BOM precedes rec 0
        else:
            f.seek(0)
        pos = f.tell()
        for raw in f:
            line = raw.rstrip(b'\r\n')
            if line.startswith(b'<L>'):
                rec_start = pos
            elif line.startswith(b'<LEND>') and rec_start is not None:
                # startswith, not ==: pwg_mask.records() and the direct-parse
                # regex both close a record at ANY <LEND> line, incl. the
                # 3,238 Cologne continuation lines shaped `<LEND>12345` — an
                # exact-match test silently drops those records.
                end = pos                                   # <LEND> line excluded
                f.seek(rec_start)
                head = f.read(min(LINE, end - rec_start))
                f.seek(pos + len(raw))
                m = LID_RE.match(head)
                if m:
                    lid = m.group(1).decode('utf-8', 'replace')
                    k1 = KEY1_RE.search(head)
                    con.execute('insert or replace into records values(?,?,?,?)',
                                (lid, k1.group(1).decode('utf-8', 'replace')
                                 if k1 else '', rec_start, end - rec_start))
                    n += 1
                rec_start = None
            pos += len(raw)
    con.execute("insert into meta values('source_stat',?)",
                ('%d:%d' % (st.st_size, st.st_mtime_ns),))
    con.execute("insert into meta values('source',?)", (os.path.abspath(source),))
    con.execute("insert into meta values('bom',?)", (bom.decode('latin1'),))
    con.commit()
    con.close()
    os.replace(tmp, idx)
    return n


class CdslIndex:
    """Reader over one <dict>.idx sidecar."""

    def __init__(self, idx):
        self.idx = idx
        self.con = sqlite3.connect(idx)
        self.con.text_factory = str
        self._fh = None
        self._source = self.con.execute(
            "select v from meta where k='source'").fetchone()[0]

    def _source_fh(self):
        if self._fh is None:
            self._fh = open(self._source, 'rb')
        return self._fh

    @classmethod
    def open(cls, source, force=False):
        """Open (building first if missing/stale) the index for a csl-orig source."""
        name = os.path.splitext(os.path.basename(source))[0]
        idx = index_path(name)
        build(source, idx, force=force)
        return cls(idx)

    def close(self):
        if self._fh is not None:
            self._fh.close()
            self._fh = None
        self.con.close()

    def ids(self):
        return [r[0] for r in self.con.execute('select l_id from records')]

    def ids_for_key(self, key1):
        return [r[0] for r in self.con.execute(
            'select l_id from records where key1=? order by byte_offset', (key1,))]

    def record_text(self, l_id):
        """Raw record bytes decoded: header line + '\\n' + body, no trailing newline."""
        row = self.con.execute(
            'select byte_offset, byte_len from records where l_id=?', (l_id,)).fetchone()
        if not row:
            return None
        f = self._source_fh()
        f.seek(row[0])
        data = f.read(row[1])
        if data.endswith(b'\n'):
            data = data[:-1]
        return data.decode('utf-8', 'replace')

    def record(self, l_id):
        """(pc_header, body) -- same shape as EntryAnatomy load_records values."""
        text = self.record_text(l_id)
        if text is None:
            return None
        parts = text.split('\n', 1)
        header = parts[0]
        body = parts[1] if len(parts) > 1 else ''
        pc = header.split('<pc>', 1)[1] if '<pc>' in header else ''
        return pc, body

    def chunks(self):
        """Lazy iteration yielding the text AFTER '<L>' for each record (i.e. the
        split('<L>') chunks of a whole-file read, minus the <LEND> line) --
        drop-in fuel for consumers that regex per-chunk."""
        for l_id, off, ln in self.con.execute(
                'select l_id, byte_offset, byte_len from records order by byte_offset'):
            text = self.record_text(l_id)
            if text is None:
                continue
            yield text[len('<L>'):] if text.startswith('<L>') else text


def direct_records(path):
    """The pre-H440 whole-file parse (parity baseline), memory-heavy by design."""
    with open(path, encoding='utf-8') as f:
        txt = f.read()
    out = {}
    for m in re.finditer(r"<L>(\S+?)<pc>(\S+?)\n(.*?)\n?<LEND>", txt, re.S):
        out[m.group(1)] = (m.group(2), m.group(3))
    return out


def spot_check(name, n=20, seed=4408):
    """Compare n sidecar records against the direct whole-file parse."""
    import random
    src = source_path(name)
    idx = CdslIndex.open(src)
    direct = direct_records(src)
    ids = idx.ids()
    rng = random.Random(seed)
    sample = rng.sample(ids, min(n, len(ids)))
    bad = []
    for lid in sample:
        got = idx.record(lid)
        want = direct.get(lid)
        if got != want:
            bad.append(lid)
    print('spot-check %s: %d/%d identical (direct-parse baseline %d records)'
          % (name, len(sample) - len(bad), len(sample), len(direct)))
    idx.close()
    return not bad


def _write_fixture(tmp):
    src = os.path.join(tmp, 'fix.txt')
    with open(src, 'w', encoding='utf-8', newline='\n') as f:
        f.write('<L>1<pc>10,1<k1>agni<k2>agni\nbody one <lex>m.</lex>\n<LEND>\n')
        f.write('<L>2<pc>10,2<k1>akEk<k2>akEk\nbody two\nmore\n<LEND>\n')
        f.write('<L>3<pc>10,3<k1>agni<k2>agni<h>2\n\n<LEND>\n')   # empty body
        f.write('<L>4<pc>10,4<k1>go<k2>go\nbody four\n<LEND>5\n')  # continuation <LEND>5
        f.write('<L>5<pc>10,5<k1>go<k2>go<h>2\nbody five\n<LEND>\n')
        f.write('trailer line outside any record\n')
    return src


def _selftest():
    import shutil
    old_orig, old_idx = DEFAULT_CSL_ORIG, IDX_DIR
    tmp = None
    failures = []
    try:
        tmp = tempfile.mkdtemp(prefix='cdsl_index_selftest_')
        src = _write_fixture(tmp)
        globals()['DEFAULT_CSL_ORIG'] = tmp
        globals()['IDX_DIR'] = os.path.join(tmp, 'idx')
        # source_path('fix') must resolve to the fixture
        os.makedirs(os.path.join(tmp, 'fix'))
        shutil.copy(src, os.path.join(tmp, 'fix', 'fix.txt'))

        idx = CdslIndex.open(source_path('fix'))
        texts = {i: idx.record_text(i) for i in idx.ids()}
        if texts['1'] != '<L>1<pc>10,1<k1>agni<k2>agni\nbody one <lex>m.</lex>':
            failures.append('rec1 text mismatch: %r' % texts['1'])
        if texts['3'] != '<L>3<pc>10,3<k1>agni<k2>agni<h>2\n':
            failures.append('rec3 (empty body) mismatch: %r' % texts['3'])
        if texts['4'] != '<L>4<pc>10,4<k1>go<k2>go\nbody four':
            failures.append('rec4 (<LEND>5 continuation) mismatch: %r' % texts['4'])
        if idx.record('1') != ('10,1<k1>agni<k2>agni', 'body one <lex>m.</lex>'):
            failures.append('record() shape mismatch: %r' % (idx.record('1'),))
        if sorted(idx.ids_for_key('agni')) != ['1', '3']:
            failures.append('ids_for_key: %r' % idx.ids_for_key('agni'))
        chunks = list(idx.chunks())
        if chunks[0] != "1<pc>10,1<k1>agni<k2>agni\nbody one <lex>m.</lex>":
            failures.append('chunk shape: %r' % chunks[0])
        idx.close()

        # BOM: same fixture with a BOM must index identically
        src2 = os.path.join(tmp, 'fixbom.txt')
        with open(src2, 'wb') as f:
            f.write(b'\xef\xbb\xbf')
            f.write(open(src, 'rb').read())
        os.makedirs(os.path.join(tmp, 'fixbom'), exist_ok=True)
        shutil.copy(src2, os.path.join(tmp, 'fixbom', 'fixbom.txt'))
        idx2 = CdslIndex.open(source_path('fixbom'))
        if sorted(idx2.ids()) != ['1', '2', '3', '4', '5']:
            failures.append('BOM ids: %r' % idx2.ids())
        idx2.close()

        # staleness: touching the source forces a rebuild
        os.utime(source_path('fix'), None)
        con = sqlite3.connect(index_path('fix'))
        before = con.execute('select count(*) from records').fetchone()[0]
        con.close()
        n = build(source_path('fix'))
        if n != 5:
            failures.append('rebuild count: %r' % n)

        # direct-parse parity on the fixture
        direct = direct_records(source_path('fix'))
        if set(direct) != {'1', '2', '3', '4', '5'}:
            failures.append('direct fixture ids: %r' % sorted(direct))
        if direct['2'] != ('10,2<k1>akEk<k2>akEk', 'body two\nmore'):
            failures.append('direct rec2: %r' % (direct['2'],))
        if direct['4'] != ('10,4<k1>go<k2>go', 'body four'):
            failures.append('direct rec4 continuation: %r' % (direct['4'],))
        idx = CdslIndex.open(source_path('fix'))       # reopen (closed above)
        side = {i: idx.record(i) for i in ('1', '2', '3', '4', '5')}
        # reopen idx for the parity assertion (idx2 left it rebuilt-fresh)
        if any(side[i] != direct[i] for i in direct):
            failures.append('fixture sidecar/direct parity: %r' % [(i, side[i], direct[i]) for i in direct if side[i]!=direct[i]][:2])
    finally:
        globals()['DEFAULT_CSL_ORIG'], globals()['IDX_DIR'] = old_orig, old_idx
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        for f in failures:
            print('FAIL:', f, file=sys.stderr)
        sys.exit(1)
    print('cdsl_index selftest: OK (6/6)')


def main():
    import argparse
    ap = argparse.ArgumentParser(description=(__doc__ or '').split('\n')[1])
    sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build')
    b.add_argument('name', help="dict name ('pwg') or '--all' for every v02 dir")
    b.add_argument('--force', action='store_true')
    sc = sub.add_parser('spot-check')
    sc.add_argument('name')
    sc.add_argument('n', type=int, nargs='?', default=20)
    sub.add_parser('selftest')
    args = ap.parse_args()

    if args.cmd == 'selftest':
        _selftest()
        return
    if args.cmd == 'spot-check':
        sys.exit(0 if spot_check(args.name, args.n) else 1)
    if args.cmd == 'build':
        names = (sorted(os.listdir(DEFAULT_CSL_ORIG))
                 if args.name == '--all' else [args.name])
        for nm in names:
            src = source_path(nm)
            if not os.path.exists(src):
                print('  skip %s: no source' % nm)
                continue
            r = build(src, force=args.force)
            print('  %s: %s' % (nm, 'fresh (skipped)' if r < 0 else '%d records' % r))


if __name__ == '__main__':
    main()
