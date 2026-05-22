# Author: mmj
# DATE: 11.05.2026
import shutil
import subprocess
import tempfile
from pathlib import Path

from src.validators.diff_validator import validate_unified_diff
from src.validators.syntax_validator import validate_python_compile

from src.validators.semantic_validator import validate_meaningful_patch


def build_temp_file(info):
    tmpdir = tempfile.mkdtemp()
    file_path = Path(tmpdir) / info["file_path"]
    file_path.parent.mkdir(parents=True, exist_ok=True)

    start_line = int(info.get("start_line") or 1)
    prefix = "\n" * max(start_line - 1, 0)

    file_path.write_text(prefix + info["code"] + "\n", encoding="utf-8")
    return tmpdir, file_path


def validate_patch(info, patch):
    ok, msg = validate_unified_diff(patch, info["file_path"])
    if not ok:
        return False, msg

    ok, msg = validate_meaningful_patch(patch)

    if not ok:
        return False, msg

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

        language = info.get("language", "").lower()

        if language == "python" or str(file_path).endswith(".py"):
            ok, msg = validate_python_compile(file_path, tmpdir)
            if not ok:
                return False, msg

        return True, "valid"

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)