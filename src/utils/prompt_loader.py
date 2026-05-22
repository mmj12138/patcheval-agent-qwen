# Author: mmj
# DATE: 10.05.2026

from functools import lru_cache

# read once time
@lru_cache(maxsize=None)
def load_prompt_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()