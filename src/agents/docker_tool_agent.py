# Author: mmj
# DATE: 14.05.2026
from config import DOCKER_RETRY_PROMPT_PATH
from src.llm.llm import call_llm
from src.utils.patch_cleaner import clean_patch
from src.utils.prompt_loader import load_prompt_template

from src.agents.basic_agent import get_vul_info, build_prompt
from src.tools.docker_feedback_tool import get_docker_feedback
from src.validators.diff_validator import validate_unified_diff


DOCKER_RETRY_TEMPLATE = load_prompt_template(DOCKER_RETRY_PROMPT_PATH)


def build_docker_retry_prompt(info, bad_patch, docker_feedback):
    return DOCKER_RETRY_TEMPLATE.format(
        docker_feedback=docker_feedback,
        bad_patch=bad_patch,
        file_path=info["file_path"],
        start_line=info["start_line"],
        code=info["code"],
    )


def repair(sample, max_retries=3):
    info = get_vul_info(sample)

    prompt = build_prompt(info)
    raw_patch = call_llm([{"role": "user", "content": prompt}])
    patch = clean_patch(raw_patch, info["file_path"])

    language = info.get("language", "")
    cve = info["cve_id"]

    last_error = None
    same_error_count = 0

    for _ in range(max_retries + 1):
        ok, error = validate_unified_diff(patch, info["file_path"])
        print("[DIFF VALIDATOR]", ok, error)

        if not ok:
            if error == last_error:
                same_error_count += 1
            else:
                same_error_count = 0
            last_error = error

            extra_hint = ""
            if same_error_count >= 1:
                extra_hint = """
    The model repeated the same invalid patch.

    Do NOT repeat the previous patch.
    Preserve all existing control-flow structures such as try/catch.
    Make a smaller patch that only changes the vulnerable sink line.
    """

            retry_prompt = build_docker_retry_prompt(
                info=info,
                bad_patch=patch,
                docker_feedback=f"Static patch validation failed:\n{error}\n{extra_hint}",
            )

            raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
            patch = clean_patch(raw_patch, info["file_path"])
            continue

        success, docker_feedback = get_docker_feedback(
            cve=cve,
            patch=patch,
            language=language,
        )

        if success:
            return patch

        retry_prompt = build_docker_retry_prompt(
            info=info,
            bad_patch=patch,
            docker_feedback=f"Static patch validation failed:\n{error}",
        )
        print("========== RETRY PROMPT ==========")
        print(retry_prompt[:2000])

        raw_patch = call_llm([{"role": "user", "content": retry_prompt}])
        patch = clean_patch(raw_patch, info["file_path"])

    return patch