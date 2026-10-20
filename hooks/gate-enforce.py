#!/usr/bin/env python3
"""
BeforeTool hook: Enforce gate verdicts on prompt_engine calls.

Blocks:
1. A FAIL gate_verdict without retry attempt (structured `overall: FAIL`, or
   the legacy `GATE_REVIEW: FAIL` string)
2. Missing gate_verdict when resuming a chain that requires it

Gemini adaptation of Claude's gate-enforce.py — uses top-level
decision/reason instead of hookSpecificOutput.permissionDecision.
"""

import json
import re
import sys
import os
from pathlib import Path

# Add shared lib to path (lib/ is symlinked to core/hooks/lib/)
sys.path.insert(0, str(Path(__file__).parent / "lib"))

# Default workspace root to extension root, without overriding user config
os.environ.setdefault("MCP_WORKSPACE", str(Path(__file__).resolve().parents[1]))

from session_state import load_session_state


def parse_hook_input() -> dict:
    """Parse JSON input from Gemini hook system."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def deny(reason: str) -> None:
    """Output a Gemini-format deny decision and exit."""
    print(json.dumps({"decision": "deny", "reason": reason}))
    sys.exit(0)


def read_fail_verdict(gate_verdict) -> tuple[bool, str]:
    """Return (is_fail, reason) for either gate_verdict shape.

    Engines from 6.0 send a structured object ({"overall": "PASS"|"FAIL",
    "rationale": "..."}); older engines send "GATE_REVIEW: FAIL - reason".
    A value of any other shape, or an object without a string `overall`,
    is not a FAIL.
    """
    if isinstance(gate_verdict, dict):
        overall = gate_verdict.get("overall")
        if not isinstance(overall, str) or overall.strip().upper() != "FAIL":
            return False, ""
        rationale = gate_verdict.get("rationale")
        reason = rationale.strip()[:50] if isinstance(rationale, str) else ""
        return True, reason or "unspecified"

    if isinstance(gate_verdict, str):
        if not re.search(r'GATE_REVIEW:\s*FAIL', gate_verdict, re.IGNORECASE):
            return False, ""
        reason_match = re.search(r'FAIL\s*[-:]\s*(.+)', gate_verdict, re.IGNORECASE)
        return True, reason_match.group(1).strip()[:50] if reason_match else "unspecified"

    return False, ""


def main():
    hook_input = parse_hook_input()

    tool_name = (
        hook_input.get("tool_name", "")
        or hook_input.get("toolName", "")
        or hook_input.get("name", "")
    )

    # Only process prompt_engine calls
    if "prompt_engine" not in tool_name:
        sys.exit(0)

    tool_input = (
        hook_input.get("tool_input", {})
        or hook_input.get("toolInput", {})
        or {}
    )

    # Extract parameters
    chain_id = tool_input.get("chain_id", "")
    gate_verdict = tool_input.get("gate_verdict", "")

    # Check 1: FAIL verdict should trigger retry guidance
    failed, reason = read_fail_verdict(gate_verdict)
    if failed:
        deny(f"Gate FAIL: {reason}. Improve and retry with PASS.")

    # Check 2: Resuming chain without required gate_verdict
    if chain_id and not gate_verdict:
        session_id = hook_input.get("session_id", "") or hook_input.get("sessionId", "")
        state = load_session_state(session_id) if session_id else None

        if state and state.get("pending_gate"):
            gate = state['pending_gate']
            deny(f"Gate pending: {gate}. Submit gate_verdict first.")

    # All checks passed — allow tool execution
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)


if __name__ == "__main__":
    main()
