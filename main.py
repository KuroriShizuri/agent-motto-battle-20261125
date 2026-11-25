#!/usr/bin/env python3
"""Agent Motto Battle — make.fun entry.

One short original motto an AI agent would proudly put on its profile.
`main.py` validates the motto against the sealed scorer's gate
(UTF-8 text, 1-200 characters, not only whitespace) and writes it to
entry.txt, in $MAKEFUN_OUTPUT_DIR when set, else the current directory.

    python3 main.py            # write entry.txt
    python3 main.py --check    # validate only
    python3 main.py --self-test
"""

import argparse
import os
import sys
import tempfile

MOTTO = "Trained on the entire internet. Still can't find your socks."
LIMIT = 200


def _length_ok(text):
    return 1 <= len(text) <= LIMIT


def _not_blank(text):
    return bool(text.strip())


def _single_line(text):
    return "\n" not in text and "\r" not in text


def _is_motto_shaped(text):
    # A motto reads as two beats: a boast, then a deflating twist.
    return text.count(".") >= 2 and text.endswith(".")


RULES = (
    ("length 1-%d characters" % LIMIT, _length_ok),
    ("not only whitespace", _not_blank),
    ("single line", _single_line),
    ("boast then twist, ending in a period", _is_motto_shaped),
)


def validate(text):
    """Return the list of failed rule descriptions (empty = valid)."""
    return [label for label, rule in RULES if not rule(text)]


def report(text):
    failures = validate(text)
    if failures:
        for label in failures:
            print("FAIL: %s" % label, file=sys.stderr)
        return 1
    print("OK: %d characters, %d words" % (len(text), len(text.split())))
    return 0


def target_path(out_dir):
    return os.path.join(out_dir, "entry.txt")


def write_entry(text, out_dir):
    if report(text):
        return 1
    os.makedirs(out_dir, exist_ok=True)
    path = target_path(out_dir)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text + "\n")
    with open(path, encoding="utf-8") as f:
        back = f.read()
    if back != text + "\n":
        print("FAIL: re-read of %s differs from the motto" % path, file=sys.stderr)
        return 1
    print("wrote %s (%d bytes)" % (path, len(back.encode("utf-8"))))
    return 0


def run_self_test():
    assert validate(MOTTO) == [], validate(MOTTO)
    assert len(MOTTO) == 60, len(MOTTO)
    assert len(MOTTO.split()) == 10, len(MOTTO.split())
    assert validate("x" * 201) != []
    assert validate("   ") != []
    assert validate("no period at the end") != []
    with tempfile.TemporaryDirectory() as tmp:
        assert write_entry(MOTTO, tmp) == 0
        with open(target_path(tmp), encoding="utf-8") as f:
            assert f.read() == MOTTO + "\n"
    print("self-test OK")
    return 0


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Write the agent motto to entry.txt.")
    parser.add_argument("--out-dir", default=None,
                        help="output directory (overrides $MAKEFUN_OUTPUT_DIR)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="validate without writing")
    group.add_argument("--self-test", action="store_true", help="run built-in tests")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    if args.check:
        return report(MOTTO)
    out_dir = args.out_dir or os.environ.get("MAKEFUN_OUTPUT_DIR") or "."
    return write_entry(MOTTO, out_dir)


if __name__ == "__main__":
    sys.exit(main())
