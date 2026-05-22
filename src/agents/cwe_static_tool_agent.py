# Author: mmj
# DATE: 10.05.2026
from src.llm.llm import call_llm
from src.utils.patch_cleaner import clean_patch
from src.validators.diff_validator import is_valid_unified_diff
from src.validators.patch_validator import validate_patch
from src.agents.basic_agent import get_vul_info, build_prompt
from src.agents.feedback_agent import build_retry_prompt
from src.tools.cwe_hints import get_tool_hint


from config import (
    CWE_TOOL_PROMPT_PATH,
    CWE_TOOL_RETRY_PROMPT_PATH
)
from src.utils.prompt_loader import load_prompt_template

TOOL_TEMPLATE = load_prompt_template(
    CWE_TOOL_PROMPT_PATH
)

TOOL_RETRY_TEMPLATE = load_prompt_template(
    CWE_TOOL_RETRY_PROMPT_PATH
)

def build_tool_prompt(info):
    base_prompt = build_prompt(info)
    tool_hint = get_tool_hint(info)

    return TOOL_TEMPLATE.format(
        base_prompt=base_prompt,
        tool_hint=tool_hint,
    )

def build_tool_retry_prompt(
    info,
    bad_patch,
    error
):
    retry_prompt = build_retry_prompt(
        info,
        bad_patch,
        error
    )

    tool_hint = get_tool_hint(info)

    return TOOL_RETRY_TEMPLATE.format(
        retry_prompt=retry_prompt,
        tool_hint=tool_hint,
    )


def repair(sample, max_retries=3):
    """
    CWE static tool agent:
    LLM + validation feedback + static CWE repair hints.
    """
    info = get_vul_info(sample)

    prompt = build_tool_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])
    patch = clean_patch(raw_patch, info["file_path"])

    for _ in range(max_retries + 1):
        if not is_valid_unified_diff(patch, info["file_path"]):
            error = (
                "Invalid unified diff format. "
                "The patch must start with the correct file path and contain @@ hunks."
            )
        else:
            ok, message = validate_patch(info, patch)
            if ok:
                return patch
            error = message

        retry_prompt = build_tool_retry_prompt(info, patch, error)
        raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
        patch = clean_patch(raw_patch, info["file_path"])

    return patch
