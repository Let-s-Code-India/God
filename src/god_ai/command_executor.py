"""Public command-execution API."""

from .executor import ExecutionResult, extract_commands, run_commands

__all__ = ["ExecutionResult", "extract_commands", "run_commands"]