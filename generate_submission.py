#!/usr/bin/env python3
"""
Generate submission.jsonl from canonical test pairs (T01 - T30).
Conforms to §7.2 of challenge-brief.md.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from bot import compose


def main():
    root = Path(__file__).parent
    dataset_dir = root / "dataset"
    expanded_dir = dataset_dir / "expanded"

    test_pairs_path = expanded_dir / "test_pairs.json"
    if not test_pairs_path.exists():
        print(f"Error: {test_pairs_path} not found!")
        sys.exit(1)

    with open(test_pairs_path) as f:
        pairs_data = json.load(f)

    pairs = pairs_data.get("pairs", [])
    print(f"Found {len(pairs)} canonical test pairs.")

    # Helper loaders
    def load_category(slug: str) -> dict:
        for p in [expanded_dir / "categories" / f"{slug}.json", dataset_dir / "categories" / f"{slug}.json"]:
            if p.exists():
                with open(p) as f:
                    return json.load(f)
        return {"slug": slug, "voice": {}}

    def load_merchant(mid: str) -> dict:
        for p in (expanded_dir / "merchants").glob(f"{mid}*.json"):
            with open(p) as f:
                return json.load(f)
        # Check merchants_seed
        seed_p = dataset_dir / "merchants_seed.json"
        if seed_p.exists():
            with open(seed_p) as f:
                for m in json.load(f).get("merchants", []):
                    if m["merchant_id"] == mid:
                        return m
        return {"merchant_id": mid, "identity": {"name": mid}}

    def load_customer(cid: str) -> dict:
        for p in (expanded_dir / "customers").glob(f"{cid}*.json"):
            with open(p) as f:
                return json.load(f)
        seed_p = dataset_dir / "customers_seed.json"
        if seed_p.exists():
            with open(seed_p) as f:
                for c in json.load(f).get("customers", []):
                    if c["customer_id"] == cid:
                        return c
        return {"customer_id": cid, "identity": {"name": "Customer"}}

    def load_trigger(tid: str) -> dict:
        for p in (expanded_dir / "triggers").glob(f"{tid}*.json"):
            with open(p) as f:
                return json.load(f)
        seed_p = dataset_dir / "triggers_seed.json"
        if seed_p.exists():
            with open(seed_p) as f:
                for t in json.load(f).get("triggers", []):
                    if t["id"] == tid:
                        return t
        return {"id": tid, "kind": "generic", "payload": {}}

    out_file = root / "submission.jsonl"
    lines = []

    for item in pairs:
        test_id = item["test_id"]
        tid = item["trigger_id"]
        mid = item["merchant_id"]
        cid = item.get("customer_id")

        trg = load_trigger(tid)
        merchant = load_merchant(mid)
        cat_slug = merchant.get("category_slug", "general")
        category = load_category(cat_slug)
        customer = load_customer(cid) if cid else None

        result = compose(category, merchant, trg, customer)

        row = {
            "test_id": test_id,
            "body": result["body"],
            "cta": result["cta"],
            "send_as": result["send_as"],
            "suppression_key": result["suppression_key"],
            "rationale": result["rationale"]
        }
        lines.append(json.dumps(row, ensure_ascii=False))

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Successfully generated {out_file} with {len(lines)} lines.")


if __name__ == "__main__":
    main()
