"""H4204 box census: reconcile the 20 no_pwg_residuals.jsonl keys against the
live pwg-ru-data store (tm/pwg_ru_translated.jsonl) -- has any key healed
since the 2026-07-15 registry snapshot, independent of the frozen pc lane?
Read-only: touches neither the registry nor the store.
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

RESIDUALS = "no_pwg_residuals.jsonl"
STORE = r"C:\Users\user\Documents\GitHub\pwg-ru-data\tm\pwg_ru_translated.jsonl"


def load_residual_keys(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_dict_code(code):
    code = code.lower()
    if code.startswith("nws"):
        return "nws"
    if code in ("pwg", "pw"):
        return "pw"
    return code


def store_root_layer_pairs(path):
    """Store rows key on 'root'/'safe_root' + 'layer', not the registry's
    synthetic 'word~~h0_zz_<dict>' locator -- collect (root, dict_code)
    pairs so a registry key can be checked root+dict, not root alone
    (root alone false-positives across dictionaries sharing a headword)."""
    pairs = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            code = normalize_dict_code(row.get("layer") or "")
            prov = row.get("provenance") or {}
            for field in ("root", "safe_root"):
                v = prov.get(field)
                if v:
                    pairs.add((v.lower(), code))
            subcard = row.get("subcard")
            if subcard:
                pairs.add((subcard.split("~~", 1)[0].lower(), code))
    return pairs


def main():
    residuals = load_residual_keys(RESIDUALS)
    store_pairs = store_root_layer_pairs(STORE)
    print(f"registry rows: {len(residuals)}")
    print(f"store distinct (root, dict) pairs: {len(store_pairs)}")
    print()
    healed = []
    still_blocked = []
    for row in residuals:
        key = row["key"]
        base, _, locator = key.partition("~~")
        root = base.lower()
        raw_code = locator.rsplit("_", 1)[-1].lower() if "_" in locator else ""
        dict_code = normalize_dict_code(raw_code)
        if (root, dict_code) in store_pairs:
            healed.append(row)
        else:
            still_blocked.append(row)
    print(f"already healed (present in store, independent of freeze): {len(healed)}")
    for row in healed:
        print(f"  HEALED  {row['key']}  reason={row['reason']}")
    print()
    print(f"still blocked (absent from store): {len(still_blocked)}")
    for row in still_blocked:
        print(f"  BLOCKED {row['key']}  reason={row['reason']}")


if __name__ == "__main__":
    main()
