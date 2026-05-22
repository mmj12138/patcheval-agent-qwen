# Author: mmj
# DATE: 22.05.2026
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


GENERAL_HINT = (
    "Identify the user-controlled input and the vulnerable sink. "
    "Apply the smallest safe validation, escaping, authorization, or bounds check. "
    "Preserve existing behavior and avoid unrelated rewrites."
)


DEFAULT_HINTS = {
    "CWE-20": "Validate input type, length, range, format, and allowed values before use.",
    "CWE-22": "Normalize and resolve paths, reject traversal, and ensure the final path stays inside the allowed base directory.",
    "CWE-59": "Use secure tempfile APIs and avoid following attacker-controlled symbolic links.",
    "CWE-73": "Do not use user-controlled file paths directly. Validate, normalize, and restrict them to allowed directories.",
    "CWE-77": "Avoid command strings with user input. Use argument lists and validate arguments.",
    "CWE-78": "Avoid shell=True and shell string interpolation. Use subprocess argument lists.",
    "CWE-79": "Escape untrusted output before rendering HTML and avoid marking user data as safe.",
    "CWE-89": "Use parameterized SQL queries and pass user input as bound parameters.",
    "CWE-94": "Avoid eval/exec or dynamic code generation with user-controlled data.",
    "CWE-200": "Avoid exposing sensitive information in responses, errors, logs, or timing differences.",
    "CWE-203": "Use generic responses and constant-time comparisons where appropriate.",
    "CWE-250": "Apply least privilege and avoid unnecessary elevated permissions.",
    "CWE-269": "Enforce privilege checks before sensitive operations.",
    "CWE-285": "Add explicit authorization checks before protected actions.",
    "CWE-287": "Verify authentication state server-side before granting access.",
    "CWE-306": "Require authentication before sensitive endpoints or operations.",
    "CWE-327": "Replace weak cryptographic algorithms with safe alternatives.",
    "CWE-330": "Use cryptographically secure randomness for tokens and secrets.",
    "CWE-347": "Verify signatures against the correct signed object and trusted keys.",
    "CWE-352": "Require and validate CSRF tokens for state-changing requests.",
    "CWE-400": "Add limits, timeouts, size checks, and safe loop termination.",
    "CWE-434": "Validate uploaded file type, size, extension, and storage path.",
    "CWE-502": "Avoid unsafe deserialization of untrusted data.",
    "CWE-522": "Do not expose credentials in logs, URLs, errors, or responses.",
    "CWE-532": "Redact sensitive values before logging.",
    "CWE-601": "Validate redirect targets and allow only same-origin or explicitly allowed redirects.",
    "CWE-639": "Check ownership and authorization before accessing user-controlled object IDs.",
    "CWE-668": "Ensure resources are only exposed to the correct security boundary or authorized actor.",
    "CWE-755": "Handle exceptional paths explicitly and avoid hangs or infinite loops.",
    "CWE-787": "Check buffer sizes and bounds before writing.",
    "CWE-798": "Remove hard-coded credentials and load secrets from secure configuration.",
    "CWE-863": "Verify roles, permissions, and object ownership before sensitive operations.",
    "CWE-918": "Validate outbound URLs, restrict schemes/hosts, and block private/internal IP ranges.",
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_keywords(text):
    candidates = [
        "redirect", "url", "path", "file", "open", "join", "query", "sql",
        "execute", "eval", "exec", "subprocess", "shell", "token", "password",
        "auth", "permission", "role", "signature", "xml", "template", "html",
        "log", "upload", "deserialize", "pickle", "yaml", "request", "response",
        "timeout", "loop", "secret", "csrf", "session", "cookie",
    ]

    text = text.lower()
    return [w for w in candidates if w in text]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="data/tools/cwe_repair_strategies_auto.json")
    parser.add_argument("--min_count", type=int, default=1)
    args = parser.parse_args()

    data = load_json(args.input)

    counter = Counter()
    names = {}
    keyword_counter = defaultdict(Counter)

    for item in data:
        language = item.get("programming_language") or item.get("programing_language") or "Unknown"
        cwe_info = item.get("cwe_info", {}) or {}

        desc = item.get("cve_description", "")
        snippets = " ".join(v.get("snippet", "") for v in item.get("vul_func", []) or [])
        text = desc + " " + snippets

        kws = collect_keywords(text)

        for cwe, meta in cwe_info.items():
            key = (cwe, language)
            counter[key] += 1
            names[cwe] = meta.get("name", cwe)

            for kw in kws:
                keyword_counter[key][kw] += 1

    rows = []

    for (cwe, language), count in counter.most_common():
        if count < args.min_count:
            continue

        hint = DEFAULT_HINTS.get(cwe, GENERAL_HINT)

        rows.append({
            "cwe": cwe,
            "title": names.get(cwe, cwe),
            "language": language,
            "count": count,
            "repair_hint": hint,
        })

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Input cases: {len(data)}")
    print(f"Generated hints: {len(rows)}")
    print(f"Saved to: {output}")

    print("\nTop generated hints:")
    for row in rows[:30]:
        print(f"{row['cwe']} / {row['language']} / {row['count']} - {row['title']}")


if __name__ == "__main__":
    main()