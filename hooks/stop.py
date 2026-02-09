#!/usr/bin/env python3
"""
SessionEnd hook: Shell verification for Ralph autonomous loops.

Wraps ralph-stop logic using the shared lib symlink to locate the
source hook. The lib/ symlink points to claude-prompts/hooks/lib/,
so the parent of that resolved path contains ralph-stop.py.

Output format is already Gemini-compatible (decision/block/reason at top level).
"""
import sys
import importlib.util
from pathlib import Path

# Resolve hooks directory from lib symlink target
# lib/ -> ../node_modules/claude-prompts/hooks/lib/ -> parent = hooks/
SHARED_LIB = Path(__file__).resolve().parent / "lib"
CORE_HOOKS_DIR = SHARED_LIB.resolve().parent

ralph_stop_path = CORE_HOOKS_DIR / "ralph-stop.py"

if not ralph_stop_path.exists():
    # Hook source not found — allow stop silently
    sys.exit(0)

spec = importlib.util.spec_from_file_location("ralph_stop", ralph_stop_path)
ralph_stop = importlib.util.module_from_spec(spec)
sys.modules["ralph_stop"] = ralph_stop
spec.loader.exec_module(ralph_stop)

if __name__ == "__main__":
    ralph_stop.main()
