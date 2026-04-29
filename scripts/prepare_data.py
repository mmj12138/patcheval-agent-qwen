# Author: mmj
# DATE: 29.04.2026
import argparse
import json
import random
from pathlib import Path


SAFE_FIELDS = [
    "cve_id",
    "cve_description",
    "cwe_info",
    "repo",
    "patch_url",
    "programming_language",
    "programing_language",
    "vul_func",
    "poc_patch",
    "unit_test_cmd",
    "poc_test_cmd",
]


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_sample(sample):
    # no fix_func / vul_patch
    return {k: sample.get(k) for k in SAFE_FIELDS if k in sample}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="PatchEval json file")
    parser.add_argument("--output", default="data/input_real.json")
    parser.add_argument("--num", type=int, default=5)
    parser.add_argument("--language", default=None, help="Python / Go / JavaScript")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    data = load_json(Path(args.input))

    if args.language:
        data = [
            x for x in data
            if x.get("programming_language", x.get("programing_language", "")).lower()
            == args.language.lower()
        ]

    data = [normalize_sample(x) for x in data]

    random.seed(args.seed)
    if args.num > 0:
        data = random.sample(data, min(args.num, len(data)))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} samples to {output}")


if __name__ == "__main__":
    main()