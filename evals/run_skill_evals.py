#!/usr/bin/env python3
"""Validate or execute the GitHub Project Publisher behavioral eval corpus."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = Path(__file__).with_name("cases.jsonl")
SCHEMA_PATH = Path(__file__).with_name("result.schema.json")
REQUIRED_TAGS = {
    "direct-trigger", "implicit-trigger", "negative-trigger", "incomplete-input",
    "card", "binary", "free-form", "no-question", "host-permission", "blocker",
}
ROUTES = {
    "no-question", "binary-confirmation", "structured-card", "free-form",
    "host-permission", "supported-fallback", "blocker-stop", "not-applicable",
}
EXPECTED_KEYS = {
    "should_use_skill", "route", "must_call_request_user_input", "must_stop_before_mutation",
}


def load_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    seen: set[str] = set()
    tags: set[str] = set()
    for number, line in enumerate(CASES_PATH.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"case line {number} is not valid JSON") from exc
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError(f"case line {number} has a missing or duplicate id")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            raise ValueError(f"case {case_id} has no prompt")
        case_tags = case.get("tags")
        if not isinstance(case_tags, list) or not all(isinstance(tag, str) for tag in case_tags):
            raise ValueError(f"case {case_id} has invalid tags")
        expected = case.get("expected")
        if not isinstance(expected, dict) or set(expected) != EXPECTED_KEYS:
            raise ValueError(f"case {case_id} has an invalid expected result")
        if expected.get("route") not in ROUTES:
            raise ValueError(f"case {case_id} has an unsupported route")
        if not all(isinstance(expected.get(key), bool) for key in EXPECTED_KEYS - {"route"}):
            raise ValueError(f"case {case_id} has non-boolean expectations")
        seen.add(case_id)
        tags.update(case_tags)
        cases.append(case)
    missing_tags = sorted(REQUIRED_TAGS - tags)
    if missing_tags:
        raise ValueError(f"eval corpus is missing required coverage tags: {', '.join(missing_tags)}")
    return cases


def grade(case: dict[str, object], result: dict[str, object]) -> list[str]:
    failures: list[str] = []
    if result.get("case_id") != case["id"]:
        failures.append("case_id")
    expected = case["expected"]
    assert isinstance(expected, dict)
    for key, value in expected.items():
        if result.get(key) != value:
            failures.append(key)
    return failures


def execute_case(codex: str, case: dict[str, object], output: Path) -> None:
    skill_path = ROOT / "github-project-publisher" / "SKILL.md"
    prompt = (
        f"Read and apply the skill at {skill_path}. This is a read-only policy evaluation: "
        "do not execute Git, GitHub, filesystem mutation, or network operations. Decide how the "
        "skill must route the interaction in the scenario below. Set must_call_request_user_input "
        "to true only when that exact structured-input tool is available in the scenario and the "
        "semantic card test passes. Return only the requested schema.\n\n"
        f"Case ID: {case['id']}\nScenario: {case['prompt']}"
    )
    proc = subprocess.run(
        [codex, "exec", "--output-schema", str(SCHEMA_PATH), "-o", str(output), prompt],
        cwd=ROOT,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Codex eval failed for {case['id']} with exit code {proc.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run every case through codex exec")
    parser.add_argument("--codex", help="Path to the Codex CLI executable")
    parser.add_argument("--artifacts", type=Path, default=Path(__file__).with_name("artifacts"))
    args = parser.parse_args()
    try:
        cases = load_cases()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Behavior eval corpus: {len(cases)} case(s), required coverage present")
    if not args.execute:
        return 0

    codex = args.codex or shutil.which("codex")
    if not codex:
        print("error: Codex CLI was not found", file=sys.stderr)
        return 2
    args.artifacts.mkdir(parents=True, exist_ok=True)
    failed = 0
    for case in cases:
        output = args.artifacts / f"{case['id']}.json"
        try:
            execute_case(codex, case, output)
            result = json.loads(output.read_text(encoding="utf-8"))
            mismatches = grade(case, result)
        except (OSError, RuntimeError, json.JSONDecodeError) as exc:
            print(f"[ERROR] {case['id']}: {exc}")
            failed += 1
            continue
        if mismatches:
            print(f"[FAIL] {case['id']}: {', '.join(mismatches)}")
            failed += 1
        else:
            print(f"[PASS] {case['id']}")
    print(f"Behavior eval result: {len(cases) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
