#!/usr/bin/env python
import json
import os
import sqlite3
import sys
import tempfile
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import max_account_orchestrator as m


def main():
    with tempfile.TemporaryDirectory() as td:
        db = os.path.join(td, 'q.sqlite')
        m.main(['--db', db, 'init', '--account', 'acc1=' + os.path.join(td, 'a1'),
                '--account', 'acc2=' + os.path.join(td, 'a2')])
        for n in range(2):
            out = os.path.join(td, 'out%d.json' % n)
            argv = [sys.executable, '-c', 'import os; print(os.environ["CLAUDE_CONFIG_DIR"])']
            m.main(['--db', db, 'enqueue', '--external-id', 'j%d' % n,
                    '--argv-json', json.dumps(argv), '--cwd', td, '--output', out])
        m.main(['--db', db, 'run-once', '--timeout', '10'])
        con = sqlite3.connect(db)
        assert con.execute("select count(*) from jobs where state='done'").fetchone()[0] == 2
        con.execute("insert into jobs(external_id,argv_json,cwd,output_path,state) values('stale','[]',?,?,'in_progress')", (td, os.path.join(td, 'x')))
        con.commit(); con.close()
        m.main(['--db', db, 'recover'])
        con = sqlite3.connect(db)
        assert con.execute("select state from jobs where external_id='stale'").fetchone()[0] == 'pending'
        con.close()
        assert m.parse_reset('rate limit reset_at=1999999999', now=1) == 1999999999
        assert m.parse_reset('429 too many requests', now=100) == 18100
    print('max_account_orchestrator_selftest: PASS')


if __name__ == '__main__':
    main()
