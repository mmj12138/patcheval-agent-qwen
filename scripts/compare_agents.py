import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.validators.diff_validator import validate_unified_diff
from src.validators.patch_validator import validate_patch

try:
    from src.validators.patch_validator import is_meaningful_patch
except ImportError:
    def is_meaningful_patch(patch):
        removed = [
            x[1:].strip()
            for x in patch.splitlines()
            if x.startswith("-") and not x.startswith("---")
        ]
        added = [
            x[1:].strip()
            for x in patch.splitlines()
            if x.startswith("+") and not x.startswith("+++")
        ]

        if not patch.strip():
            return False, "empty_patch"

        if not removed and not added:
            return False, "no_actual_change"

        if removed and added and set(removed) == set(added):
            return False, "all_changes_are_noop"

        meaningful_added = [
            x for x in added
            if x and not x.startswith(("#", "//", "/*", "*"))
        ]

        if not meaningful_added:
            return False, "comment_only"

        return True, "meaningful"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_info_map(input_path):
    data = load_json(input_path)
    info_map = {}

    for item in data:
        vul_funcs = item.get("vul_func", [])
        if not vul_funcs:
            continue

        vf = vul_funcs[0]

        info_map[item["cve_id"]] = {
            "cve_id": item["cve_id"],
            "file_path": vf.get("file_path"),
            "language": item.get("programming_language", ""),
            "start_line": vf.get("start_line", 1),
            "code": vf.get("snippet", ""),
        }

    return info_map


def build_patch_map(path):
    data = load_json(path)
    return {item["cve"]: item for item in data}


def infer_file_path_from_patch(patch):
    for line in patch.splitlines():
        if line.startswith("--- a/"):
            return line[len("--- a/"):].strip()
    return None


def eval_patch(info, patch):
    result = {
        "non_empty": False,
        "valid_diff": False,
        "meaningful": False,
        "apply_compile": False,
        "final_pass": False,
        "reason": "",
    }

    if not patch or not patch.strip():
        result["reason"] = "empty_patch"
        return result

    result["non_empty"] = True

    file_path = info.get("file_path") or infer_file_path_from_patch(patch)

    if not file_path:
        result["reason"] = "missing_file_path"
        return result

    ok, msg = validate_unified_diff(patch, file_path)
    if not ok:
        result["reason"] = f"invalid_diff: {msg}"
        return result

    result["valid_diff"] = True

    ok, msg = is_meaningful_patch(patch)
    if not ok:
        result["reason"] = f"meaningless: {msg}"
        return result

    result["meaningful"] = True

    info = dict(info)
    info["file_path"] = file_path

    ok, msg = validate_patch(info, patch)
    if not ok:
        result["reason"] = f"apply_or_compile_fail: {msg.splitlines()[0] if msg else msg}"
        return result

    result["apply_compile"] = True
    result["final_pass"] = True
    result["reason"] = "pass"

    return result


def rate(x, total):
    return f"{x / total * 100:.2f}%" if total else "0.00%"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--basic", required=True)
    parser.add_argument("--feedback", required=True)
    parser.add_argument("--static_tool", required=True)
    parser.add_argument("--dynamic_tool", required=True)
    parser.add_argument("--output_csv", default="outputs/agent_comparison.csv")
    parser.add_argument("--output_md", default="outputs/agent_comparison.md")
    args = parser.parse_args()

    info_map = build_info_map(args.input)

    methods = {
        "basic": build_patch_map(args.basic),
        "feedback": build_patch_map(args.feedback),
        "static_tool": build_patch_map(args.static_tool),
        "dynamic_tool": build_patch_map(args.dynamic_tool),
    }

    all_cves = sorted(set(methods["basic"].keys()) & set(info_map.keys()))

    results = defaultdict(dict)
    failure_types = defaultdict(Counter)

    for cve in all_cves:
        info = info_map[cve]
        for method, patches in methods.items():
            patch = patches.get(cve, {}).get("fix_patch", "")
            res = eval_patch(info, patch)
            results[cve][method] = res

            if not res["final_pass"]:
                failure_types[method][res["reason"].split(":")[0]] += 1

    rows = []

    basic = results

    for method in methods:
        total = len(all_cves)

        non_empty = sum(results[cve][method]["non_empty"] for cve in all_cves)
        valid_diff = sum(results[cve][method]["valid_diff"] for cve in all_cves)
        meaningful = sum(results[cve][method]["meaningful"] for cve in all_cves)
        apply_compile = sum(results[cve][method]["apply_compile"] for cve in all_cves)
        final_pass = sum(results[cve][method]["final_pass"] for cve in all_cves)

        fixed_basic_valid_diff = 0
        fixed_basic_meaningful = 0
        fixed_basic_apply_compile = 0
        fixed_basic_final = 0
        regressions = 0

        if method != "basic":
            for cve in all_cves:
                b = results[cve]["basic"]
                m = results[cve][method]

                if not b["valid_diff"] and m["valid_diff"]:
                    fixed_basic_valid_diff += 1

                if not b["meaningful"] and m["meaningful"]:
                    fixed_basic_meaningful += 1

                if not b["apply_compile"] and m["apply_compile"]:
                    fixed_basic_apply_compile += 1

                if not b["final_pass"] and m["final_pass"]:
                    fixed_basic_final += 1

                if b["final_pass"] and not m["final_pass"]:
                    regressions += 1

        rows.append({
            "method": method,
            "total": total,

            "non_empty": non_empty,
            "non_empty_rate": rate(non_empty, total),

            "valid_diff": valid_diff,
            "valid_diff_rate": rate(valid_diff, total),

            "meaningful": meaningful,
            "meaningful_rate": rate(meaningful, total),

            "apply_compile": apply_compile,
            "apply_compile_rate": rate(apply_compile, total),

            "final_pass": final_pass,
            "final_pass_rate": rate(final_pass, total),

            "fixed_basic_valid_diff": fixed_basic_valid_diff,
            "fixed_basic_meaningful": fixed_basic_meaningful,
            "fixed_basic_apply_compile": fixed_basic_apply_compile,
            "fixed_basic_final": fixed_basic_final,
            "regressions": regressions,
        })

    headers = [
        "method",
        "total",
        "non_empty",
        "non_empty_rate",
        "valid_diff",
        "valid_diff_rate",
        "meaningful",
        "meaningful_rate",
        "apply_compile",
        "apply_compile_rate",
        "final_pass",
        "final_pass_rate",
        "fixed_basic_valid_diff",
        "fixed_basic_meaningful",
        "fixed_basic_apply_compile",
        "fixed_basic_final",
        "regressions",
    ]

    Path(args.output_csv).parent.mkdir(parents=True, exist_ok=True)

    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in rows:
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")

    lines.append("\n## Failure types\n")

    for method in methods:
        lines.append(f"### {method}")
        if not failure_types[method]:
            lines.append("- None")
        else:
            for k, v in failure_types[method].most_common():
                lines.append(f"- {k}: {v}")
        lines.append("")

    lines.append("\n## Per-CVE comparison\n")
    lines.append("| CVE | basic | feedback | static_tool | dynamic_tool |")
    lines.append("| --- | --- | --- | --- | --- |")

    for cve in all_cves:
        row = [cve]
        for method in methods:
            r = results[cve][method]
            if r["final_pass"]:
                status = "PASS"
            elif r["apply_compile"]:
                status = "APPLY_COMPILE_OK"
            elif r["meaningful"]:
                status = "MEANINGFUL_ONLY"
            elif r["valid_diff"]:
                status = "VALID_DIFF_ONLY"
            else:
                status = r["reason"]
            row.append(status)
        lines.append("| " + " | ".join(row) + " |")

    Path(args.output_md).write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines[:8]))
    print(f"\nSaved CSV: {args.output_csv}")
    print(f"Saved Markdown: {args.output_md}")


if __name__ == "__main__":
    main()