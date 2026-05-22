# Author: mmj
# DATE: 10.05.2026

import argparse
import json
import os
from tqdm import tqdm


def load_agent(agent_name):
    if agent_name == "basic":
        from src.agents.basic_agent import repair
        return repair

    if agent_name == "feedback":
        from src.agents.feedback_agent import repair
        return repair

    if agent_name == "cwe_tool":
        from src.agents.cwe_static_tool_agent import repair
        return repair

    if agent_name == "dynamic_tool":
        from src.agents.dynamic_tool_agent import repair
        return repair

    if agent_name == "docker_tool":
        from src.agents.docker_tool_agent import repair
        return repair

    if agent_name == "tools":
        from src.agents.tool_agent import repair
        return repair

    raise ValueError(f"Unknown agent: {agent_name}")


def run_pipeline(input_file, output_file, agent_name):
    repair = load_agent(agent_name)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    results = []

    for sample in tqdm(data):
        try:
            patch = repair(sample)

            results.append({
                "cve": sample.get("cve_id"),
                "agent": agent_name,
                "fix_patch": patch
            })

        except Exception as e:
            results.append({
                "cve": sample.get("cve_id"),
                "agent": agent_name,
                "fix_patch": "",
                "error": str(e)
            })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Saved results to {output_file}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/processed/input_real.json",
        help="Input JSON file"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON file"
    )
    parser.add_argument(
        "--agent",
        choices=["basic", "feedback", "tools", "cwe_tool", "dynamic_tool", "docker_tool"],
        default="basic",
        help="Agent mode"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.output is None:
        args.output = f"outputs/{args.agent}_patches.json"

    run_pipeline(
        input_file=args.input,
        output_file=args.output,
        agent_name=args.agent
    )