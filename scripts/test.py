# Author: mmj
# DATE: 22.05.2026

import json

if __name__ == "__main__":
    with open("../outputs/basic_7b_patches.json") as f:

        basic = json.load(f)

    with open("../outputs/feedback_7b_patches.json") as f:

        feedback = json.load(f)

    changed = []

    for b, f in zip(basic, feedback):

        if b["fix_patch"] != f["fix_patch"]:

            changed.append(b["cve"])

    print("changed:", len(changed))

    print(changed[:20])
