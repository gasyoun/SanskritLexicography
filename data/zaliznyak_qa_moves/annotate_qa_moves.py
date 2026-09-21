#!/usr/bin/env python3
"""H5171 — Q&A move annotation of Zaliznyak transcripts (Socratic-tutor eval corpus).

Reads:
  * 27 timecoded lecture transcripts  <bookindex>/data/imports/lectures-v2/transcripts/*.json
  * itkin school-dialog contexts       <bookindex>/src/content/itkin-i.-b..md, itkin-a.-i..md

Writes (derive-don't-store: this script is the source, JSONL+stats are derived):
  zaliznyak_qa_moves.jsonl — one row per detected move occurrence
      {replica_id, move_class, quote, t, file, source, speaker}
  stats.json               — per-class totals, per-file counts, marker hits

Move classes per Uprava docs/ZALIZNYAK_HINTING_STYLE_ANALYSIS_19-09-2026.md §3:
  answer_hold         (§3.1 ответ-удержание, социальный контракт)
  coinference         (§3.3 совывыведение: вопрос аудитории вместо ответа)
  deferred            (§3.5 отложенное разрешение)
  trap                (§3.7 именование ловушки + перенаправление)
  refusal_generalize  (§3.4 отказ обобщать за ученика)
  uncertainty_sign    (§3.9 знак неуверенности)

Usage: annotate_qa_moves.py --bookindex <path> --out <dir> [--selftest]
Stdlib only. Deterministic. Quotes stay short (legal frame: analysis doc §6.4).
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

MAX_QUOTE = 240
CTX = 90  # context chars each side of the matched marker

# --- marker battery: class -> list of regexes (§2 sweep markers + §3 verbatim evidence)
BATTERY = {
    "answer_hold": [
        r"не\s+(?:нужно\s+|надо\s+)?(?:кричать|выкрикивать|выкрикнуть)",
        r"готовы[ея]\s+(?:знан|ответ)",
        r"дать\s+возможность\s+подумать",
        r"возможность\s+подумать\s+тем",
        r"кто\s+(?:уже\s+)?знает[^.]{0,30}(?:не\s+говор|молч|подожд)",
        r"не\s+подсказывай(?:те|)",
        r"прошу\s+(?:людей\s+)?быть\s+скромными",
        r"не\s+спешите\s+(?:с\s+)?ответ",
    ],
    "coinference": [
        r"как\s+вы\s+думаете",
        r"что\s+вы\s+думаете",
        r"как\s+думаете",
        r"попробуйт[её]",
        r"подумайт[её]",
        r"угада[её]т[её]?",
        r"вы\s+сами\s+вычислит[её]",
        r"давайт[её][^.,!?]{0,40}(?:посмотр|вычисл|подум|попроб|разбер|провер)",
        r"кто\s+(?:нибудь\s+)?(?:скажет|знает|сможет|может)\s*(?:ответить)?\s*\?",
        r"(?:скажите|скажи)те?\s+мн[её][,.]?\s*(?:какое|какой|почему|откуда)",
        r"а\s+почему\s*\?",
        r"почему[^?]{0,50}\?",  # §2 ритм «утверждение → почему? → разбор» (×1281/265)
    ],
    "deferred": [
        r"оставляю\s+[^.]{0,40}(?:нереш|открыт|нере[шш]ён)",
        r"оставим\s+[^.]{0,30}(?:в\s+стороне|пока|нереш|открыт)",
        r"верн[её]мся\s+[^.]{0,30}(?:позже|дальше|к\s+этому|чуть\s+позже)",
        r"(?:мы\s+)?(?:ещ[её]|пока)\s+не\s+(?:будем|готовы)\s+(?:разбирать|решать|говорить)",
        r"до\s+этого\s+(?:ещ[её]\s+)?дойд[её]м",
        r"потом\s+(?:об\s+этом|к\s+этому)\s+(?:поговорим|верн[её]мся|скажем)",
    ],
    "trap": [
        r"ловушк[аиу]",
        r"(?:вы\s+)?не\s+можете\s+вывести",
        r"ищите\s+другие\s+примеры",
        r"не\s+попадитесь",
        r"это[^.]{0,25}ловушк",
    ],
    "refusal_generalize": [
        r"я\s+не\s+буду\s+вам\s+(?:это\s+)?(?:говорить|сказать|сообщать)",
        r"надеюсь[^.]{0,25}вы\s+сами[^.]{0,20}(?:пойм|догад|понял)",
        r"(?:вы\s+сейчас\s+)?сами\s+(?:это\s+)?(?:пойм[её]т[её]|догадаетесь|увидите|пойали)",
        r"(?:вы\s+)?(?:сами\s+)?(?:скажете|скажи)\s+общее",
        r"сказать\s+общее",
        r"я\s+не\s+буду\s+(?:за\s+вас\s+|это\s+)?(?:выводить|обобщать|формулировать)",
    ],
    "uncertainty_sign": [
        r"трудно\s+(?:сказать|судить|решить|представить|вообразить|уследить)",
        r"до\s+конца\s+не\s+ясно",
        r"\bне\s+ясно\b",
        r"\bнеясно\b",
        r"\bспорно\b",
        r"\bосторожно\b",
        r"знак\s+неуверенности",
        r"точно\s+не\s+(?:зна[её]м|можем\s+сказать)",
        r"вы(?:сокой|соко)\s+степени\s+(?:гипотетич|вероятн)",
    ],
}

COMPILED = {
    cls: [re.compile(pat, re.IGNORECASE) for pat in pats]
    for cls, pats in BATTERY.items()
}

# Relaxed battery for itkin dialog windows: BookIndex contexts are ~120-char
# KWIC windows truncated on both sides, so long §3 phrasings rarely survive.
# These short dialog-shaped delegation prompts (§3.10 «Давайте, давайте,
# полностью вычислите значение») fire only on itkin windows.
RELAXED = {
    "coinference": [
        re.compile(r"\bдавайт[её]\b", re.IGNORECASE),
        re.compile(r"вы\s+думаете", re.IGNORECASE),
        re.compile(r"переведит[её]", re.IGNORECASE),
        re.compile(r"вычислит[её]", re.IGNORECASE),
        re.compile(r"что\s+бы\s+это\s+значило", re.IGNORECASE),
        re.compile(r"как\s+будет[^.?!]{0,25}\?", re.IGNORECASE),
        re.compile(r"что\s+значит[^.?!]{0,30}\?", re.IGNORECASE),
    ],
}


def window(text: str, start: int, end: int) -> str:
    a = max(0, start - CTX)
    b = min(len(text), end + CTX)
    quote = text[a:b].replace("\n", " ")
    if a > 0:
        quote = "…" + quote
    if b < len(text):
        quote = quote + "…"
    return quote[:MAX_QUOTE + 2]


def scan_text(text: str, seen_spans: set, relaxed: bool = False):
    """Yield (move_class, quote, marker) for each unique (class, span) hit."""
    batteries = list(COMPILED.items())
    if relaxed:
        batteries += list(RELAXED.items())
    for cls, patterns in batteries:
        for pat in patterns:
            for m in pat.finditer(text):
                key = (cls, m.start() // 40)
                if key in seen_spans:
                    continue
                seen_spans.add(key)
                yield cls, window(text, m.start(), m.end()), m.group(0)


# Speaker markers inside unattributed transcript segments: attribute each match
# to the nearest preceding marker so audience questions («Вопрос из зала:…»)
# don't pollute Zaliznyak's own move classes.
TR_SPEAKERS = re.compile(
    r"(А\.\s*А\.\s*Зализняк|А\.\s*А\.|Зализняк|Из\s+зала|Ответ\s+из\s+зала"
    r"|Вопрос\s+из\s+зала|Студент[ы]?|Слушател[ьяьи])\s*:"
)


def attribute(text: str, pos: int) -> str:
    last = None
    for m in TR_SPEAKERS.finditer(text, 0, pos + 1):
        last = m.group(1)
    if last is None:
        return "А. А. Зализняк"  # default: lecture voice
    if re.search(r"зала|Студент|Слушател", last, re.I):
        return "из зала"
    return "А. А. Зализняк"


def transcript_rows(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    vid = data.get("video_id", path.stem)
    rows = []
    excluded = 0
    for i, seg in enumerate(data.get("segments", [])):
        text = seg.get("text", "")
        t = seg.get("t")
        seen = set()
        for j, (cls, quote, marker) in enumerate(scan_text(text, seen)):
            spk = attribute(text, text.find(marker) if marker in text else 0)
            if spk == "из зала":
                excluded += 1
                continue
            rows.append({
                "replica_id": f"{vid}.s{i:03d}.m{j:02d}",
                "move_class": cls,
                "quote": quote,
                "marker": marker,
                "t": t,
                "file": vid,
                "source": "lectures-v2/transcripts",
                "speaker": spk,
            })
    return vid, rows, excluded


SPEAKER_RE = re.compile(
    r"(А\.\s*З\.|И\.\s*Б\.\s*Иткин|Из\s+зала|Саша\s+Иткин|А\.\s*А\.\s*Зализняк)"
)


def itkin_rows(path: Path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"```json\n(.*?)\n```", text, re.S)
    if not m:
        return [], {}
    data = json.loads(m.group(1))
    base = re.sub(r"[^a-z-]", "-", path.stem.lower().replace(".", "-"))
    stem = base if base.startswith("itkin") else "itkin-" + base
    stem = re.sub(r"-{2,}", "-", stem).strip("-")
    all_rows = []
    for book, occ in (data.get("occurrences") or {}).items():
        contexts = occ.get("contexts", [])
        pages = occ.get("pages", [])
        for k, ctx in enumerate(contexts):
            page = pages[k] if k < len(pages) else None
            # the BookIndex contexts are truncated KWIC windows around Иткин
            # mentions — replica attribution is unreliable, so the whole window
            # is scanned as one dialog unit (speaker left null).
            seen = set()
            for n, (cls, quote, marker) in enumerate(scan_text(ctx, seen, relaxed=True)):
                all_rows.append({
                    "replica_id": f"{stem}.ctx{k:03d}.m{n:02d}",
                    "move_class": cls,
                    "quote": quote,
                    "marker": marker,
                    "t": None,
                    "file": stem,
                    "source": f"BookIndex/src/content/{path.name}",
                    "speaker": None,
                    "page": page,
                    "book": book,
                })
    return stem, all_rows


def selftest():
    """Positive controls from §3 verbatim evidence; negative control: neutral text."""
    fixtures = {
        "answer_hold": "Я как обычно прошу людей быть скромными и не крикнуть свои готовые знания.",
        "coinference": "Как вы думаете, кто здесь на самом деле является прямым дополнением?",
        "deferred": "я пока оставляю этот вопрос нерешённым, мы с вами попробуем его решить дальше",
        "trap": "Это трудно. Это, на самом деле, немножко ловушка такая.",
        "refusal_generalize": "попробуйте… сказать общее… Я не буду вам сам говорить.",
        "uncertainty_sign": "Как по количеству сгоревшего очень трудно сказать… ставим такой знак неуверенности.",
    }
    ok = True
    for cls, text in fixtures.items():
        seen = set()
        got = {c for c, _, _ in scan_text(text, seen)}
        if cls not in got:
            print(f"SELFTEST FAIL: {cls} not detected in: {text}", file=sys.stderr)
            ok = False
    seen = set()
    neutral = "Слово береста встречается в новгородских грамотах четырнадцатого века."
    got = list(scan_text(neutral, seen))
    if got:
        print(f"SELFTEST FAIL: neutral text produced {got}", file=sys.stderr)
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bookindex")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)
    if not args.bookindex or not args.out:
        ap.error("--bookindex and --out are required (or use --selftest)")

    bi = Path(args.bookindex)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    all_rows = []
    per_file = {}
    excluded_total = 0
    tdir = bi / "data" / "imports" / "lectures-v2" / "transcripts"
    for p in sorted(tdir.glob("*.json")):
        vid, rows, excluded = transcript_rows(p)
        all_rows.extend(rows)
        excluded_total += excluded
        per_file[vid] = Counter(r["move_class"] for r in rows)
    for name in ("itkin-i.-b..md", "itkin-a.-i..md"):
        p = bi / "src" / "content" / name
        if p.exists():
            stem, rows = itkin_rows(p)
            all_rows.extend(rows)
            per_file[stem] = Counter(r["move_class"] for r in rows)

    marker_hits = Counter(r["marker"].lower() for r in all_rows)
    class_totals = Counter(r["move_class"] for r in all_rows)
    stats = {
        "schema": "zaliznyak_qa_moves_stats/1",
        "tool": "data/zaliznyak_qa_moves/annotate_qa_moves.py",
        "inputs": {
            "transcripts": str(tdir),
            "itkin": ["src/content/itkin-i.-b..md", "src/content/itkin-a.-i..md"],
        },
        "files_annotated": len(per_file),
        "files_with_rows": len({r["file"] for r in all_rows}),
        "rows_total": len(all_rows),
        "rows_excluded_audience_speaker": excluded_total,
        "class_totals": dict(sorted(class_totals.items())),
        "per_file": {f: dict(c) for f, c in sorted(per_file.items())},
        "top_markers": dict(marker_hits.most_common(25)),
        "provenance": "H5171; classes per Uprava docs/ZALIZNYAK_HINTING_STYLE_ANALYSIS_19-09-2026.md §3",
    }
    with (out / "zaliznyak_qa_moves.jsonl").open("w", encoding="utf-8") as f:
        for r in all_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: stats[k] for k in ("files_annotated", "rows_total", "class_totals")},
                     ensure_ascii=False, indent=2))
    missing = set(BATTERY) - set(class_totals)
    if missing:
        print(f"WARNING: classes with zero rows: {sorted(missing)}", file=sys.stderr)


if __name__ == "__main__":
    main()
