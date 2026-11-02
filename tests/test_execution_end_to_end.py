"""Execute real local guest .py files, wrap stdout as QGA-shaped JSON, parse.

Negative fixtures reproduce the observed failure modes; never contact real hosts.
"""
from pathlib import Path
import unittest

from vyronforge_hotfix.execution_integrity import run_local_python_file
from vyronforge_hotfix.guest_protocol import (
    GuestProtocolError, decode_legacy_tab_record,
    make_synthetic_qga_reply, parse_synthetic_qga_reply,
)

FIXTURES = Path(__file__).with_name("fixtures")


class EndToEndTests(unittest.TestCase):
    def test_real_guest_source_to_qga_to_parser(self):
        process = run_local_python_file(FIXTURES / "guest_valid.py")
        self.assertEqual(process.exit_code, 0)
        self.assertTrue(process.stdout)
        parsed = parse_synthetic_qga_reply(make_synthetic_qga_reply(process.stdout))
        self.assertEqual(len(parsed), 3)
        self.assertEqual([x["target"] for x in parsed], ["VM110", "VM100", "VM170"])

    def test_negative_missing_main_exits_zero_but_parser_fails(self):
        process = run_local_python_file(FIXTURES / "guest_missing_main.py")
        self.assertEqual(process.exit_code, 0)  # Reproduces false process-PASS.
        self.assertEqual(process.stdout, b"")
        with self.assertRaisesRegex(GuestProtocolError, "EMPTY_OR_OVERSIZED_STDOUT"):
            parse_synthetic_qga_reply(make_synthetic_qga_reply(process.stdout))

    def test_negative_literal_backslash_t_fails(self):
        process = run_local_python_file(FIXTURES / "guest_literal_tab.py")
        self.assertIn(b"\\t", process.stdout)
        self.assertNotIn(b"\t", process.stdout)
        with self.assertRaisesRegex(GuestProtocolError, "BAD_LEGACY_FIELD_DELIMITER"):
            decode_legacy_tab_record(process.stdout)

    def test_fixed_real_tab_passes(self):
        process = run_local_python_file(FIXTURES / "guest_real_tab.py")
        self.assertIn(b"\t", process.stdout)
        self.assertEqual(decode_legacy_tab_record(process.stdout)[0], "VM110")

    def test_malformed_guest_payload_does_not_promote_process_success(self):
        process = run_local_python_file(FIXTURES / "guest_literal_tab.py")
        self.assertEqual(process.exit_code, 0)
        with self.assertRaises(GuestProtocolError):
            parse_synthetic_qga_reply(make_synthetic_qga_reply(process.stdout))


if __name__ == "__main__":
    unittest.main()
