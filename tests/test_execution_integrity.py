"""Pure checks and real local synthetic subprocess checks (no shell/network)."""
import unittest
from pathlib import Path
from unittest import mock
from types import SimpleNamespace

from vyronforge_hotfix.execution_integrity import (
    BoundaryIntegrityError, LocalExecutionError, digest, run_local_python_file,
    utf8_payload, verify_exact_bytes,
)

FIXTURES = Path(__file__).with_name("fixtures")


class ExecutionIntegrityTests(unittest.TestCase):
    def test_exact_bytes_pass(self):
        sample = b"abc\n"
        r = verify_exact_bytes(sample, sample)
        self.assertEqual((r.status, r.expected_length), ("PASS", 4))
        self.assertEqual(r.expected_sha256, digest(sample))

    def test_crlf_mutation_fails(self):
        expected = b"x=1\ny=2\n"
        mutated = expected.replace(b"\n", b"\r\n")
        self.assertEqual(len(mutated) - len(expected), 2)
        with self.assertRaisesRegex(BoundaryIntegrityError, "BOUNDARY_BYTE_MUTATION"):
            verify_exact_bytes(expected, mutated)

    def test_literal_tab_and_true_tab_not_equal(self):
        with self.assertRaises(BoundaryIntegrityError):
            verify_exact_bytes(b"VSAFE\tVM110\n", b"VSAFE\\tVM110\n")

    def test_path_escape_mutation_rejected(self):
        with self.assertRaises(BoundaryIntegrityError):
            verify_exact_bytes(utf8_payload(r"Z:\AREA_01"), utf8_payload(r"Z:\AREA\_01"))

    def test_utf8_and_symbol_case(self):
        text = 'Grüße 漢字 & _ path=Z:\\AREA_01 "quoted"'
        self.assertEqual(utf8_payload(text).decode("utf-8"), text)

    def test_bad_text_types_rejected(self):
        with self.assertRaises(TypeError):
            digest("not bytes")
        with self.assertRaises(TypeError):
            utf8_payload(b"not string")

    def test_child_binary_echo_real_subprocess(self):
        payload = b"hello\r\nfoo\n" + utf8_payload("Grüße 漢字") + b"\x00\x09\\t"
        result = run_local_python_file(FIXTURES / "echo_bytes.py", stdin=payload)
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout_sha256, digest(payload))
        self.assertEqual(result.stdin_sha256, digest(payload))
        self.assertEqual(verify_exact_bytes(payload, result.stdout).status, "PASS")

    def test_shell_disabled_text_disabled(self):
        mock_result = SimpleNamespace(returncode=0, stdout=b"ok", stderr=b"")
        with mock.patch("vyronforge_hotfix.execution_integrity.subprocess.run", return_value=mock_result) as captured:
            result = run_local_python_file(FIXTURES / "echo_bytes.py", stdin=b"ok")
        self.assertEqual(result.stdout, b"ok")
        kwargs = captured.call_args.kwargs
        self.assertIs(kwargs["shell"], False)
        self.assertIs(kwargs["text"], False)
        self.assertEqual(kwargs["input"], b"ok")
        self.assertEqual(kwargs["check"], False)
        self.assertIsInstance(captured.call_args.args[0], list)

    def test_nonzero_exit_fails(self):
        with self.assertRaisesRegex(LocalExecutionError, "LOCAL_CHILD_NONZERO_EXIT"):
            run_local_python_file(FIXTURES / "guest_exit_failure.py")

    def test_script_missing_fails(self):
        with self.assertRaisesRegex(LocalExecutionError, "LOCAL_PYTHON_FILE_REQUIRED"):
            run_local_python_file(FIXTURES / "absent.py")

    def test_args_and_input_types_fail(self):
        with self.assertRaises(TypeError):
            run_local_python_file(FIXTURES / "echo_bytes.py", stdin="text")
        with self.assertRaises(TypeError):
            run_local_python_file(FIXTURES / "echo_bytes.py", args=(123,))
        with self.assertRaises(ValueError):
            run_local_python_file(FIXTURES / "echo_bytes.py", timeout_seconds=0)

    def test_timeout_fails_closed(self):
        with mock.patch("vyronforge_hotfix.execution_integrity.subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("python", 1)):
            with self.assertRaisesRegex(LocalExecutionError, "LOCAL_CHILD_TIMEOUT"):
                run_local_python_file(FIXTURES / "echo_bytes.py")

    def test_no_raw_stream_in_exception(self):
        with self.assertRaises(BoundaryIntegrityError) as err:
            verify_exact_bytes(b"redacted-A", b"redacted-B")
        self.assertNotIn("redacted", str(err.exception))


if __name__ == "__main__":
    unittest.main()
