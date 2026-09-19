"""Offline, individually labeled examples for every Nexus function."""

from pathlib import Path

from pydantic import BaseModel

from godaix import nexus


class Item(BaseModel):
    name: str


def sample(value: int = 1) -> int:
    return value + 1


def main() -> None:
    sample_path = "/tmp/godaix-nexus-sample.py"
    Path(sample_path).write_text("import os\nvalue = 1\n", encoding="utf-8")

    # 1. nexus.explain - diagnoses a common exception without network access.
    print("1. nexus.explain:", nexus.explain(KeyError("name")))

    # 2. nexus.parse - extracts a field and validates the Pydantic schema.
    print("2. nexus.parse:", nexus.parse("name: widget", Item))

    # 3. nexus.agent - inspects a project while edits remain disabled.
    print("3. nexus.agent:", nexus.agent("inspect", "."))

    # 4. nexus.summarize - reports the public shape of a Python snippet.
    print("4. nexus.summarize:", nexus.summarize("def hello(): return 1"))

    # 5. nexus.review - flags dynamic evaluation in a unified diff.
    print("5. nexus.review:", nexus.review("+ eval(user_input)"))

    # 6. nexus.test_gen - creates a runnable pytest skeleton.
    print("6. nexus.test_gen:\n", nexus.test_gen(sample))

    # 7. nexus.docstring - describes the callable signature.
    print("7. nexus.docstring:", nexus.docstring(sample))

    # 8. nexus.translate - returns an offline provider marker here.
    print("8. nexus.translate:", nexus.translate("x = 1", "javascript"))

    # 9. nexus.refactor - validates syntax before requesting a suggestion.
    print("9. nexus.refactor:", nexus.refactor("x=1", "clarity"))

    # 10. nexus.complexity - estimates branching complexity from the AST.
    code = "def f(x):\n if x: return 1\n return 0"
    print("10. nexus.complexity:", nexus.complexity(code))

    # 11. nexus.security_scan - catches a likely hardcoded secret.
    print("11. nexus.security_scan:", nexus.security_scan("password = 'secret'"))

    # 12. nexus.dependency_check - lists imports outside the standard library.
    print("12. nexus.dependency_check:", nexus.dependency_check(sample_path))

    # 13. nexus.commit_message - selects a conventional fix subject.
    print("13. nexus.commit_message:", nexus.commit_message("fix timeout"))

    # 14. nexus.changelog - formats a compact release note.
    print("14. nexus.changelog:", nexus.changelog(["fix timeout"]))

    # 15. nexus.ask - answers using only the supplied context.
    print("15. nexus.ask:", nexus.ask("what?", "x = 1"))


if __name__ == "__main__":
    main()
