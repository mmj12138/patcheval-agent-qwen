import os

from src.llm.llm import call_llm
from src.utils.patch_cleaner import clean_patch
from src.validators.diff_validator import is_valid_unified_diff


def load_prompt_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEFAULT_PROMPT_PATH = os.path.join(PROJECT_ROOT, "prompt", "default.txt")
DEFAULT_RETRY_PROMPT_PATH = os.path.join(PROJECT_ROOT, "prompt", "retry.txt")

PROMPT_PATH = os.getenv("PROMPT_PATH", DEFAULT_PROMPT_PATH)
RETRY_PROMPT_PATH = os.getenv("RETRY_PROMPT_PATH", DEFAULT_RETRY_PROMPT_PATH)

PROMPT_TEMPLATE = load_prompt_template(PROMPT_PATH)
RETRY_PROMPT_TEMPLATE = load_prompt_template(RETRY_PROMPT_PATH)


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
    return PROMPT_TEMPLATE.format(
        cve_id=info["cve_id"],
        description=info["description"],
        cwe_info=info["cwe_info"],
        language=info["language"],
        file_path=info["file_path"],
        start_line=info["start_line"],
        end_line=info["end_line"],
        code=info["code"],
    )


def build_retry_prompt(info, bad_patch, error):
    return RETRY_PROMPT_TEMPLATE.format(
        error=error,
        bad_patch=bad_patch,
        cve_id=info["cve_id"],
        description=info["description"],
        cwe_info=info["cwe_info"],
        language=info["language"],
        file_path=info["file_path"],
        start_line=info["start_line"],
        end_line=info["end_line"],
        code=info["code"],
    )


def repair_agent(sample, max_retries=3):
    info = get_vul_info(sample)

    prompt = build_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])
    patch = clean_patch(raw_patch, info["file_path"])

    for _ in range(max_retries + 1):
        if is_valid_unified_diff(patch, info["file_path"]):
            return patch

        retry_prompt = build_retry_prompt(
            info,
            patch,
            "not a valid unified diff patch",
        )
        raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
        patch = clean_patch(raw_patch, info["file_path"])

    return patch if is_valid_unified_diff(patch, info["file_path"]) else ""


def repair_with_refinement(sample):
    return repair_agent(sample)