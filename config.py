import os

MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-Coder-7B-Instruct")
MAX_SAMPLES = int(os.getenv("MAX_SAMPLES", 5))
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", 2048))

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

PROMPT_DIR = os.path.join(PROJECT_ROOT, "prompt")


DEFAULT_PROMPT_PATH = os.getenv(
    "PROMPT_PATH",
    os.path.join(PROMPT_DIR, "default.txt")
)

RETRY_PROMPT_PATH = os.getenv(
    "RETRY_PROMPT_PATH",
    os.path.join(PROMPT_DIR, "retry.txt")
)

TOOL_PROMPT_PATH = os.getenv(
    "TOOL_PROMPT_PATH",
    os.path.join(PROMPT_DIR, "tool.txt")
)

CWE_TOOL_PROMPT_PATH = os.getenv(
    "CWE_TOOL_PROMPT_PATH",
    os.path.join(PROMPT_DIR, "cwe_tool.txt")
)

CWE_TOOL_RETRY_PROMPT_PATH = os.getenv(
    "CWE_TOOL_RETRY_PROMPT_PATH",
    os.path.join(PROMPT_DIR, "cwe_tool_retry.txt")
)

DOCKER_RETRY_PROMPT_PATH = os.path.join(
    PROMPT_DIR,
    "docker_retry.txt"
)