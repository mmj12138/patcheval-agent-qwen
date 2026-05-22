# Author: mmj
# DATE: 11.05.2026
import json
import os

from config import PROJECT_ROOT


KNOWLEDGE_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "tools",
    "cwe_repair_strategies_auto.json",
)


def load_knowledge():
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def score_item(info, item):
    score = 0

    cwe_ids = info.get("cwe_id", [])
    language = info.get("language", "").lower()
    code = info.get("code", "").lower()
    description = info.get("description", "").lower()

    if item.get("cwe") in cwe_ids:
        score += 5

    if item.get("language", "").lower() == language:
        score += 2

    for kw in item.get("keywords", []):
        kw = kw.lower()
        if kw in code:
            score += 1
        if kw in description:
            score += 1

    return score

def retrieve_repair_strategies(info, top_k=4):
    knowledge = load_knowledge()
    cwe_info = info.get("cwe_info", {}) or {}
    target_cwes = set(cwe_info.keys())

    selected = []
    seen = set()

    # 1. Exact CWE match first
    for item in knowledge:
        cwe = item.get("cwe")
        if cwe in target_cwes and cwe not in seen:
            selected.append(item)
            seen.add(cwe)

    # 2. Then ranked semantic/keyword fallback
    ranked = []
    for item in knowledge:
        cwe = item.get("cwe")
        if cwe in seen:
            continue

        score = score_item(info, item)
        if score > 0:
            ranked.append((score, item))

    ranked.sort(key=lambda x: x[0], reverse=True)

    for _, item in ranked:
        if len(selected) >= top_k:
            break

        cwe = item.get("cwe")
        if cwe not in seen:
            selected.append(item)
            seen.add(cwe)

    if not selected:
        return (
            "General repair strategy:\n"
            "- Identify user-controlled input.\n"
            "- Identify the dangerous sink.\n"
            "- Apply the smallest validation, sanitization, escaping, "
            "bounds checking, authorization, or parameterization fix.\n"
            "- Preserve existing control flow and error handling.\n"
            "- Do not rewrite unrelated code."
        )

    return "\n".join(
        f"- {item.get('cwe')} / {item.get('title')}: {item.get('repair_hint')}"
        for item in selected
    )