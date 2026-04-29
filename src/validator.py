# Author: mmj
# DATE: 29.04.2026
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def build_temp_file(info):
    tmpdir = tempfile.mkdtemp()
    file_path = Path(tmpdir) / info["file_path"]
    file_path.parent.mkdir(parents=True, exist_ok=True)

    start_line = int(info.get("start_line") or 1)
    prefix = "\n" * max(start_line - 1, 0)

    file_path.write_text(prefix + info["code"] + "\n", encoding="utf-8")
    return tmpdir, file_path


def validate_patch(info, patch):
    if not patch.strip():
        return False, "empty patch"

    if not patch.startswith(f"--- a/{info['file_path']}\n+++ b/{info['file_path']}"):
        return False, "patch header is invalid"

    if "@@" not in patch:
        return False, "missing unified diff hunk"

    tmpdir, file_path = build_temp_file(info)

    try:
        patch_file = Path(tmpdir) / "candidate.patch"
        patch_file.write_text(patch, encoding="utf-8")

        result = subprocess.run(
            ["patch", "-p1", "-i", str(patch_file)],
            cwd=tmpdir,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            return False, f"patch apply failed:\n{result.stderr}\n{result.stdout}"

        if info["language"].lower() == "python" or str(file_path).endswith(".py"):
            result = subprocess.run(
                ["python", "-m", "py_compile", str(file_path)],
                cwd=tmpdir,
                text=True,
                capture_output=True,
            )

            if result.returncode != 0:
                return False, f"python compile failed:\n{result.stderr}"

        return True, "valid"

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)