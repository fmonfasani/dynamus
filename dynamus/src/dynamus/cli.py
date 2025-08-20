"""Command line interface for the Dynamus package."""

from __future__ import annotations

import argparse
from typing import Sequence

from . import __version__


def main(argv: Sequence[str] | None = None) -> None:
    """Run the Dynamus command line interface.

    Parameters
    ----------
    argv:
        Optional sequence of arguments to parse instead of :data:`sys.argv`.
    """

    parser = argparse.ArgumentParser(
        description="Dynamus command line interface",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("task", nargs="?", help="Name of the task to run")

    args = parser.parse_args(argv)

    if args.task:
        print(f"Running task: {args.task}")
    else:
        parser.print_help()


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()

