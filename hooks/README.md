# Gemini Prompts Hooks

Hooks for Gemini CLI that provide syntax detection, chain tracking, gate enforcement, and context tracking.

## Why Hooks?

| Problem | Hook Solution |
|---------|---------------|
| Model ignores `>>analyze` syntax | `before-agent.py` detects and suggests MCP call |
| User forgets to continue chain | `after-tool.py` injects chain progress reminder |
| Gate review skipped | `after-tool.py` reminds: `GATE_REVIEW: PASS\|FAIL` |
| FAIL verdict executed anyway | `gate-enforce.py` blocks prompt_engine with deny decision |
| Ralph loop loses file context | `ralph-context-tracker.py` records edits/commands silently |

| Session state bloat | `pre-compact.py` cleans up before compression |

## Requirements

- **Gemini CLI v0.24.0+** — Earlier versions don't support `hooks.enabled`
- **Global hooks toggle** — Enable in `~/.gemini/settings.json`

## Setup

**Step 1: Enable hooks globally**

Create or edit `~/.gemini/settings.json`:

```json
{
  "hooks": {
    "enabled": true
  }
}
```

**Step 2: Install the extension**

```bash
# Clone or download gemini-prompts
git clone https://github.com/minipuft/gemini-prompts.git
cd gemini-prompts
git submodule update --init

# Symlink to extensions directory
ln -s "$(pwd)" ~/.gemini/extensions/gemini-prompts
```

## Architecture

```
hooks/
├── hooks.json                 # Gemini hooks config
├── before-agent.py            # BeforeAgent (syntax detection)
├── gate-enforce.py            # BeforeTool (gate verdict enforcement)
├── after-tool.py              # AfterTool:prompt_engine (chain/gate tracking)
├── ralph-context-tracker.py   # AfterTool:edit/write/bash (Ralph context)

├── pre-compact.py             # PreCompress (session cleanup)
├── stop.py                    # SessionEnd (graceful shutdown)
└── lib -> ../node_modules/claude-prompts/hooks/lib  # Shared utilities
```

**Shared utilities** (`lib/`) are symlinked to the `claude-prompts` npm package, providing `session_state`, `session_tracker`, `lesson_extractor`, `workspace`, and `cache_manager` modules.

## Hook Event Mapping

| Gemini Event | Claude Code Equivalent | Hook | Purpose |
|--------------|------------------------|------|---------|

| `BeforeAgent` | `UserPromptSubmit` | `before-agent.py` | Detect `>>prompt` syntax |
| `BeforeTool` | `PreToolUse` | `gate-enforce.py` | Block FAIL verdicts / missing gate responses |
| `AfterTool` | `PostToolUse` | `after-tool.py` | Track chain state, gate reminders |
| `AfterTool` | `PostToolUse` | `ralph-context-tracker.py` | Track file/command changes for Ralph |
| `PreCompress` | `PreCompact` | `pre-compact.py` | Preserve state across compression |
| `SessionEnd` | `Stop` | `stop.py` | Shell verification loop control |

## Configuration

Hooks are configured in `hooks/hooks.json`:

```json
{
  "hooks": {
    "BeforeTool": [{
      "matcher": "prompt_engine",
      "hooks": [{
        "name": "gate-enforce",
        "type": "command",
        "command": "python3 ${extensionPath}${/}hooks${/}gate-enforce.py"
      }]
    }],
    "AfterTool": [
      { "matcher": "prompt_engine", "hooks": [{ "...": "chain-tracker" }] },
      { "matcher": "write_file|replace|bash|task_tool", "hooks": [{ "...": "ralph-context-tracker" }] }
    ]
  }
}
```

**Dual AfterTool matchers**: Two separate matcher entries fire independently — `prompt_engine` for chain/gate tracking, `write_file|replace|bash|task_tool` for Ralph context tracking.

**Key differences from Claude Code:**

| Aspect | Gemini CLI | Claude Code |
|--------|------------|-------------|
| Path variable | `${extensionPath}` | `${CLAUDE_PLUGIN_ROOT}` |
| Path separator | `${/}` (cross-platform) | `/` |
| Timeout | milliseconds | seconds |
| Block decision | `{ "decision": "deny", "reason": "..." }` | `{ "hookSpecificOutput": { "permissionDecision": "deny" } }` |

## Known Gaps

| Claude Code Hook | Gemini Status | Impact |
|-----------------|---------------|--------|
| `subagent-gate-enforce` | No equivalent event | Delegated sub-agents can complete without satisfying gate criteria |

Gemini CLI does not expose a sub-agent completion event (`SubagentStop` equivalent). Sub-agents are still experimental in Gemini CLI. When the event is added upstream, port Claude's `subagent-gate-enforce.py` using the same I/O adaptation pattern as `gate-enforce.py`.

## Verifying Hooks Work

1. Start a Gemini session: `gemini`
2. Enable debug logging: `export GEMINI_HOOK_DEBUG=1`
3. Check `.gemini/hook-debug.log` for output
4. Test with: `>>diagnose :: 'security-review'`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "hooks.enabled" error | Upgrade: `npm i -g @google/gemini-cli@latest` |
| Hooks not firing | Check `~/.gemini/settings.json` has `"hooks": { "enabled": true }` |
| Hooks running twice | Using symlink? Don't add hooks to `settings.json` |
| Import errors | Verify `lib` symlink exists and points to `../node_modules/claude-prompts/hooks/lib` |

## Updating

The `lib/` utilities come from the `claude-prompts` npm package. To update:

```bash
npm update claude-prompts
```

This pulls the latest shared utilities without changing the Gemini-specific hook scripts.
