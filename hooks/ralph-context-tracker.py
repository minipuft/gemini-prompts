#!/usr/bin/env python3
"""
AfterTool hook: Track file changes and tool usage for Ralph loops.

Triggers after: write_file, replace, bash, task_tool (during active Ralph sessions)

Records:
1. File modifications (write_file/replace tools)
2. Command executions (bash tool)
3. Delegated sub-agent summaries (task_tool)

Gemini adaptation of Claude's ralph-context-tracker.py — uses Gemini
tool name conventions. No output (silent tracking).
"""

import json
import sys
from pathlib import Path

# Add shared lib to path (lib/ is symlinked to core/hooks/lib/)
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from session_tracker import get_session_tracker
from lesson_extractor import summarize_error
from workspace import get_runtime_state_dir


def parse_hook_input() -> dict:
    """Parse JSON input from Gemini hook system."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def get_active_ralph_session() -> str | None:
    """
    Get the currently active Ralph session ID.

    Checks for verify-active.json state file (source of truth for Ralph sessions).
    """
    dev_fallback = Path(__file__).parent.parent / "runtime-state"
    runtime_dir = get_runtime_state_dir(dev_fallback)
    state_file = runtime_dir / "verify-active.json"

    if not state_file.exists():
        return None

    try:
        state = json.loads(state_file.read_text())
        return state.get("sessionId")
    except (json.JSONDecodeError, IOError):
        return None


def extract_file_change_details(tool_input: dict, tool_name: str) -> dict | None:
    """Extract file change details from write_file/replace tool input."""
    if "replace" in tool_name:
        return {
            "file": tool_input.get("file_path", tool_input.get("filePath", "unknown")),
            "type": "modify",
            "details": f"Replace: {tool_input.get('old_string', tool_input.get('oldString', ''))[:50]}..."
        }
    elif "write_file" in tool_name:
        content = tool_input.get("content", "")
        return {
            "file": tool_input.get("file_path", tool_input.get("filePath", "unknown")),
            "type": "add",
            "details": f"Write: {len(content)} chars"
        }
    return None


def extract_bash_details(tool_input: dict, tool_response: str) -> dict | None:
    """Extract command execution details from bash tool."""
    command = tool_input.get("command", "")
    if not command:
        return None

    cmd_summary = command[:100] + "..." if len(command) > 100 else command

    verification_indicators = ["test", "npm run", "yarn", "pytest", "cargo test", "go test", "make"]
    is_verification = any(ind in command.lower() for ind in verification_indicators)

    return {
        "command": cmd_summary,
        "is_verification": is_verification,
        "output_summary": summarize_error(tool_response) if tool_response else None
    }


def extract_task_details(tool_input: dict, tool_response: str) -> dict:
    """Extract delegated sub-agent summary from task_tool payload."""
    agent_type = (
        tool_input.get("subagent_type")
        or tool_input.get("agent_type")
        or tool_input.get("subagentType")
        or "unknown"
    )
    response_text = summarize_error(tool_response) if tool_response else "No response captured."
    if len(response_text) > 500:
        response_text = response_text[:500] + "..."

    return {
        "agent_type": str(agent_type),
        "summary": response_text,
    }


def main():
    hook_input = parse_hook_input()

    tool_name = (
        hook_input.get("tool_name", "")
        or hook_input.get("toolName", "")
        or hook_input.get("name", "")
    )

    # Only track during active Ralph sessions
    ralph_session = get_active_ralph_session()
    if not ralph_session:
        sys.exit(0)

    tool_input = (
        hook_input.get("tool_input", {})
        or hook_input.get("toolInput", {})
        or {}
    )
    tool_response = (
        hook_input.get("tool_response", {})
        or hook_input.get("toolResponse", {})
        or hook_input.get("result", {})
    )

    # Convert response to string if needed
    if isinstance(tool_response, dict):
        content = tool_response.get("content", "")
        if isinstance(content, list):
            tool_response = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        else:
            tool_response = str(content)
    else:
        tool_response = str(tool_response)

    tracker = get_session_tracker(ralph_session)

    # Track file changes
    if "replace" in tool_name or "write_file" in tool_name:
        change = extract_file_change_details(tool_input, tool_name)
        if change:
            tracker.record_file_change(
                file_path=change["file"],
                change_type=change["type"],
                details=change["details"]
            )

    # Track bash commands
    if "bash" in tool_name.lower():
        bash_details = extract_bash_details(tool_input, tool_response)
        if bash_details and bash_details["is_verification"]:
            pass  # Verification output captured by ralph-stop.py

    # Track delegated sub-agent outputs
    if "task_tool" in tool_name or "task" in tool_name.lower():
        task_details = extract_task_details(tool_input, tool_response)
        tracker.record_subagent_result(
            agent_type=task_details["agent_type"],
            summary=task_details["summary"],
        )
        tracker.append_loop_memory(
            f"Sub-agent `{task_details['agent_type']}` completed: {task_details['summary']}"
        )

    # No output needed — silent tracking
    sys.exit(0)


if __name__ == "__main__":
    main()
