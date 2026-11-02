"""Synthetic guest program; local-only; no external interactions."""
import json
import sys


def main():
    rows = [
        {"target": "VM110", "state": "OK", "detail_code": "AUTH_READ_COMPLETED"},
        {"target": "VM100", "state": "UNKNOWN", "detail_code": "NOT_INSPECTED"},
        {"target": "VM170", "state": "WARN", "detail_code": "SYNTHETIC_ONLY"},
    ]
    payload = {"protocol": "VYF_GUEST_RECORDS_V1", "completed": True,
               "record_count": len(rows), "records": rows}
    sys.stdout.buffer.write((json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
