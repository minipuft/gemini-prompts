# Claude Prompts for Gemini CLI

Hot-reloadable prompt engineering with chains, gates, and symbolic syntax.

## Quick Start

Use symbolic syntax to execute prompts:

```
>>prompt_id                    # Execute single prompt
>>step1 --> >>step2            # Chain prompts sequentially
>>prompt @CAGEERF              # Apply methodology framework
>>prompt :: 'quality criteria' # Add inline validation gate
```

## Available MCP Tools

### prompt_engine
Execute prompts with frameworks, gates, and chains.

**Examples:**
- `prompt_engine(command: ">>analyze")` - Execute the analyze prompt
- `prompt_engine(command: ">>step1 --> >>step2")` - Chain execution
- `prompt_engine(chain_id: "chain-step1#1", user_response: "...")` - Resume chain

### resource_manager
CRUD operations for prompts, gates, and methodologies.

**Actions:** `create`, `update`, `delete`, `list`, `inspect`, `reload`

### system_control
Framework management, analytics, and status.

**Examples:**
- `system_control(action: "status")` - Show current state
- `system_control(action: "framework", operation: "list")` - List frameworks

## Chain Workflow

When executing chains, hooks will remind you of progress:
- `[Chain] Step 1/3 - call prompt_engine to continue`
- `[Gate] review - Respond: GATE_REVIEW: PASS|FAIL - <reason>`

## More Information

See the [documentation](https://github.com/minipuft/claude-prompts-mcp) for full details.
