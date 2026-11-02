"""Guest protocol validation, including malformed and unknown output."""
import base64
import json
import unittest

from vyronforge_hotfix.guest_protocol import (
    GuestProtocolError, decode_guest_records, decode_legacy_tab_record,
    encode_guest_records, make_synthetic_qga_reply, parse_synthetic_qga_reply,
)

ROWS = [{"target": "VM110", "state": "OK", "detail_code": "SYNTHETIC_ONLY"}]


class GuestProtocolTests(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(decode_guest_records(encode_guest_records(ROWS)), ROWS)

    def test_qga_round_trip(self):
        response = make_synthetic_qga_reply(encode_guest_records(ROWS))
        self.assertEqual(parse_synthetic_qga_reply(response), ROWS)

    def test_empty_output_denied_even_exit_zero(self):
        with self.assertRaisesRegex(GuestProtocolError, "EMPTY_OR_OVERSIZED_STDOUT"):
            parse_synthetic_qga_reply(make_synthetic_qga_reply(b""))

    def test_literal_tabs_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "BAD_LEGACY_FIELD_DELIMITER"):
            decode_legacy_tab_record(b"VSAFE\\tVM110\\tOK\\tSYNTHETIC_ONLY\n")

    def test_actual_tab_accepted(self):
        self.assertEqual(decode_legacy_tab_record(b"VSAFE\tVM110\tOK\tSYNTHETIC_ONLY\n"),
                         ("VM110", "OK", "SYNTHETIC_ONLY"))

    def test_legacy_crlf_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "BAD_LEGACY_LINE_ENDING"):
            decode_legacy_tab_record(b"VSAFE\tVM110\tOK\tSYNTHETIC_ONLY\r\n")

    def test_qga_nonzero_exit_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "GUEST_PROCESS_NOT_SUCCESSFUL"):
            parse_synthetic_qga_reply(make_synthetic_qga_reply(encode_guest_records(ROWS), exit_code=2))

    def test_qga_process_not_exited_denied(self):
        r = make_synthetic_qga_reply(encode_guest_records(ROWS))
        r["return"]["exited"] = False
        with self.assertRaises(GuestProtocolError):
            parse_synthetic_qga_reply(r)

    def test_qga_invalid_base64_denied(self):
        r = make_synthetic_qga_reply(encode_guest_records(ROWS))
        r["return"]["out-data"] = "#$%"
        with self.assertRaisesRegex(GuestProtocolError, "INVALID_QGA_BASE64"):
            parse_synthetic_qga_reply(r)

    def test_qga_missing_field_denied(self):
        r = make_synthetic_qga_reply(encode_guest_records(ROWS))
        del r["return"]["exitcode"]
        with self.assertRaisesRegex(GuestProtocolError, "QGA_RESULT_SCHEMA_MISMATCH"):
            parse_synthetic_qga_reply(r)

    def test_qga_error_reply_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "QGA_REPLY_SCHEMA_MISMATCH"):
            parse_synthetic_qga_reply({"error": {"desc": "unknown"}})

    def test_record_count_mismatch_denied(self):
        p = json.loads(encode_guest_records(ROWS))
        p["record_count"] = 0
        with self.assertRaisesRegex(GuestProtocolError, "RECORD_COUNT_MISMATCH"):
            decode_guest_records(json.dumps(p).encode("utf-8"))

    def test_incomplete_marker_denied(self):
        p = json.loads(encode_guest_records(ROWS))
        p["completed"] = False
        with self.assertRaisesRegex(GuestProtocolError, "GUEST_COMPLETION_NOT_PROVEN"):
            decode_guest_records(json.dumps(p).encode("utf-8"))

    def test_unexpected_field_denied(self):
        p = json.loads(encode_guest_records(ROWS))
        p["records"][0]["payload"] = "unrecognized"
        with self.assertRaisesRegex(GuestProtocolError, "RECORD_SCHEMA_MISMATCH"):
            decode_guest_records(json.dumps(p).encode("utf-8"))

    def test_non_utf8_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "NON_JSON_GUEST_OUTPUT"):
            decode_guest_records(b"\xff")

    def test_non_json_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "NON_JSON_GUEST_OUTPUT"):
            decode_guest_records(b"VSAFE\tVM110\tOK\n")

    def test_non_synthetic_id_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "INVALID_TARGET_ID"):
            encode_guest_records([{"target": "\\bad path", "state": "OK", "detail_code": "SYNTHETIC_ONLY"}])

    def test_extra_freeform_string_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "INVALID_DETAIL_CODE"):
            encode_guest_records([{"target": "VM110", "state": "OK", "detail_code": "a real path"}])

    def test_boolean_not_valid_count(self):
        p = json.loads(encode_guest_records(ROWS))
        p["record_count"] = True
        with self.assertRaisesRegex(GuestProtocolError, "RECORD_COUNT_MISMATCH"):
            decode_guest_records(json.dumps(p).encode("utf-8"))

    def test_empty_records_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "INVALID_RECORD_COUNT"):
            encode_guest_records([])

    def test_more_than_32_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "INVALID_RECORD_COUNT"):
            encode_guest_records(ROWS * 33)

    def test_oversized_output_denied(self):
        with self.assertRaisesRegex(GuestProtocolError, "EMPTY_OR_OVERSIZED_STDOUT"):
            decode_guest_records(b"A" * 65537)

    def test_qga_stderr_not_exposed(self):
        r = make_synthetic_qga_reply(encode_guest_records(ROWS), stderr=b"private placeholder")
        parsed = parse_synthetic_qga_reply(r)
        self.assertEqual(parsed, ROWS)


if __name__ == "__main__":
    unittest.main()
