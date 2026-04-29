import json
from tqdm import tqdm
from src.agent import repair_with_refinement
from config import MAX_SAMPLES
import os

def run_pipeline(input_file, output_file):
    with open(input_file, "r") as f:
        data = json.load(f)

    results = []

    for sample in tqdm(data[:MAX_SAMPLES]):
        try:
            patch = repair_with_refinement(sample)
            results.append({
                "cve": sample["cve_id"],
                "fix_patch": patch
            })
        except Exception as e:
            print("Error:", e)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_pipeline("data/processed/input_real.json", "outputs/patches.json")
