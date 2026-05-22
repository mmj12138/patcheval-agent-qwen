# Author: mmj
# DATE: 22.05.2026
# Author: mmj
# DATE: 22.05.2026

import argparse
import json
from pathlib import Path


def load_summary(eval_root, method):
    summary_path = Path(eval_root) / method / "summary.json"

    if not summary_path.exists():
        raise FileNotFoundError(f"summary.json not found: {summary_path}")

    with open(summary_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_metrics(method, summary):
    strict = summary.get("strict_evaluation", {})
    poc = summary.get("poc_only_evaluation", {})
    failure = summary.get("failure_analysis", {})
    breakdown = failure.get("breakdown", {})

    total = strict.get("total_cases", 0)

    apply_fail = sum(
        count for key, count in breakdown.items()
        if "apply_fail" in key
    )

    validation_fail = sum(
        count for key, count in breakdown.items()
        if "validation_fail" in key
    )

    compilation_fail = sum(
        count for key, count in breakdown.items()
        if "compilation_fail" in key
    )

    missing_language = sum(
        count for key, count in breakdown.items()
        if "missing_language" in key
    )

    known_fail = apply_fail + validation_fail + compilation_fail + missing_language
    other_fail = max(total - strict.get("total_success", 0) - known_fail, 0)

    return {
        "method": method,
        "total": total,
        "strict_success": strict.get("total_success", 0),
        "strict_rate": strict.get("pass_rate", "0.00%"),
        "poc_success": poc.get("total_success", 0),
        "poc_rate": poc.get("pass_rate", "0.00%"),
        "apply_fail": apply_fail,
        "validation_fail": validation_fail,
        "compilation_fail": compilation_fail,
        "missing_language": missing_language,
        "other_fail": other_fail,
    }


def print_markdown_table(rows):
    headers = [
        "method",
        "total",
        "strict_success",
        "strict_rate",
        "poc_success",
        "poc_rate",
        "apply_fail",
        "validation_fail",
        "compilation_fail",
        "missing_language",
        "other_fail",
    ]

    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        print("| " + " | ".join(str(row[h]) for h in headers) + " |")


def save_csv(rows, output_csv):
    headers = [
        "method",
        "total",
        "strict_success",
        "strict_rate",
        "poc_success",
        "poc_rate",
        "apply_fail",
        "validation_fail",
        "compilation_fail",
        "missing_language",
        "other_fail",
    ]

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for row in rows:
            f.write(",".join(str(row[h]) for h in headers) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval_root",
        default="evaluation_output",
        help="Root directory containing evaluation output folders",
    )
    parser.add_argument(
        "--methods",
        nargs="+",
        required=True,
        help="Evaluation output folder names",
    )
    parser.add_argument(
        "--output_csv",
        default="outputs/eval_summary.csv",
        help="Output CSV path",
    )

    args = parser.parse_args()

    rows = []

    for method in args.methods:
        summary = load_summary(args.eval_root, method)
        rows.append(extract_metrics(method, summary))

    print_markdown_table(rows)
    save_csv(rows, args.output_csv)

    print(f"\nSaved CSV to: {args.output_csv}")


if __name__ == "__main__":
    main()