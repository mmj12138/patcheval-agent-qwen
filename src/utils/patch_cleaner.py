# Author: mmj
# DATE: 11.05.2026
import re


def clean_patch(text, file_path="file.py"):
    if not text:
        return ""

    text = text.replace("```diff", "")
    text = text.replace("```patch", "")
    text = text.replace("```python", "")
    text = text.replace("```py", "")
    text = text.replace("```", "")
    text = text.replace("\nPatch:\n", "\n")
    text = text.replace("Patch:\n", "")
    text = text.replace("Minimal patch:", "")
    text = text.strip()

    header = f"--- a/{file_path}\n+++ b/{file_path}"

    # 优先从最后一个正确 header 开始截取，避免前面有 prompt echo
    start = text.rfind(header)

    if start == -1:
        # 如果模型输出 diff --git，也尝试从 --- a/ 开始
        alt = f"--- a/{file_path}"
        start = text.rfind(alt)

    if start == -1:
        return text.strip()

    patch = text[start:].strip()

    # 截掉后面的解释或 prompt echo
    stop_markers = [
        "\nExplanation:",
        "\nThe patch",
        "\nThis patch",
        "\nNote:",
        "\nOutput:",
        "\nPlease",
        "\nHere is",
        "\nRegenerate",
        "\nRules:",
        "\nVulnerable code:",
        "\nCorrected code:",
        "\nAssistant:",
    ]

    for marker in stop_markers:
        idx = patch.find(marker)
        if idx != -1:
            patch = patch[:idx].strip()

    return patch