"""Deterministic checks of the temporary-session transport, not model quality."""
from pathlib import Path
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from asset_core.appserver import AppServer, envelope_schema


class TemporarySessionTests(unittest.TestCase):
    def run_client(self, mode, **options):
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "sample-skill" / "SKILL.md"
            skill.parent.mkdir()
            skill.write_text("---\nname: sample-skill\ndescription: test\n---\n", encoding="utf-8")
            client = AppServer([sys.executable, "-u", str(ROOT / "tests" / "fixtures" / "fake_appserver.py"), mode])
            try:
                return client.run(skill, {"artifact_dir": directory}, envelope_schema({"type": "object"}), directory, **options)
            finally:
                client.close()

    def test_only_current_thread_and_turn_supply_result(self):
        result, thread_id = self.run_client("normal")
        self.assertEqual(result["result"], {"proof": "expected"})
        self.assertEqual(thread_id, "temp-thread")

    def test_persistent_dispatcher_fallback_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "ephemeral"):
            self.run_client("persistent")

    def test_timeout_terminates_the_attempt(self):
        with self.assertRaises(TimeoutError):
            self.run_client("hang", timeout=0.01)

    def test_cancel_does_not_report_a_success(self):
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(InterruptedError):
            self.run_client("hang", cancel=cancel)


if __name__ == "__main__":
    unittest.main()
