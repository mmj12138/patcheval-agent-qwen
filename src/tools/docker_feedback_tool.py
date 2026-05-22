# Author: mmj
# DATE: 14.05.2026
import logging

from src.evaluation.run_evaluation import Evaluation


def get_docker_feedback(cve, patch, language, test_name="docker_tool"):
    logger = logging.getLogger(f"docker-feedback-{cve}")
    logger.setLevel(logging.INFO)

    evaluation = Evaluation(logger=logger)

    poc_ok, poc_msg, unit_ok, unit_msg, error_type = evaluation.run_evaluation(
        cve=cve,
        llm_patch=patch,
        language=language,
        test_name=test_name,
        cve_logs=[],
    )

    success = error_type == "Repair Success"

    feedback = f"""
Docker execution feedback:

error_type:
{error_type}

PoC result:
{poc_ok}

PoC message:
{poc_msg}

Unit test result:
{unit_ok}

Unit test message:
{unit_msg}
""".strip()

    return success, feedback