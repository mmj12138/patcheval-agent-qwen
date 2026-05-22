# Author: mmj
# DATE: 11.05.2026
import re


def validate_unified_diff(patch, file_path):
    if not patch or not patch.strip():
        return False, "Patch is empty."

    expected_header = f"--- a/{file_path}\n+++ b/{file_path}"

    if not patch.startswith(expected_header):
        return (
            False,
            f"Patch header is invalid. It must start exactly with:\n{expected_header}",
        )

    if "@@" not in patch:
        return False, "Patch is header-only or missing @@ hunk."

    bad_phrases = [
        "Corrected code:",
        "Human resources",
        "context line",
        "vulnerable line",
        "fixed line",
        "This patch",
        "Explanation",
        "Regenerate a corrected patch",
        "Vulnerable code:",
        "Rules:",
        "Assistant:",
    ]

    for phrase in bad_phrases:
        if phrase in patch:
            return False, f"Patch contains prompt pollution or placeholder text: '{phrase}'."

    if re.search(r"^\d+[acd]\d+", patch, flags=re.MULTILINE):
        return False, "Patch uses ed-style diff format instead of unified diff."

    lines = patch.splitlines()

    removed = [
        line[1:].strip()
        for line in lines
        if line.startswith("-") and not line.startswith("---")
    ]

    added = [
        line[1:].strip()
        for line in lines
        if line.startswith("+") and not line.startswith("+++")
    ]

    if not removed and not added:
        return False, "Patch contains no actual added or removed code lines."

    if removed and added and set(removed) == set(added):
        return False, "Patch only replaces lines with identical content."

    if added and all(x.startswith("#") or not x for x in added):
        return False, "Patch only adds or modifies comments, not executable security logic."

    if any(x.startswith("def ") for x in added):
        return False, "Patch appears to add a duplicate function definition instead of modifying existing code."

    unrelated = [
        "import ssl",
        "smtplib",
        "smtp.example.com",
        "server.login",
        "Human resources",
    ]

    for phrase in unrelated:
        if phrase in patch:
            return False, f"Patch adds unrelated or suspicious code: {phrase}"

    if len(added) > 20:
        return False, "Patch adds too many lines; expected a minimal fix."

    if removed and added and set(removed) == set(added):
        return False, "Patch replaces lines with identical content."

    dangerous_patterns = [
        ("verify_password(request.vars.password[:1024])", "verify_password(request.vars.password)",
         "Patch removes password length limit."),
        ("if not userobj.email", "if userobj.email",
         "Patch reverses email existence check."),
    ]

    for old, new, reason in dangerous_patterns:
        if old in patch and new in patch:
            return False, reason

    # 1. 删除 try/catch 但没有补回
    for token in ["try {", "catch", "try:", "except"]:
        removed_has = any(token in x for x in removed)
        added_has = any(token in x for x in added)
        if removed_has and not added_has:
            return False, f"Patch removes control-flow/error-handling structure '{token}' without replacement."

    # 2. 修改行里存在 no-op
    for r in removed:
        if r in added:
            return False, f"Patch contains no-op replacement: '{r}'"

    return True, "valid"


def is_valid_unified_diff(patch, file_path):
    ok, _ = validate_unified_diff(patch, file_path)
    return ok