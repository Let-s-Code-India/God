"""Backward-compatible web entry point."""

from god_ai.web import create_app, serve


if __name__ == "__main__":
    serve()
