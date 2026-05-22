# Author: mmj
# DATE: 10.05.2026

from src.llm.llm import call_llm
from src.utils.patch_cleaner import clean_patch
from src.validators.diff_validator import validate_unified_diff
from src.validators.patch_validator import validate_patch
from src.agents.basic_agent import get_vul_info, build_prompt
from config import RETRY_PROMPT_PATH
from src.utils.prompt_loader import load_prompt_template

RETRY_PROMPT_TEMPLATE = load_prompt_template(
    RETRY_PROMPT_PATH
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


def repair(sample, max_retries=3):
    """
    Feedback agent:
    LLM -> validate -> if failed, send error feedback -> retry.
    """
    info = get_vul_info(sample)

    prompt = build_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])
    patch = clean_patch(raw_patch, info["file_path"])

    for _ in range(max_retries + 1):
        ok, error = validate_unified_diff(patch, info["file_path"])

        if not ok:
            pass
        else:
            ok, message = validate_patch(info, patch)
            if ok:
                return patch
            error = message

        retry_prompt = build_retry_prompt(info, patch, error)
        raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
        patch = clean_patch(raw_patch, info["file_path"])

    return patch