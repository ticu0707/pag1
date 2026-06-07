#!/usr/bin/env python3
"""
validate_agents.py — Static validator for .claude/agents/*.md files.

Usage:
    python scripts/validate_agents.py .claude/agents/
    python scripts/validate_agents.py .claude/agents/my-team-orchestrator.md

Checks: YAML frontmatter, required fields, model aliases, maxTurns type,
placeholder text, orchestrator patterns, tool over-granting.
Exit code 0 = all PASS, 1 = any FAIL.
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


VALID_MODEL_IDS = {
    "claude-opus-4-8",
    "claude-opus-4-7",
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-haiku-4-5",
    "claude-haiku-4-5-20251001",
}

VALID_EFFORT_VALUES = {"low", "medium", "high", "xhigh", "max"}

MODEL_ALIASES = {"sonnet", "opus", "haiku", "claude-sonnet", "claude-opus", "claude-haiku"}

ORCHESTRATOR_REQUIRED_PATTERNS = {
    "circuit_breaker": [
        r"circuit.breaker",
        r"retry once",
        r"second attempt",
        r"FAILED_",
        r"do not attempt.*third",
        r"not attempt.*third",
    ],
    "checkpoint": [
        r"## CHECKPOINT",
        r"checkpoint",
        r"400 token",
        r"compressed",
    ],
    "background_wait": [
        r"waiting for all agents",
        r"I am now waiting",
        r"do not proceed.*synthesis",
        r"EVERY.*launched agent",
        r"wait.*all.*complete",
    ],
    "security_summarize": [
        r"summarize.*own words",
        r"do not copy.paste.*raw",
        r"SECURITY ALERT",
        r"ABSOLUTE SECURITY",
        r"potentially compromised",
    ],
}

RESEARCHER_FORBIDDEN_TOOLS = {"Write", "Edit", "Bash"}
VALIDATOR_FORBIDDEN_TOOLS = {"Write", "Edit"}


def parse_frontmatter(content: str) -> tuple:
    """Returns (yaml_dict, body, error_message). error_message is None on success."""
    if not content.startswith("---"):
        return None, content, "File does not start with YAML frontmatter (---)"

    end = content.find("\n---", 3)
    if end == -1:
        return None, content, "YAML frontmatter not closed (missing closing ---)"

    yaml_str = content[3:end].strip()
    body = content[end + 4:].strip()

    try:
        data = yaml.safe_load(yaml_str)
        if not isinstance(data, dict):
            return None, body, "YAML frontmatter parsed but is not a mapping"
        return data, body, None
    except yaml.YAMLError as e:
        return None, body, f"YAML parse error: {e}"


def check_placeholders(text: str) -> list:
    """Find [BRACKET] placeholders likely not replaced (uppercase, 3+ chars)."""
    matches = re.findall(r'\[[A-Z][A-Z0-9_\s\-]{2,}\]', text)
    # Known false positives used as examples in templates
    false_positive_fragments = {"[LOG", "[WARNING", "[PARTIAL", "[CHECKPOINT"}
    return [m for m in matches if not any(fp in m for fp in false_positive_fragments)]


def is_orchestrator(name: str, description: str, tools: str) -> bool:
    if "orchestrator" in name.lower():
        return True
    if tools and "Agent(" in tools:
        return True
    if description and ("coordinate" in description.lower() or "orchestrat" in description.lower()):
        return True
    return False


def is_researcher(name: str, tools: str) -> bool:
    return "research" in name.lower() or (
        tools and ("WebSearch" in tools or "WebFetch" in tools)
    )


def is_validator(name: str) -> bool:
    return "validator" in name.lower() or "reviewer" in name.lower()


def parse_tools(tools_value) -> set:
    if not tools_value:
        return set()
    tools_str = str(tools_value)
    # Strip Agent(...) wrapper before splitting
    tools_str = re.sub(r'Agent\([^)]*\)', 'Agent', tools_str)
    return {t.strip() for t in re.split(r'[,\s]+', tools_str) if t.strip()}


def validate_file(path: Path) -> list:
    """Returns list of issues: [{"level": "FAIL"|"WARN", "code": str, "message": str}]"""
    issues = []

    def add(level: str, code: str, msg: str):
        issues.append({"level": level, "code": code, "message": msg})

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        add("FAIL", "READ_ERROR", f"Cannot read file: {e}")
        return issues

    frontmatter, body, parse_error = parse_frontmatter(content)

    if parse_error:
        add("FAIL", "YAML_PARSE", parse_error)
        return issues

    # Required fields
    for field in ("name", "description"):
        if field not in frontmatter or not frontmatter[field]:
            add("FAIL", "MISSING_REQUIRED_FIELD", f"Required field '{field}' is missing or empty")

    name = str(frontmatter.get("name", ""))
    description = str(frontmatter.get("description", ""))
    tools_raw = frontmatter.get("tools", "")
    tools_str = str(tools_raw)

    # Model ID validation
    model = str(frontmatter.get("model", "")).strip()
    if model:
        if model.lower() in MODEL_ALIASES:
            add("FAIL", "MODEL_ALIAS",
                f"model: '{model}' is an alias — use exact ID (e.g., claude-sonnet-4-6)")
        elif model not in VALID_MODEL_IDS:
            add("WARN", "MODEL_UNKNOWN",
                f"model: '{model}' not in known model list — verify it's a valid Anthropic model ID")

    # maxTurns type check
    max_turns = frontmatter.get("maxTurns")
    if max_turns is not None:
        if isinstance(max_turns, str):
            add("FAIL", "MAXTURNS_STRING",
                f"maxTurns: '{max_turns}' is a string — must be integer (remove quotes)")
        elif not isinstance(max_turns, int):
            add("FAIL", "MAXTURNS_INVALID",
                f"maxTurns: {max_turns!r} is not an integer")
    else:
        add("WARN", "MISSING_MAXTURNS",
            "maxTurns not set — agent has no cost ceiling (required per production hardening)")

    # Placeholder detection
    placeholders = check_placeholders(content)
    if placeholders:
        add("FAIL", "PLACEHOLDER",
            f"Unreplaced placeholders found: {placeholders[:5]}"
            + (" (and more)" if len(placeholders) > 5 else ""))

    # Naming conventions
    if name and "_" in name:
        add("WARN", "NAMING_UNDERSCORE",
            f"name: '{name}' uses underscore — use hyphens (kebab-case)")
    if name and len(name) > 30:
        add("WARN", "NAMING_TOO_LONG",
            f"name: '{name}' is {len(name)} chars — max 30 recommended")

    # Description quality
    if description:
        desc_lower = description.lower()
        if "do not invoke" not in desc_lower and "don't invoke" not in desc_lower:
            add("WARN", "DESCRIPTION_NO_EXCLUSION",
                "description missing 'Do NOT invoke for' exclusion case — may trigger incorrectly")
        if len(description) < 40:
            add("WARN", "DESCRIPTION_TOO_SHORT",
                "description is very short — may not trigger or exclude correctly")

    # effort field validation
    effort = frontmatter.get("effort")
    if effort is not None:
        if isinstance(effort, str):
            if effort.lower() not in VALID_EFFORT_VALUES:
                add("WARN", "EFFORT_INVALID_VALUE",
                    f"effort: '{effort}' not a valid value — expected: low, medium, high, xhigh (Opus 4.7/4.8), max (Opus 4.6+)")
        elif not isinstance(effort, (int, float)):
            add("WARN", "EFFORT_WRONG_TYPE",
                f"effort: {effort!r} should be a string value (low/medium/high/xhigh/max)")

    # background must be boolean
    bg = frontmatter.get("background")
    if bg is not None and isinstance(bg, str):
        add("FAIL", "BACKGROUND_STRING",
            f"background: '{bg}' is a string — must be boolean true/false (no quotes)")

    # Orchestrator-specific checks
    if is_orchestrator(name, description, tools_str):
        for pattern_name, regexes in ORCHESTRATOR_REQUIRED_PATTERNS.items():
            if not any(re.search(r, content, re.IGNORECASE) for r in regexes):
                add("WARN", f"ORCHESTRATOR_{pattern_name.upper()}_MISSING",
                    f"Orchestrator missing '{pattern_name}' pattern — see references/production-hardening.md")

        # background + explicit wait
        if "background: true" in content or "background:true" in content:
            wait_patterns = [r"waiting for all agents", r"I am now waiting", r"wait.*all.*complete"]
            if not any(re.search(p, content, re.IGNORECASE) for p in wait_patterns):
                add("WARN", "ORCHESTRATOR_BACKGROUND_NO_WAIT",
                    "Orchestrator uses background: true but missing explicit wait instruction before synthesis")

    # Tool over-granting
    granted = parse_tools(tools_raw)
    if is_researcher(name, tools_str) and granted:
        forbidden = granted & RESEARCHER_FORBIDDEN_TOOLS
        if forbidden:
            add("FAIL", "TOOL_OVERGRANT_RESEARCHER",
                f"Researcher has write/execute tools: {sorted(forbidden)} — researchers must NOT modify files")

    if is_validator(name) and granted:
        forbidden = granted & VALIDATOR_FORBIDDEN_TOOLS
        if forbidden:
            add("WARN", "TOOL_OVERGRANT_VALIDATOR",
                f"Validator has modification tools: {sorted(forbidden)} — validators should not modify files")

    return issues


def extract_agent_references(content: str) -> list:
    """Extract agent names from Agent(...) calls in tools field or system prompt body."""
    refs = []
    for match in re.finditer(r'Agent\(([^)]+)\)', content):
        for name in match.group(1).split(','):
            name = name.strip().strip('"\'')
            if not name or name.startswith('['):
                continue  # empty or template placeholder — skip
            refs.append(name)
    return refs


def validate_cross_references(directory: Path, results: dict) -> None:
    """Directory-level: Agent() references must point to existing .md files."""
    existing_stems = {f.stem for f in directory.glob("*.md")}
    for filename, issues in results.items():
        path = directory / filename
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for ref in extract_agent_references(content):
            if ref not in existing_stems:
                issues.append({
                    "level": "FAIL",
                    "code": "DEAD_AGENT_REFERENCE",
                    "message": (
                        f"Agent('{ref}') referenced but '{ref}.md' not found in directory "
                        "— dead reference silently fails at runtime"
                    ),
                })


def validate_directory(directory: Path) -> dict:
    results = {}
    md_files = sorted(directory.glob("*.md"))
    if not md_files:
        print(f"No .md files found in {directory}")
        return results
    for f in md_files:
        results[f.name] = validate_file(f)
    validate_cross_references(directory, results)
    return results


def print_report(results: dict) -> bool:
    """Print validation report. Returns True if all PASS (no FAIL items)."""
    total = len(results)
    pass_count = 0
    fail_count = 0

    print("\n" + "=" * 62)
    print("AGENT VALIDATION REPORT")
    print("=" * 62)

    for filename, issues in results.items():
        fails = [i for i in issues if i["level"] == "FAIL"]
        warns = [i for i in issues if i["level"] == "WARN"]

        if fails:
            status = "FAIL"
            fail_count += 1
        else:
            status = "PASS"
            pass_count += 1

        warn_suffix = f"  ({len(warns)} warning{'s' if len(warns) != 1 else ''})" if warns else ""
        print(f"\n[{status}] {filename}{warn_suffix}")

        for issue in issues:
            marker = "  ✗" if issue["level"] == "FAIL" else "  ⚠"
            print(f"{marker} [{issue['code']}] {issue['message']}")

    print("\n" + "-" * 62)
    print(f"Results: {pass_count}/{total} PASS  |  {fail_count} FAIL")

    if fail_count > 0:
        print("\nFix all FAIL items before Step 8 (delivery).")
    else:
        print("\nAll files pass validation. Proceed to Step 8.")
    print("=" * 62 + "\n")

    return fail_count == 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_agents.py <path-to-dir-or-file>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_file():
        results = {target.name: validate_file(target)}
    elif target.is_dir():
        results = validate_directory(target)
    else:
        print(f"ERROR: {target} does not exist or is not a file/directory")
        sys.exit(1)

    all_pass = print_report(results)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
