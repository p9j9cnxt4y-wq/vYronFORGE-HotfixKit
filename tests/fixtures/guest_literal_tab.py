"""Intentional negative control: emits backslash+t instead of ASCII HT (09)."""
import sys


def main():
    sys.stdout.buffer.write(b"VSAFE\\tVM110\\tOK\\tSYNTHETIC_ONLY\n")


if __name__ == "__main__":
    main()
