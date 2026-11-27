"""The call shape hooks/before-agent.py tells the model to send to prompt_engine.

Prompt argument values belong in `inputs`; `options` carries execution hints only.
The hook imports cache_manager and session_state from the hooks/lib symlink, so
this test stubs both modules and needs no `npm ci` and starts no server.

Run: python3 -m unittest discover -s hooks/tests
"""

import importlib.util
import sys
import types
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "before-agent.py"


def load_hook():
    stubs = {
        "cache_manager": ["load_prompts_cache", "get_prompt_by_id", "match_prompts_to_intent", "get_chains_only"],
        "session_state": ["load_session_state", "format_chain_reminder"],
    }
    for module_name, names in stubs.items():
        module = types.ModuleType(module_name)
        for name in names:
            setattr(module, name, lambda *a, **k: None)
        sys.modules[module_name] = module
    spec = importlib.util.spec_from_file_location("before_agent_under_test", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FormatToolCall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.format_tool_call = staticmethod(load_hook().format_tool_call)

    def test_prompt_arguments_go_in_inputs(self):
        info = {"arguments": [{"name": "topic", "default": "caching"}, {"name": "depth"}]}
        call = self.format_tool_call("research", info)
        self.assertEqual(
            call,
            'prompt_engine(command:">>research", inputs:{"topic": "caching", "depth": "<depth>"})',
        )
        self.assertNotIn("options:", call)

    def test_chain_prompt_uses_inputs_too(self):
        info = {"is_chain": True, "chain_steps": 3, "arguments": [{"name": "feature"}]}
        call = self.format_tool_call("plan_then_build", info)
        self.assertEqual(call, 'prompt_engine(command:">>plan_then_build", inputs:{"feature": "<feature>"})')

    def test_prompt_without_arguments_sends_neither(self):
        call = self.format_tool_call("ping", {"arguments": []})
        self.assertEqual(call, 'prompt_engine(command:">>ping")')


if __name__ == "__main__":
    unittest.main()
