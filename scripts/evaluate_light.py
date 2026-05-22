# Author: mmj
# DATE: 10.05.2026

import argparse
import json

from src.agents.basic_agent import get_vul_info
from src.validators.diff_validator import is_valid_unified_diff
from src.validators.patch_validator import validate_patch


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Original PatchEval subset")
    parser.add_argument("--pred", required=True, help="Generated patches json")
    args = parser.parse_args()

    data = load_json(args.input)
    preds = load_json(args.pred)

    gt_by_cve = {x["cve_id"]: x for x in data}

    total = len(preds)
    non_empty = 0
    valid_diff = 0
    validate_ok = 0
    exact_match = 0

    for pred in preds:
        cve = pred["cve"]
        patch = pred.get("fix_patch", "")
        sample = gt_by_cve.get(cve)

        if not sample:
            continue

        info = get_vul_info(sample)

        if patch.strip():
            non_empty += 1

        if is_valid_unified_diff(patch, info["file_path"]):
            valid_diff += 1

        ok, _ = validate_patch(info, patch)
        if ok:
            validate_ok += 1

        gt_patch = sample.get("vul_patch", "").strip()
        if gt_patch and patch.strip() == gt_patch:
            exact_match += 1

    print("Total:", total)
    print("Non-empty:", non_empty, f"{non_empty / total:.2%}")
    print("Valid diff:", valid_diff, f"{valid_diff / total:.2%}")
    print("Apply/compile OK:", validate_ok, f"{validate_ok / total:.2%}")
    print("Exact match:", exact_match, f"{exact_match / total:.2%}")


if __name__ == "__main__":
    main()