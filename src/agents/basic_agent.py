# Author: mmj
# DATE: 10.05.2026

from src.llm.llm import call_llm
from src.utils.patch_cleaner import clean_patch
from config import DEFAULT_PROMPT_PATH
from src.utils.prompt_loader import load_prompt_template

PROMPT_TEMPLATE = load_prompt_template(
    DEFAULT_PROMPT_PATH
)


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


def repair(sample):
    """
    Baseline:
    LLM only, no validation feedback, no retry, no tools.
    """
    info = get_vul_info(sample)

    prompt = build_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])

    patch = clean_patch(raw_patch, info["file_path"])
    return patch