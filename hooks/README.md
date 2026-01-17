# Gemini Prompts Hooks

Hooks for Gemini CLI that provide the same functionality as Claude Code hooks: syntax detection, chain tracking, and gate reminders.

## Why Hooks?

| Problem | Hook Solution |
|---------|---------------|
| Model ignores `>>analyze` syntax | `before-agent.py` detects and suggests MCP call |
| User forgets to continue chain | `after-tool.py` injects chain progress reminder |
| Gate review skipped | `after-tool.py` reminds: `GATE_REVIEW: PASS\|FAIL` |
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
├── hooks.json          # Gemini hooks config
├── before-agent.py     # BeforeAgent (syntax detection)
├── after-tool.py       # AfterTool (chain/gate tracking)
├── pre-compact.py      # PreCompress (session cleanup)
├── session-start.py    # SessionStart (dev sync)
├── stop.py             # SessionEnd (graceful shutdown)
└── lib -> ../core/hooks/lib   # Shared utilities (via submodule)
```

**Shared utilities** (`lib/`) are provided by the `core` submodule, which tracks the [claude-prompts-mcp](https://github.com/minipuft/claude-prompts-mcp) dist branch.

## Hook Event Mapping

| Gemini Event | Claude Code Equivalent | Purpose |
|--------------|------------------------|---------|
| `BeforeAgent` | `UserPromptSubmit` | Detect `>>prompt` syntax |
| `AfterTool` | `PostToolUse` | Track chain state, gate reminders |
| `PreCompress` | `PreCompact` | Clean session state |
| `SessionStart` | `SessionStart` | Dev sync |
| `SessionEnd` | `Stop` | Graceful shutdown |

## Configuration

Hooks are configured in `hooks/hooks.json`:

```json
{
  "hooks": {
    "BeforeAgent": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ${extensionPath}${/}hooks${/}before-agent.py",
        "timeout": 5000
      }]
    }],
    "AfterTool": [{
      "matcher": "prompt_engine",
      "hooks": [{
        "type": "command",
        "command": "python3 ${extensionPath}${/}hooks${/}after-tool.py",
        "timeout": 5000
      }]
    }]
  }
}
```

**Key differences from Claude Code:**

| Aspect | Gemini CLI | Claude Code |
|--------|------------|-------------|
| Path variable | `${extensionPath}` | `${CLAUDE_PLUGIN_ROOT}` |
| Path separator | `${/}` (cross-platform) | `/` |
| Timeout | milliseconds | seconds |

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
| Import errors | Verify `lib` symlink exists and points to `../core/hooks/lib` |

## Updating

The `lib/` utilities come from the `core` submodule. To update:

```bash
git submodule update --remote --merge
```

This pulls the latest shared utilities from claude-prompts-mcp without changing the Gemini-specific hook scripts.
