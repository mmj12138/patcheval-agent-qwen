# Author: mmj
# DATE: 11.05.2026
import subprocess


def validate_python_compile(file_path, cwd):
    result = subprocess.run(
        ["python", "-m", "py_compile", str(file_path)],
        cwd=cwd,
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        return False, f"python compile failed:\n{result.stderr}"

    return True, "valid"