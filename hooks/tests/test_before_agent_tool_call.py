"""The call shape hooks/before-agent.py tells the model to send to prompt_engine.

Prompt argument values are written inline in the command string
(`>>id name:"value" other:"value"`), the form every released server parses for a prompt
and for a chain's first step. The call carries no `options` and no `inputs`.
The hook imports cache_manager and session_state from the hooks/lib symlink, so
this test stubs both modules and needs no `npm ci` and starts no server.

Run: python3 -m unittest discover -s hooks/tests
"""

import importlib.util
import json
import re
import sys
import types
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "before-agent.py"

# The server's `name:"value"` pair grammar (argument-parser.ts, KEY_VALUE_PAIR_SOURCE) and
# its unescape of quoted text (parseQuotedValue in jsonUtils.ts), ported so a test can read an
# emitted command the way the server does and compare the values it recovers.
PAIR = re.compile(r"""([\w-]+)\s*[=:]\s*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'|([^\s"']+(?:\s+(?![\w-]+\s*[=:])[^\s"']*)*))""")
ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}


def unescape_quoted(raw):
    def decode(match):
        escape = match.group(1)
        if escape.startswith("u") and len(escape) == 5:
            return chr(int(escape[1:], 16))
        return ESCAPES.get(escape, escape)

    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", decode, raw, flags=re.S)


def read_command(call):
    """Return (command string, {name: value}) the way a tool call and the server read `call`."""
    match = re.fullmatch(r'prompt_engine\(command:(".*")\)', call, flags=re.S)
    if match is None:
        raise AssertionError(f"not a command-only prompt_engine call: {call}")
    command = json.loads(match.group(1))
    head, _, rest = command.partition(" ")
    values = {pair.group(1): unescape_quoted(pair.group(2)) for pair in PAIR.finditer(rest)}
    return head, values


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

    def assert_inline_only(self, call):
        self.assertNotIn("options:", call)
        self.assertNotIn("inputs:", call)
        read_command(call)

    def test_exact_emitted_strings(self):
        # (arguments, exact call). Each row is one shape the server must parse.
        cases = {
            "default and placeholder": (
                "research",
                [{"name": "topic", "default": "caching"}, {"name": "depth"}],
                r'prompt_engine(command:">>research topic:\"caching\" depth:\"<depth>\"")',
            ),
            "value with spaces": (
                "research",
                [{"name": "topic", "default": "api rate limits"}],
                r'prompt_engine(command:">>research topic:\"api rate limits\"")',
            ),
            "value with a colon": (
                "plan",
                [{"name": "feature", "default": "Two modes: standalone, embedded"}],
                r'prompt_engine(command:">>plan feature:\"Two modes: standalone, embedded\"")',
            ),
            "value with a double quote": (
                "plan",
                [{"name": "feature", "default": 'say "hi"'}],
                r'prompt_engine(command:">>plan feature:\"say \\\"hi\\\"\"")',
            ),
            "value with a backslash": (
                "scan",
                [{"name": "path", "default": "C:\\Users\\dev"}],
                r'prompt_engine(command:">>scan path:\"C:\\\\Users\\\\dev\"")',
            ),
            "value with a line break": (
                "scan",
                [{"name": "text", "default": "a\nb"}],
                r'prompt_engine(command:">>scan text:\"a\\nb\"")',
            ),
            "value with an apostrophe": (
                "scan",
                [{"name": "note", "default": "it's fine"}],
                r"""prompt_engine(command:">>scan note:\"it's fine\"")""",
            ),
            "chain prompt": (
                "plan_then_build",
                [{"name": "feature"}],
                r'prompt_engine(command:">>plan_then_build feature:\"<feature>\"")',
            ),
            "no arguments": ("ping", [], 'prompt_engine(command:">>ping")'),
        }
        for label, (prompt_id, arguments, expected) in cases.items():
            with self.subTest(label):
                call = self.format_tool_call(prompt_id, {"arguments": arguments})
                self.assertEqual(call, expected)
                self.assert_inline_only(call)

    def test_emitted_command_reads_back_as_the_same_values(self):
        values = {
            "plain": "caching",
            "spaces": "api rate limits",
            "colon": "Two modes: (1) standalone, (2) embedded /dashboard + SSE",
            "double quote": 'say "hi" twice',
            "backslash": "C:\\Users\\dev",
            "line break": "a\nb\tc",
            "apostrophe": "it's fine",
            "operators": "a --> b :: c",
        }
        arguments = [{"name": name.replace(" ", "_"), "default": value} for name, value in values.items()]
        call = self.format_tool_call("research", {"arguments": arguments})
        head, read = read_command(call)
        self.assertEqual(head, ">>research")
        self.assertEqual(read, {name.replace(" ", "_"): value for name, value in values.items()})

    def test_placeholder_reads_back_as_the_name_in_angle_brackets(self):
        _, read = read_command(self.format_tool_call("research", {"arguments": [{"name": "depth"}]}))
        self.assertEqual(read, {"depth": "<depth>"})

    def test_chain_prompt_uses_the_same_inline_form(self):
        info = {"is_chain": True, "chain_steps": 3, "arguments": [{"name": "feature"}]}
        call = self.format_tool_call("plan_then_build", info)
        self.assertEqual(read_command(call), (">>plan_then_build", {"feature": "<feature>"}))

    def test_prompt_without_arguments_emits_just_the_command(self):
        for info in ({"arguments": []}, {}):
            with self.subTest(info=info):
                self.assertEqual(self.format_tool_call("ping", info), 'prompt_engine(command:">>ping")')

    def test_control_the_old_shapes_fail_the_inline_assertions(self):
        # A probe that never fails proves nothing: the `options` shape (main) and the `inputs`
        # shape (the previous commit on this branch) must both be rejected by what passes above.
        old_shapes = {
            "options": 'prompt_engine(command:">>research", options:{"topic": "caching", "depth": "<depth>"})',
            "inputs": 'prompt_engine(command:">>research", inputs:{"topic": "caching", "depth": "<depth>"})',
        }
        for label, call in old_shapes.items():
            with self.subTest(label):
                with self.assertRaises(AssertionError):
                    self.assert_inline_only(call)
                with self.assertRaises(AssertionError):
                    read_command(call)


if __name__ == "__main__":
    unittest.main()
