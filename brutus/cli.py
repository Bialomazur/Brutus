import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="brutus",
        description=(
            "Project CLI scaffold. Install with `pip install -e .` and run `brutus --help`."
        ),
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit",
    )

    args = parser.parse_args(argv)

    if args.version:
        # Keep version in one place (pyproject) but avoid importing packaging tooling here.
        print("brutus")
        return 0

    parser.print_help()
    return 0
