# Author: mmj
# DATE: 14.05.2026
import argparse
import json
import re
from pathlib import Path


def extract_cves_from_images(images_file):
    cves = set()

    with open(images_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            match = re.search(r"(cve-\d{4}-\d+)", line, re.IGNORECASE)
            if match:
                cves.add(match.group(1).upper())

    return cves


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="PatchEval input.json")
    parser.add_argument("--images", required=True, help="images.txt")
    parser.add_argument("--output", required=True, help="filtered output json")
    parser.add_argument("--num", type=int, default=None, help="optional max samples")
    args = parser.parse_args()

    available_cves = extract_cves_from_images(args.images)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    filtered = [
        item for item in data
        if item.get("cve_id", "").upper() in available_cves
    ]

    if args.num is not None:
        filtered = filtered[:args.num]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)

    print(f"Available CVEs in images.txt: {len(available_cves)}")
    print(f"Matched samples: {len(filtered)}")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()