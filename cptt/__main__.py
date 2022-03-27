from __future__ import annotations

from cptt.parser import parser


def main(*args: list[str]) -> int:
    try:
        namespace = parser.parse_args(args)
    except SystemExit as exc:
        return exc.code

    print(namespace)
    return 0


def run_main():
    import sys
    raise SystemExit(main(*sys.argv[1:]))


if __name__ == '__main__':
    run_main()
