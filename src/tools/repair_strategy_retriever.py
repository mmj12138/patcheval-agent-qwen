# Author: mmj
# DATE: 11.05.2026
import json
import os

from config import PROJECT_ROOT


KNOWLEDGE_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "tool_knowledge",
    "cwe_repair_strategies.json",
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


def retrieve_repair_strategies(info, top_k=2):
    knowledge = load_knowledge()

    ranked = []
    for item in knowledge:
        score = score_item(info, item)
        if score > 0:
            ranked.append((score, item))

    ranked.sort(key=lambda x: x[0], reverse=True)
    selected = [item for _, item in ranked[:top_k]]

    if not selected:
        return (
            "General repair strategy: identify user-controlled input, "
            "identify the dangerous sink, and apply the smallest validation, "
            "sanitization, escaping, bounds checking, or parameterization fix."
        )

    return "\n".join(
        f"- {item['cwe']} / {item['title']}: {item['repair_hint']}"
        for item in selected
    )