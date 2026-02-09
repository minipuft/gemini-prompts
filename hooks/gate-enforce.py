#!/usr/bin/env python3
"""
BeforeTool hook: Enforce gate verdicts on prompt_engine calls.

Blocks:
1. GATE_REVIEW: FAIL without retry attempt
2. Missing gate_verdict when resuming a chain that requires it

Gemini adaptation of Claude's gate-enforce.py — uses top-level
decision/reason instead of hookSpecificOutput.permissionDecision.
"""

import json
import re
import sys
from pathlib import Path

# Add shared lib to path (lib/ is symlinked to core/hooks/lib/)
sys.path.insert(0, str(Path(__file__).parent / "lib"))

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
    if gate_verdict:
        fail_match = re.search(r'GATE_REVIEW:\s*FAIL', gate_verdict, re.IGNORECASE)
        if fail_match:
            reason_match = re.search(r'FAIL\s*[-:]\s*(.+)', gate_verdict, re.IGNORECASE)
            reason = reason_match.group(1).strip()[:50] if reason_match else "unspecified"
            deny(f"Gate FAIL: {reason}. Improve and retry with PASS.")

    # Check 2: Resuming chain without required gate_verdict
    if chain_id and not gate_verdict:
        session_id = hook_input.get("session_id", "") or hook_input.get("sessionId", "")
        state = load_session_state(session_id) if session_id else None

        if state and state.get("pending_gate"):
            gate = state['pending_gate']
            deny(f"Gate pending: {gate}. Submit gate_verdict first.")

    # All checks passed — allow tool execution
    sys.exit(0)


if __name__ == "__main__":
    main()
