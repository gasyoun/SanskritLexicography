#!/usr/bin/env python3
"""Rebuild the Zaliznyak archive transcript census + index.

Reads a listing of the yadisk "ААЗализняк-архив" remote (produced by
`rclone lsf yadisk:ААЗализняк-архив -R --files-only --format tsp`, ";"
separated: mtime;size;path) and emits transcript_index.tsv — one row per
(folder, basename) group that has at least one text-layer file.

Rerun after re-listing the remote:
    rclone lsf "yadisk:ААЗализняк-архив" -R --files-only --format tsp \
        > listing.tsv
    python3 build_census.py listing.tsv transcript_index.tsv
"""
import csv
import re
import sys
import collections

TEXT_EXTS = {"txt", "srt", "json", "ans", "html", "tsv", "vtt"}
MEDIA_EXTS = {"mp3", "mp4", "mkv", "webm"}

TOPIC_KEYWORDS = [
    ("sanskrit_vedic", r"санскрит|ведийск|риг-?вед|\bRV\b|панини|веда"),
    ("birchbark_novgorod", r"берест|новгород"),
    ("russian_diachrony", r"истори[ияи].*(язык|ударен)|контуры истории"),
    ("interview_conversation", r"беседует|отвечает на вопросы|разговор|интервью"),
    ("velesova_book", r"велесов"),
]


def classify_topic(name):
    low = name.lower()
    tags = [tag for tag, pat in TOPIC_KEYWORDS if re.search(pat, low, re.IGNORECASE)]
    return tags or ["other_unclassified"]


def load_listing(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split(";")
            if len(parts) < 3:
                continue
            mtime, size, remote_path = parts[0], parts[1], ";".join(parts[2:])
            rows.append((mtime, size, remote_path))
    return rows


def group_by_basename(rows):
    groups = collections.defaultdict(dict)
    for mtime, size, path in rows:
        folder, rest = (path.split("/", 1) + [""])[:2] if "/" in path else ("(root)", path)
        m = re.match(r"^(.*)\.([A-Za-z0-9]+)$", rest)
        if not m:
            continue
        base, ext = m.group(1), m.group(2).lower()
        groups[(folder, base)][ext] = (size, mtime)
    return groups


def build_index(groups):
    out = []
    for (folder, base), exts in sorted(groups.items()):
        text_ext = sorted(e for e in exts if e in TEXT_EXTS)
        media_ext = sorted(e for e in exts if e in MEDIA_EXTS)
        if not text_ext:
            continue
        out.append({
            "folder": folder,
            "basename": base,
            "text_formats": ",".join(text_ext),
            "media_formats": ",".join(media_ext) if media_ext else "(none-in-same-folder)",
            "topic_tags": ",".join(classify_topic(base)),
            "text_bytes_total": sum(int(exts[e][0]) for e in text_ext),
        })
    return out


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    listing_path, out_path = sys.argv[1], sys.argv[2]
    rows = load_listing(listing_path)
    groups = group_by_basename(rows)
    index_rows = build_index(groups)
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["folder", "basename", "text_formats", "media_formats", "topic_tags", "text_bytes_total"])
        for r in index_rows:
            w.writerow([r["folder"], r["basename"], r["text_formats"], r["media_formats"], r["topic_tags"], r["text_bytes_total"]])
    print(f"wrote {len(index_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
