#!/usr/bin/env python
r"""Content-addressed translation memory (TM) for the PWG masked-harness pipeline.

Reuse, don't reinvent. An identical source span — a sense's German gloss, or a
selfheal fragment's source text — maps to exactly one translation. So the same
meaning that recurs (a root's sense reappearing in a derived noun, a citation
block shared across entries, a fragment that already succeeded on a prior run)
is REUSED instead of being paid for again at the LLM.

Key = sha256(lang | prompt_sha | source). Including `prompt_sha` (the hash of the
active translation prompt / rubric) means a prompt change INVALIDATES stale
entries automatically — the TM only ever returns a translation the *current*
prompt would have produced, which is exactly the "reuse only if nothing changed"
guarantee. Language-scoped, so EN and RU never cross-contaminate.

Storage: append-friendly JSONL at src/pilot/tm/tm.<lang>.jsonl; `load()` dedups by
key (last wins). Values are arbitrary JSON — a plain string for a sense
(german -> english/russian) or a list of restored sense dicts for a fragment.
Zero LLM, pure Python.

Distinct from `mw_en_tm.py`: that feed is EXTERNAL candidate vocabulary (Monier-Williams
English glosses, keyed by SLP1 headword) injected as hints for the LLM to adjudicate.
This is a reuse cache of the pipeline's OWN produced translations, keyed by source-text
hash, so an identical source is served from cache instead of re-translated.

  from translation_memory import TM
  tm = TM('en', prompt_sha)          # loads src/pilot/tm/tm.en.jsonl
  hit = tm.get(source_text)          # -> stored translation or None
  tm.put(source_text, translation)   # returns True if new/changed
  tm.save()
"""
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))          # .../src/pilot
TM_DIR = os.path.join(HERE, 'tm')


def key(lang, prompt_sha, src):
    """Stable content address for (lang, prompt, source)."""
    h = hashlib.sha256()
    h.update((lang or '').encode('utf-8'));        h.update(b'\x00')
    h.update((prompt_sha or '').encode('utf-8'));  h.update(b'\x00')
    h.update((src or '').encode('utf-8'))
    return h.hexdigest()


def default_path(lang):
    return os.path.join(TM_DIR, 'tm.%s.jsonl' % lang)


class TM:
    def __init__(self, lang, prompt_sha, path=None):
        self.lang = lang
        self.prompt_sha = prompt_sha or ''
        self.path = path or default_path(lang)
        self._d = {}          # key -> record
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get('k'):
                    self._d[r['k']] = r

    def get(self, src):
        """Return the stored translation for `src` under the current lang+prompt, or None.
        Cross-prompt entries never match (the key includes prompt_sha)."""
        r = self._d.get(key(self.lang, self.prompt_sha, src))
        return r['out'] if r else None

    def put(self, src, out):
        """Store src -> out. Returns True if this added or changed an entry."""
        k = key(self.lang, self.prompt_sha, src)
        cur = self._d.get(k)
        if cur is not None and cur.get('out') == out:
            cur['n'] = cur.get('n', 1) + 1        # seen again, same translation
            return False
        self._d[k] = {'k': k, 'src': src, 'out': out,
                      'lang': self.lang, 'prompt_sha': self.prompt_sha,
                      'n': (cur.get('n', 0) + 1) if cur else 1}
        return True

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            for r in self._d.values():
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
        os.replace(tmp, self.path)

    def stats(self):
        return {'entries': len(self._d), 'lang': self.lang, 'path': self.path,
                'reused_total': sum(r.get('n', 1) - 1 for r in self._d.values())}

    def __len__(self):
        return len(self._d)


if __name__ == '__main__':
    # quick self-check (no files touched): put/get round-trip + prompt-sha isolation
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'tm.en.jsonl')
        a = TM('en', 'PROMPTv1', p)
        assert a.get('Wasser') is None
        assert a.put('Wasser', 'water') is True
        assert a.put('Wasser', 'water') is False          # idempotent
        assert a.get('Wasser') == 'water'
        a.save()
        b = TM('en', 'PROMPTv1', p)                        # reload
        assert b.get('Wasser') == 'water'
        c = TM('en', 'PROMPTv2', p)                        # prompt changed -> miss
        assert c.get('Wasser') is None
        e = TM('ru', 'PROMPTv1', p)                        # lang changed -> miss
        assert e.get('Wasser') is None
        # fragment value can be a list of sense dicts
        a.put('frag-src', [{'german': 'g', 'english': 'e'}])
        assert a.get('frag-src') == [{'german': 'g', 'english': 'e'}]
    print('translation_memory self-check OK')
