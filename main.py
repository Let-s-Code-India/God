"""Backward-compatible script entry point; use the installed ``god`` command."""

from god_ai.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
