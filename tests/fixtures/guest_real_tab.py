"""Synthetically emits the actual tab delimiter."""
import sys


def main():
    row = chr(9).join(("VSAFE", "VM110", "OK", "SYNTHETIC_ONLY"))
    sys.stdout.buffer.write((row + "\n").encode("ascii"))


if __name__ == "__main__":
    main()
