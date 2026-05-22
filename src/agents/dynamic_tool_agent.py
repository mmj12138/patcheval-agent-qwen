# Author: mmj
# DATE: 11.05.2026
from src.llm.llm import call_llm
from src.utils.patch_cleaner import clean_patch
from src.validators.diff_validator import validate_unified_diff
from src.validators.patch_validator import validate_patch
from src.agents.basic_agent import get_vul_info, build_prompt
from src.agents.feedback_agent import build_retry_prompt
from src.tools.repair_strategy_retriever import retrieve_repair_strategies


def build_dynamic_tool_prompt(info):
    base_prompt = build_prompt(info)
    retrieved_hint = retrieve_repair_strategies(info)

    return f"""
{base_prompt}

# Retrieved Repair Strategy Tool Result
The following repair strategies were retrieved based on the CVE, CWE, language, and vulnerable code:

{retrieved_hint}

# Tool Usage Rules
- Use the retrieved strategies only if they are relevant.
- Do not blindly add unrelated code.
- Modify only the vulnerable logic.
- Keep the patch minimal.
- Output ONLY unified diff.

IMPORTANT PATCH RULES:
- Return a MINIMAL unified diff only.
- Modify the existing vulnerable code instead of rewriting the function.
- Do NOT duplicate functions.
- Do NOT remove try/except or error handling unless necessary.
- Preserve indentation and surrounding structure.
- Avoid no-op changes.
- Do not change unrelated logic.
- Do NOT output unchanged lines as removed/added pairs.
- Use the exact target file path from the prompt header.
- The patch must apply to the vulnerable snippet context.
"""


def build_dynamic_tool_retry_prompt(info, bad_patch, error):
    retry_prompt = build_retry_prompt(info, bad_patch, error)
    retrieved_hint = retrieve_repair_strategies(info)

    return f"""
{retry_prompt}

# Retrieved Repair Strategy Tool Result
{retrieved_hint}

# Retry Guidance
- First fix the validation error.
- Then apply the relevant retrieved repair strategy.
- Avoid duplicate code.
- Avoid comment-only changes.
- Avoid large rewrites.
- Output ONLY unified diff.
"""


def repair(sample, max_retries=3):
    info = get_vul_info(sample)

    prompt = build_dynamic_tool_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])
    patch = clean_patch(raw_patch, info["file_path"])

    for _ in range(max_retries + 1):
        ok, error = validate_unified_diff(patch, info["file_path"])

        if ok:
            ok, message = validate_patch(info, patch)
            if ok:
                return patch
            error = message

        retry_prompt = build_dynamic_tool_retry_prompt(info, patch, error)
        raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
        patch = clean_patch(raw_patch, info["file_path"])

    return patch