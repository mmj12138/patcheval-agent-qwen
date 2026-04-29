from src.llm import call_llm
from src.utils import clean_patch, is_valid_unified_diff
from src.validator import validate_patch


def get_vul_info(sample):
    vul = sample["vul_func"][0]
    return {
        "cve_id": sample.get("cve_id", ""),
        "description": sample.get("cve_description", ""),
        "cwe_info": sample.get("cwe_info", {}),
        "file_path": vul.get("file_path", "file.py"),
        "start_line": vul.get("start_line", 1),
        "end_line": vul.get("end_line", ""),
        "code": vul.get("snippet", ""),
        "language": sample.get("programming_language", ""),
    }


def build_prompt(info):
    return f"""
You are an expert security engineer.

Generate a minimal unified diff patch to fix the vulnerability.

CVE:
{info["cve_id"]}

Language:
{info["language"]}

Description:
{info["description"]}

CWE:
{info["cwe_info"]}

File:
{info["file_path"]}

The vulnerable code starts at line {info["start_line"]}.

Vulnerable code:
{info["code"]}

Strict rules:
- Output ONLY unified diff.
- Do NOT output full source code.
- Do NOT output ed diff format like 123c123.
- Do NOT use markdown.
- Do NOT explain.
- Do NOT add tests.
- Make the smallest possible security fix.
- Use exact file path.

The output must start exactly with:
--- a/{info["file_path"]}
+++ b/{info["file_path"]}

The patch must contain at least one @@ hunk.
"""


def build_retry_prompt(info, bad_patch, error):
    return f"""
Your previous patch was invalid.

Validation error:
{error}

Previous patch:
{bad_patch}

Regenerate a corrected patch.

Rules:
- Output ONLY unified diff.
- Start exactly with:
--- a/{info["file_path"]}
+++ b/{info["file_path"]}
- Must contain @@ hunk.
- Must apply cleanly to the vulnerable code.
- If Python, patched code must compile.
- Do not output full code.
- Do not explain.

The vulnerable code starts at line {info["start_line"]}.

Vulnerable code:
{info["code"]}
"""


def repair_agent(sample, max_retries=3):
    info = get_vul_info(sample)

    prompt = build_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])
    patch = clean_patch(raw_patch, info["file_path"])

    last_error = ""

    for _ in range(max_retries + 1):
        if not is_valid_unified_diff(patch, info["file_path"]):
            last_error = "not a valid unified diff"
        else:
            ok, msg = validate_patch(info, patch)
            if ok:
                return patch
            last_error = msg

        retry_prompt = build_retry_prompt(info, patch, last_error)
        raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
        patch = clean_patch(raw_patch, info["file_path"])

    return ""


def repair_with_refinement(sample):
    return repair_agent(sample)