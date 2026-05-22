# Author: mmj
# DATE: 10.05.2026
TOOL_HINTS = {
    "CWE-601": """
Open redirect vulnerabilities are commonly fixed by:
- validating redirect targets
- rejecting URLs starting with //
- allowing only same-origin redirects
- normalizing malformed paths
""",

    "CWE-89": """
SQL injection vulnerabilities are commonly fixed by:
- parameterized queries
- prepared statements
- avoiding SQL string concatenation
""",

    "CWE-79": """
Cross-site scripting vulnerabilities are commonly fixed by:
- escaping HTML
- sanitizing user input
""",

    "CWE-787": """
Out-of-bounds write vulnerabilities are commonly fixed by:
- validating array bounds
- checking input length
- preventing buffer overflow
"""
}

DEFAULT_HINT = """
General security repair guidance:
- Identify user-controlled input.
- Identify dangerous sink.
- Apply minimal secure fix.
- Preserve functionality.
- Keep patch minimal.
"""


def get_tool_hint(info):
    cwe_ids = info.get("cwe_id", [])

    hints = []

    for cwe in cwe_ids:
        if cwe in TOOL_HINTS:
            hints.append(TOOL_HINTS[cwe])

    if not hints:
        hints.append(DEFAULT_HINT)

    return "\n".join(hints)