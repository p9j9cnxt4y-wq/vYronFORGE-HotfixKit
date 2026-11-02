"""Intentional negative control: defining main() is not calling main()."""
import sys


def main():
    sys.stdout.buffer.write(b"THIS_WOULD_ONLY_EXIST_IF_INVOKED\n")


# No entrypoint invocation: process exits 0 with empty stdout.
