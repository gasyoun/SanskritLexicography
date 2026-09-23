#!/usr/bin/env python3
"""NKRYa (Russian National Corpus, ruscorpora.ru) evidence client for PWG-RU (H5261).

Official API only: https://github.com/ruscorpora/public-api (Bearer token,
https://ruscorpora.ru/api/v1/). Scraping and the unofficial user clients
(kunansy/rnc, kmike/ruscorpora-tools) are ruled out (grill 22-09-2026).

Three queries, all cached on disk by request hash:

  sketch(lemma, pos)          word-portrait PORTRAIT_SKETCH: up to 10 collocates per
                              syntactic relation, ranked by dice (the API returns no more)
  freq(lemma, pos)            word-portrait PORTRAIT_FREQUENCY: ipm + 1..6 category
  concordance(query, n=3)     lex-gramm concordance: total hits (queryStats) + n lines

Default corpus is MAIN. The 19th-century archaism check is a concordance run with a
`created` 1800-1899 subcorpus (a word portrait takes no subcorpus). That subcorpus
condition is UNVERIFIED until the first live `probe` confirms the API accepts it.

Token (never in git or a repo .env), first hit wins:
  1. env RUSCORPORA_API_TOKEN
  2. macOS keychain generic password, service `ruscorpora-api`
  3. python `keyring` service `ruscorpora-api` (Windows Credential Manager on MSI)
No token -> NkryaAuthError with the exact command to store one (fail closed).

CLI:
  python src/nkrya_client.py probe
  python src/nkrya_client.py sketch туча S
  python src/nkrya_client.py freq сплочённый A
  python src/nkrya_client.py pair сплочённый туча [--19c]
  python src/nkrya_client.py --selftest
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

API = "https://ruscorpora.ru/api/v1"
KEYCHAIN_SERVICE = "ruscorpora-api"
TOKEN_ENV = "RUSCORPORA_API_TOKEN"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CACHE = os.path.join(HERE, "..", "pwg_ru", "nkrya_cache")
FIXTURES = os.path.join(HERE, "fixtures", "nkrya")
MIN_INTERVAL_S = 1.0      # polite: at most one live request per second
MAX_RETRIES = 3           # on 429 / 5xx, exponential backoff
SEED = 5261               # fixed seed -> stable example sorting across runs
SLICE_19C = {"fieldName": "created", "intRange": {"begin": 1800, "end": 1899}}

STORE_HINT = (
    "No NKRYa API token found. Generate a non-expiring key at "
    "https://ruscorpora.ru/accounts/profile/for-devs, then store it:\n"
    "  macOS:   security add-generic-password -a \"$USER\" -s ruscorpora-api -w\n"
    "           (prompts for the key; nothing lands in shell history)\n"
    "  Windows: python -c \"import keyring,getpass; "
    "keyring.set_password('ruscorpora-api','token',getpass.getpass())\"\n"
    "or export %s for one shell." % TOKEN_ENV)


class NkryaError(RuntimeError):
    pass


class NkryaAuthError(NkryaError):
    pass


class NkryaOffline(NkryaError):
    """Raised in offline/fixture mode when a request is not in the cache."""


def load_token():
    tok = os.environ.get(TOKEN_ENV, "").strip()
    if tok:
        return tok
    if sys.platform == "darwin":
        try:
            p = subprocess.run(
                ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
                capture_output=True, text=True, encoding="utf-8", timeout=10)
            if p.returncode == 0 and p.stdout.strip():
                return p.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    try:
        import keyring  # optional; the Windows credential store on MSI
        tok = keyring.get_password(KEYCHAIN_SERVICE, "token")
        if tok:
            return tok.strip()
    except Exception:
        pass
    return None


def request_key(endpoint, payload):
    blob = json.dumps({"endpoint": endpoint, "payload": payload},
                      ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]


class NkryaClient:
    def __init__(self, cache_dir=DEFAULT_CACHE, offline=False, token=None):
        self.cache_dir = os.path.abspath(cache_dir)
        self.offline = offline
        self._token = token
        self._last = 0.0
        self.used_keys = []          # cache entries this client read or wrote

    # ---- transport -------------------------------------------------------
    def _cache_path(self, key):
        return os.path.join(self.cache_dir, key + ".json")

    def _call(self, endpoint, payload, method):
        key = request_key(endpoint, payload)
        path = self._cache_path(key)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                self.used_keys.append(key)
                return json.load(f)["response"]
        if self.offline:
            raise NkryaOffline("not cached (offline): %s %s" % (endpoint, key))
        if self._token is None:
            self._token = load_token()
        if not self._token:
            raise NkryaAuthError(STORE_HINT)
        resp = self._http(endpoint, payload, method)
        os.makedirs(self.cache_dir, exist_ok=True)
        rec = {"request": {"endpoint": endpoint, "method": method, "payload": payload},
               "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "response": resp}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
        self.used_keys.append(key)
        return resp

    def _http(self, endpoint, payload, method):
        url = API + endpoint
        headers = {"Authorization": "Bearer " + self._token,
                   "Accept": "application/json",
                   "User-Agent": "pwg-ru-nkrya-client/1 (H5261)"}
        data = None
        if method == "GET":
            url += "?" + urllib.parse.urlencode(
                {"query": json.dumps(payload, ensure_ascii=False)})
        else:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        for attempt in range(MAX_RETRIES + 1):
            wait = self._last + MIN_INTERVAL_S - time.time()
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    return json.loads(r.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")[:400]
                if e.code in (401, 403):
                    raise NkryaAuthError("NKRYa refused the token (HTTP %d): %s\n%s"
                                         % (e.code, body, STORE_HINT))
                if e.code == 429 or e.code >= 500:
                    if attempt < MAX_RETRIES:
                        time.sleep(2 ** attempt * 2)
                        continue
                raise NkryaError("HTTP %d on %s: %s" % (e.code, endpoint, body))
            except urllib.error.URLError as e:
                if attempt < MAX_RETRIES:
                    time.sleep(2 ** attempt * 2)
                    continue
                raise NkryaError("network error on %s: %s" % (endpoint, e))
        raise NkryaError("retries exhausted on %s" % endpoint)

    # ---- queries ---------------------------------------------------------
    def _portrait(self, lemma, pos, result_type, corpus="MAIN"):
        # word-portrait indexes lemmas without ё: "сплочённый" -> null, "сплоченный" -> 0.94 ipm
        # (live, 23-09-2026). Concordance search handles ё itself, so only portraits fold it.
        payload = {"lemma": yo_fold(lemma), "corpus": {"type": corpus},
                   "resultType": [result_type], "seed": SEED}
        if pos:
            payload["pos"] = pos
        return self._call("/word-portrait/", payload, "GET")

    def sketch(self, lemma, pos=None, corpus="MAIN"):
        """{relation: [(collocate, dice), ...]} ranked as returned (dice desc, top 10)."""
        raw = self._portrait(lemma, pos, "PORTRAIT_SKETCH", corpus)
        rels = {}
        for block in (raw.get("sketchData") or {}).get("collocates") or []:
            rel = block.get("sketchSynRelation") or "?"
            rows = []
            for c in block.get("collocations") or []:
                word = ((c.get("collocate") or {}).get("valString") or {}).get("v")
                dice = next((m.get("value") for m in c.get("metrics") or []
                             if m.get("name") in ("dice", "logDice")), None)
                if word:
                    rows.append((word, dice))
            rels[rel] = rows
        return rels

    def freq(self, lemma, pos=None, corpus="MAIN"):
        """{'ipm': float|None, 'category': int|None}."""
        raw = self._portrait(lemma, pos, "PORTRAIT_FREQUENCY", corpus)
        fd = raw.get("frequencyData") or {}
        return {"ipm": fd.get("ipm"), "category": fd.get("category")}

    def concordance(self, lexgramm, n=3, corpus="MAIN", subcorpus_conditions=None):
        """{'hits': int|None, 'docs': int|None, 'lines': [str]} for a lexGramm form."""
        payload = {"corpus": {"type": corpus}, "lexGramm": lexgramm,
                   "params": {"pageParams": {"page": 0, "docsPerPage": n,
                                             "snippetsPerDoc": 1},
                              "seed": SEED}}
        if subcorpus_conditions:
            payload["subcorpus"] = {"sectionValues": [
                {"conditionValues": list(subcorpus_conditions)}]}
        raw = self._call("/lex-gramm/concordance", payload, "POST")
        qs = raw.get("queryStats") or {}
        return {"hits": qs.get("wordUsageCount"), "docs": qs.get("textCount"),
                "lines": snippet_lines(raw, n)}

    def pair(self, modifier, head, n=3, dist=(1, 3), slice_19c=False, corpus="MAIN"):
        """Concordance of lemma `modifier` followed within `dist` words by lemma `head`."""
        return self.concordance(pair_query(modifier, head, dist), n=n, corpus=corpus,
                                subcorpus_conditions=[SLICE_19C] if slice_19c else None)


def pair_query(first, second, dist=(1, 3)):
    return {"sectionValues": [{
        "conditionValues": [{"fieldName": "disambmod", "text": {"v": "main"}},
                            {"fieldName": "distmod", "text": {"v": "with_zeros"}}],
        "subsectionValues": [
            {"conditionValues": [{"fieldName": "lex", "text": {"v": first}}]},
            {"conditionValues": [{"fieldName": "lex", "text": {"v": second}},
                                 {"fieldName": "dist",
                                  "intRange": {"begin": dist[0], "end": dist[1]}}]}]}]}


def snippet_lines(raw, n):
    """Render up to n concordance snippets; hit words wrapped in [ ]."""
    out = []
    for group in raw.get("groups") or []:
        for doc in group.get("docs") or []:
            title = ((doc.get("info") or {}).get("title") or "").strip()
            for sg in doc.get("snippetGroups") or []:
                for snip in sg.get("snippets") or []:
                    parts = []
                    for seq in snip.get("sequences") or []:
                        for w in seq.get("words") or []:
                            t = w.get("text") or ""
                            if (w.get("displayParams") or {}).get("hit"):
                                t = "[" + t + "]"
                            parts.append(t)
                    text = " ".join("".join(parts).split())
                    if text:
                        out.append(text + (" — " + title if title else ""))
                    if len(out) >= n:
                        return out
    return out


def yo_fold(s):
    """ё/Ё -> е/Е — NKRYa word portraits key lemmas without ё."""
    return s.replace("ё", "е").replace("Ё", "Е") if s else s


def rank_in(rows, word):
    """1-based rank of word in a sketch relation list, or None (not in the top 10)."""
    for i, (w, _d) in enumerate(rows, 1):
        if yo_fold(w) == yo_fold(word):
            return i, _d
    return None, None


# ---- selftest (offline, recorded doc-shaped fixtures) -----------------------
def selftest():
    import shutil
    import tempfile

    fx = os.path.abspath(FIXTURES)
    cli = NkryaClient(cache_dir=fx, offline=True)

    # 1. sketch parse on the official `слово` example shape
    rels = cli.sketch("слово", "S")
    assert rels["amod_S_A"][0] == ("честный", 10.3028), rels["amod_S_A"][:2]
    assert len(rels["amod_S_A"]) == 10
    assert "nsubj_S_V" in rels and rels["nsubj_S_V"][0][0] == "звучать"
    assert rank_in(rels["amod_S_A"], "добрый") == (4, 8.57147)
    assert rank_in(rels["amod_S_A"], "сплочённый") == (None, None)
    # ё-fold (23-09-2026): portraits key lemmas without ё; matching ignores ё both ways
    assert yo_fold("сплочённый") == "сплоченный" and yo_fold("Ёж") == "Еж"
    assert rank_in([("черный", 1.0)], "чёрный") == (1, 1.0)

    # 2. freq parse (official `кошка` example: ipm 44.0418, category 3)
    assert cli.freq("кошка", "S") == {"ipm": 44.0418, "category": 3}

    # 3. concordance: stats + hit marking + n cap
    c = cli.pair("чёрный", "кошка", n=2)
    assert c["hits"] == 137 and c["docs"] == 98, c
    assert len(c["lines"]) == 2 and "[чёрная] [кошка]" in c["lines"][0], c["lines"]

    # 4. offline miss fails loudly, never silently empty
    try:
        cli.freq("несуществующее", "S")
        raise AssertionError("offline miss must raise")
    except NkryaOffline:
        pass

    # 5. cache key is stable and order-insensitive
    assert request_key("/x", {"a": 1, "b": 2}) == request_key("/x", {"b": 2, "a": 1})
    assert request_key("/x", {"a": 1}) != request_key("/y", {"a": 1})

    # 6. no token -> fail closed with the storing hint, before any network
    tmp = tempfile.mkdtemp()
    try:
        saved = os.environ.pop(TOKEN_ENV, None)
        live = NkryaClient(cache_dir=tmp, token="")
        try:
            live.freq("туча", "S")
            raise AssertionError("empty token must fail closed")
        except NkryaAuthError as e:
            assert "security add-generic-password" in str(e)
        finally:
            if saved is not None:
                os.environ[TOKEN_ENV] = saved

        # 7. a live response is written to the cache and re-read without network
        live = NkryaClient(cache_dir=tmp, token="dummy")
        live._http = lambda ep, pl, m: {"frequencyData": {"ipm": 1.5, "category": 2}}
        assert live.freq("туча", "S")["ipm"] == 1.5
        again = NkryaClient(cache_dir=tmp, offline=True)
        assert again.freq("туча", "S") == {"ipm": 1.5, "category": 2}
        assert len(os.listdir(tmp)) == 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("nkrya_client selftest OK (7 checks, offline fixtures: %s)" % os.path.relpath(fx))


def main(argv=None):
    ap = argparse.ArgumentParser(description="NKRYa evidence client (H5261)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--offline", action="store_true", help="cache only, no network")
    ap.add_argument("--cache", default=DEFAULT_CACHE)
    ap.add_argument("cmd", nargs="?", choices=["probe", "sketch", "freq", "pair"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--19c", dest="c19", action="store_true")
    ap.add_argument("-n", type=int, default=3)
    a = ap.parse_args(argv)
    if a.selftest:
        selftest()
        return 0
    if not a.cmd:
        ap.error("command required")
    cli = NkryaClient(cache_dir=a.cache, offline=a.offline)
    try:
        if a.cmd == "probe":
            tok = load_token()
            if not tok:
                raise NkryaAuthError(STORE_HINT)
            cli._token = tok
            me = cli._http("/auth/check-authenticated/", {}, "GET")
            print("auth:", json.dumps(me, ensure_ascii=False))
            c = cli.pair("чёрный", "туча", n=1, slice_19c=True)
            print("19c subcorpus accepted: hits=%s" % c["hits"])
        elif a.cmd == "sketch":
            for rel, rows in cli.sketch(*a.args).items():
                print(rel, ", ".join("%s %.2f" % (w, d or 0) for w, d in rows))
        elif a.cmd == "freq":
            print(json.dumps(cli.freq(*a.args), ensure_ascii=False))
        elif a.cmd == "pair":
            print(json.dumps(cli.pair(a.args[0], a.args[1], n=a.n, slice_19c=a.c19),
                             ensure_ascii=False, indent=1))
    except NkryaError as e:
        print("NKRYa: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
