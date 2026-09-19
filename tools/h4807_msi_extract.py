#!/usr/bin/env python3
"""H4807 remote leg: extract Sanskrit-dictionary gloss blocks + Source attributions
from the wisdomlib-scrape JSONL.zst definitions store (read-only).

Run ON the MSI (D:\\Tools\\wisdomlib-scrape). Output: TSV.gz + ASCII stats JSON.
"""
import gzip
import io
import json
import os
import re
import sys
from collections import Counter

import zstandard

STORE = r"D:\Tools\wisdomlib-scrape\out\jsonl\definitions"
OUTDIR = r"D:\Tools\wisdomlib-scrape\out\meta\h4807"
os.makedirs(OUTDIR, exist_ok=True)

# Section-start lines that END a "Sanskrit dictionary" section
SECTION_ENDS = {
    "pali dictionary", "marathi dictionary", "nepali dictionary", "hindi dictionary",
    "bengali dictionary", "kannada dictionary", "telugu dictionary", "tamil dictionary",
    "gujarati dictionary", "urdu dictionary", "see also (relevant definitions)",
    "starts with", "full-text", "relevant text", "dictionaries of indian languages",
    "context information", "prakrit dictionary", "tibetan buddhism includes schools",
    "theravada (major branch of buddhism)", "mahayana (major branch of buddhism)",
    "vajrayana (tibetan buddhism)", "general definition (in sanskrit)",
    "ashram of narayana panditacharya", "vyakarana (sanskrit grammar)",
    "nepali is the primary language", "sanskrit, also spelled", "alias/synonym",
    "index of previous and next words", "history of ancient india",
}
SECTION_ENDS_L = {s.lower() for s in SECTION_ENDS}

stats = Counter()
pages = 0
out_tsv = os.path.join(OUTDIR, "h4807_skt_glosses.tsv.gz")

with gzip.open(out_tsv, "wt", encoding="utf-8", compresslevel=6) as out:
    out.write("slug\tsource\tgloss\n")
    for shard in sorted(os.listdir(STORE)):
        if not shard.endswith(".jsonl.zst"):
            continue
        p = os.path.join(STORE, shard)
        n_shard_pages = 0
        try:
            dctx = zstandard.ZstdDecompressor()
            with open(p, "rb") as fh:
                reader = dctx.stream_reader(fh)
                t = io.TextIOWrapper(io.BufferedReader(reader), encoding="utf-8", errors="replace")
                for line in t:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                    except Exception:
                        stats["json_err"] += 1
                        continue
                    pages += 1
                    n_shard_pages += 1
                    slug = r.get("slug", "")
                    text = r.get("text", "") or ""
                    lines = text.split("\n")
                    # find "Sanskrit dictionary" section spans
                    spans = []
                    i = 0
                    while i < len(lines):
                        if lines[i].strip().lower() == "sanskrit dictionary":
                            j = i + 1
                            while j < len(lines):
                                s = lines[j].strip().lower()
                                if s in SECTION_ENDS_L:
                                    break
                                j += 1
                            spans.append((i + 1, j))
                            i = j
                        else:
                            i += 1
                    if not spans:
                        stats["pages_no_skt_dict"] += 1
                        continue
                    stats["pages_with_skt_dict"] += 1
                    for (a, b) in spans:
                        # split into gloss blocks on Source <NL> :
                        cur = []
                        k = a
                        while k < b:
                            ln = lines[k]
                            if (ln.strip() == "Source" and k + 1 < b
                                    and lines[k + 1].strip() == ":"):
                                src = lines[k + 2].strip() if k + 2 < b else ""
                                gloss = " ".join(x.strip() for x in cur if x.strip())
                                if gloss and src:
                                    stats["gloss_blocks"] += 1
                                    if "cologne digital sanskrit dictionaries" in src.lower():
                                        stats["src_cologne"] += 1
                                    out.write("%s\t%s\t%s\n" % (
                                        slug, src.replace("\t", " "), gloss.replace("\t", " ")))
                                elif gloss:
                                    stats["gloss_no_source"] += 1
                                cur = []
                                k += 3
                            else:
                                cur.append(ln)
                                k += 1
                        # trailing block without Source
                        gloss = " ".join(x.strip() for x in cur if x.strip())
                        if gloss:
                            stats["gloss_no_source"] += 1
        except Exception as e:
            stats["shard_err_%s" % shard] += 1
            sys.stderr.write("ERR %s: %r\n" % (shard, e))
            continue
        stats["pages_shard_" + shard.split(".")[0]] = n_shard_pages

stats["pages_total"] = pages
with open(os.path.join(OUTDIR, "h4807_stats.json"), "w", encoding="utf-8") as f:
    json.dump(dict(stats), f, ensure_ascii=True, indent=1, sort_keys=True)
sys.stdout.write("PAGES %d GLOSSES %d\n" % (pages, stats["gloss_blocks"]))
sys.stdout.write("DONE\n")
