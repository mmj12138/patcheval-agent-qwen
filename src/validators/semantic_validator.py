# Author: mmj
# DATE: 22.05.2026
def validate_meaningful_patch(patch):
    removed = [
        line[1:].strip()
        for line in patch.splitlines()
        if line.startswith("-") and not line.startswith("---")
    ]

    added = [
        line[1:].strip()
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]

    if not removed or not added:
        return False, "Patch has no real code replacement."

    if set(removed) == set(added):
        return False, "Patch only replaces lines with identical content."

    if all(
        line.startswith("#") or line.startswith("//") or not line
        for line in added
    ):
        return False, "Patch only changes comments."

    suspicious = [
        "print(",
        "console.log",
        "TODO",
        "fix",
        "Exception occurred",
    ]

    for s in suspicious:
        if any(s in line for line in added):
            return False, f"Patch adds suspicious debugging or placeholder code: {s}"

    return True, "meaningful"