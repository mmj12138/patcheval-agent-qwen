import re


def clean_patch(text, file_path="file.py"):
    text = text.replace("```diff", "")
    text = text.replace("```patch", "")
    text = text.replace("```python", "")
    text = text.replace("```py", "")
    text = text.replace("```", "")
    text = text.replace("\nPatch:\n", "\n")
    text = text.replace("Patch:\n", "")
    text = text.replace("Minimal patch:", "")
    text = text.strip()

    escaped = re.escape(file_path)

    pattern = (
        rf"(--- a/{escaped}\n"
        rf"\+\+\+ b/{escaped}\n"
        rf".*?)(?=\n(?:Explanation|The patch|This patch|Note:|Output|Please|Here is|$))"
    )

    match = re.search(pattern, text, flags=re.DOTALL)
    if match:
        patch = match.group(1).strip()
    elif "--- a/" in text:
        patch = text[text.index("--- a/") :].strip()
    else:
        patch = text.strip()

    return patch


def is_valid_unified_diff(patch, file_path):
    if not patch:
        return False

    if not patch.startswith(f"--- a/{file_path}\n+++ b/{file_path}"):
        return False

    if "@@" not in patch:
        return False

    # no ed diff. eg. 2361c2361 / 532a532
    if re.search(r"^\d+[acd]\d+", patch, flags=re.MULTILINE):
        return False

    changed_lines = [
        line for line in patch.splitlines()
        if (line.startswith("+") and not line.startswith("+++"))
        or (line.startswith("-") and not line.startswith("---"))
    ]

    if not changed_lines:
        return False

    bad_phrases = [
        "Minimal patch:",
        "Explanation",
        "Here is",
        "Please",
        "```",
        "python\n",
        "py\n",
    ]

    return not any(x in patch for x in bad_phrases)