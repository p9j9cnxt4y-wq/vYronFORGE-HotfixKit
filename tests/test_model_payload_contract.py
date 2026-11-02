"""Synthetic fixture for upstream Codex issue #41486; NOT a desktop integration test."""
import unittest

from vyronforge_hotfix.execution_integrity import (
    BoundaryIntegrityError, utf8_payload, verify_exact_bytes,
)


class ModelPayloadContractTests(unittest.TestCase):
    def test_literal_windows_path_roundtrip(self):
        literal = utf8_payload(r"Z:\AREA_01")
        self.assertEqual(verify_exact_bytes(literal, literal).status, "PASS")

    def test_markdown_escape_mutation_detected(self):
        source = utf8_payload(r"Z:\AREA_01")
        mutated = utf8_payload(r"Z:\AREA\_01")
        with self.assertRaises(BoundaryIntegrityError):
            verify_exact_bytes(source, mutated)

    def test_code_span_preserved(self):
        text = utf8_payload('`Z:\\AREA_01` and "ü"')
        self.assertEqual(verify_exact_bytes(text, text).status, "PASS")

    def test_upstream_not_claimed_as_reproduced(self):
        # This suite has no Codex Desktop composer access; it tests only bytes.
        self.assertNotEqual(utf8_payload(r"Z:\AREA_01"), utf8_payload(r"Z:\AREA\_01"))


if __name__ == "__main__":
    unittest.main()
