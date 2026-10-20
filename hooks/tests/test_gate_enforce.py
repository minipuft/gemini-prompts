"""Drive hooks/gate-enforce.py the way Gemini CLI does: JSON on stdin, decision on stdout.

Needs `npm ci` first: the hook imports session_state through the hooks/lib symlink
into node_modules/claude-prompts.

Run: python3 -m unittest discover -s hooks/tests
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "gate-enforce.py"


def run_hook(tool_input: dict) -> dict:
    payload = {"tool_name": "prompt_engine", "tool_input": tool_input}
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class StructuredVerdict(unittest.TestCase):
    def test_fail_denies_with_rationale(self):
        out = run_hook({"gate_verdict": {"overall": "FAIL", "rationale": "missing tests"}})
        self.assertEqual(out["decision"], "deny")
        self.assertIn("Gate FAIL: missing tests", out["reason"])

    def test_fail_is_case_insensitive(self):
        out = run_hook({"gate_verdict": {"overall": "fail", "rationale": "x"}})
        self.assertEqual(out["decision"], "deny")

    def test_fail_without_rationale_is_unspecified(self):
        out = run_hook({"gate_verdict": {"overall": "FAIL"}})
        self.assertEqual(out["decision"], "deny")
        self.assertIn("unspecified", out["reason"])

    def test_rationale_is_truncated_to_50_characters(self):
        out = run_hook({"gate_verdict": {"overall": "FAIL", "rationale": "a" * 80}})
        self.assertIn("a" * 50 + ".", out["reason"])
        self.assertNotIn("a" * 51, out["reason"])

    def test_pass_allows(self):
        out = run_hook({"gate_verdict": {"overall": "PASS", "rationale": "all criteria met"}})
        self.assertEqual(out, {"decision": "allow"})

    def test_object_without_overall_does_not_crash_or_deny(self):
        for verdict in ({"rationale": "no overall"}, {"overall": None}, {"overall": 3}):
            with self.subTest(verdict=verdict):
                out = run_hook({"gate_verdict": verdict})
                self.assertEqual(out, {"decision": "allow"})


class LegacyStringVerdict(unittest.TestCase):
    def test_fail_denies_with_reason(self):
        out = run_hook({"gate_verdict": "GATE_REVIEW: FAIL - bad code"})
        self.assertEqual(out["decision"], "deny")
        self.assertIn("Gate FAIL: bad code", out["reason"])

    def test_pass_allows(self):
        out = run_hook({"gate_verdict": "GATE_REVIEW: PASS - looks good"})
        self.assertEqual(out, {"decision": "allow"})


if __name__ == "__main__":
    unittest.main()
