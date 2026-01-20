# gemini-prompts

Gemini CLI extension for the [claude-prompts](https://github.com/minipuft/claude-prompts-mcp) MCP server. Full hook support including `>>prompt` syntax detection, chain tracking, and gate reminders.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

## Why This Extension

| Problem | Solution | Result |
|---------|----------|--------|
| Model ignores `>>analyze` syntax | BeforeAgent hook detects and suggests MCP call | Syntax works like Claude Code |
| Chain step forgotten | AfterTool hook injects progress reminder | `[Chain] Step 2/5 - continue` appears |
| Gate review skipped | AfterTool hook reminds response format | `GATE_REVIEW: PASS\|FAIL` prompt appears |
| Session state bloat | PreCompress hook cleans up | Fresh context after compaction |

## Quick Start

```bash
# Enable hooks globally (required once)
echo '{"hooks": {"enabled": true}}' > ~/.gemini/settings.json

# Install extension
gemini extensions install https://github.com/minipuft/gemini-prompts
```

Restart Gemini CLI. Test with:

```text
>>diagnose scope:'auth' focus:'security'
```

You should see the model call `prompt_engine` with the correct syntax.

## Features

- **Syntax Detection** — `>>prompt` triggers MCP call suggestion via BeforeAgent hook
- **Chain Tracking** — Shows `Step 2/4` progress after each prompt_engine call
- **Gate Reminders** — Injects `GATE_REVIEW: PASS|FAIL` format when gates are pending
- **State Preservation** — Session state survives compression
- **Auto-cleanup** — Clears state on session end
- **Bundled MCP Server** — Includes claude-prompts via npm dependency

## Hooks

| Gemini Event | Claude Code Equivalent | Purpose |
|--------------|------------------------|---------|
| `BeforeAgent` | `UserPromptSubmit` | Detect `>>prompt` syntax |
| `AfterTool` | `PostToolUse` | Chain/gate tracking |
| `PreCompress` | `PreCompact` | Session cleanup |
| `SessionStart` | `SessionStart` | Initialization |
| `SessionEnd` | `Stop` | Graceful shutdown |

Unlike OpenCode, Gemini CLI has full hook parity with Claude Code.

## Configuration

The extension auto-registers the MCP server. Manual override in `gemini-extension.json`:

```json
{
  "mcpServers": {
    "gemini-prompts": {
      "command": "npx",
      "args": ["claude-prompts", "--transport=stdio"],
      "env": {
        "MCP_WORKSPACE": "${extensionPath}${/}node_modules${/}claude-prompts"
      }
    }
  }
}
```

## Development

```bash
git clone https://github.com/minipuft/gemini-prompts
cd gemini-prompts
git submodule update --init
npm install

# Link to extensions directory
ln -s "$(pwd)" ~/.gemini/extensions/gemini-prompts
```

See [hooks/README.md](hooks/README.md) for hook development details.

## Related Projects

| Project | Description |
|---------|-------------|
| [claude-prompts-mcp](https://github.com/minipuft/claude-prompts-mcp) | Core MCP server with chains, gates, frameworks |
| [opencode-prompts](https://github.com/minipuft/opencode-prompts) | OpenCode plugin (limited hooks) |
| [minipuft-plugins](https://github.com/minipuft/minipuft-plugins) | Claude Code plugin marketplace |

## License

MIT
