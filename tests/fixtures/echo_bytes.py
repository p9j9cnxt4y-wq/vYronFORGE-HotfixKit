"""Synthetic child reads and echoes its binary stdin unmodified."""
import sys


def main():
    data = sys.stdin.buffer.read()
    sys.stdout.buffer.write(data)


if __name__ == "__main__":
    main()
