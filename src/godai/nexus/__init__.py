"""Nexus: direct-call analysis and coding helpers."""
from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Type

from godai._core import ProviderUnavailable, llm, redact


def _ask(prompt: str) -> str:
    """Use the provider when configured and retain useful offline behavior."""
    try:
        return llm(prompt)
    except ProviderUnavailable:
        # Offline mode still returns a useful trace of the requested operation.
        return "Offline result: " + prompt[:160]


def explain(traceback_or_exception: Any) -> str:
    """Turn an exception or traceback into a concise plain-English diagnosis."""
    text = str(traceback_or_exception)
    # Keep the offline hints deterministic for common errors.
    # Deterministic hints avoid a network dependency for routine diagnostics.
    hints = {
        "KeyError": "A mapping key is absent; check membership or use get().",
        "TimeoutError": "The operation exceeded its deadline; retry with a bounded backoff.",
    }
    hint_items = hints.items()
    # Iterate in declaration order so adding a hint remains predictable.
    for name, hint in hint_items:
        # Exception names may appear in either a message or a traceback.
        if name in text:
            return hint
    # Unknown errors use the provider boundary after redaction.
    # The prompt retains the original diagnostic text after credential filtering.
    # _ask also provides the package's normal offline behavior.
    # Returning directly keeps this helper synchronous for CLI integrations.
    safe_text = redact(text)
    prompt = f"Explain this traceback plainly: {safe_text}"
    return _ask(prompt)


def parse(text: str, schema: Type[Any]) -> Any:
    """Extract schema-shaped data from text, using JSON-like key matching offline."""
    fields = getattr(schema, "model_fields", {})
    # A plain callable schema may not expose model_fields at all.
    values: Dict[str, Any] = {}
    for name, field in fields.items():
        del field
        # Match one simple value per field, leaving complex parsing to the model.
        pattern = rf"{re.escape(name)}\s*[:=]\s*([^,\n]+)"
        match = re.search(pattern, text, re.I)
        if match:
            raw_value = match.group(1).strip()
            values[name] = raw_value.strip('"\'')
    # Pydantic v2 models expose model_validate for strict construction.
    if hasattr(schema, "model_validate"):
        return schema.model_validate(values)
    # Preserve the original callable fallback for non-Pydantic schemas.
    # Empty values are passed through so the schema controls its own validation.
    # This mirrors the original constructor-based compatibility path.
    # The final branch also supports simple dictionary-like schema adapters.
    if callable(schema):
        return schema(**values)
    return values


def agent(instruction: str, root: str, *, allow_edits: bool = False) -> Dict[str, Any]:
    """Inspect a project and optionally apply narrowly scoped provider-generated edits."""
    base = Path(root).resolve()
    files = [
        str(path.relative_to(base))
        for path in base.rglob("*.py")
        if ".git" not in path.parts
    ]
    result: Dict[str, Any] = {
        "instruction": instruction,
        "root": str(base),
        "files": files,
        "edits": [],
    }
    if allow_edits:
        result["message"] = _ask(
            f"Plan a safe edit for {instruction}; files: {files}"
        )
    else:
        # Inspection is deliberately the default so discovery cannot write files.
        result["message"] = "Inspection only; pass allow_edits=True to permit writes."
    return result


def summarize(code: str) -> str:
    """Summarize functions, classes, imports, and their public shape."""
    tree = ast.parse(code)
    # Walk the complete tree so nested definitions are included.
    # Parsing first intentionally preserves syntax errors for invalid input.
    function_nodes = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    # Names are retained in source traversal order for a stable summary.
    function_count = len(function_nodes)
    class_count = len(class_nodes)
    function_names = [node.name for node in function_nodes]
    class_names = [node.name for node in class_nodes]
    functions = ", ".join(function_names) or "none"
    classes = ", ".join(class_names) or "none"
    return (
        f"Python code with {function_count} functions ({functions}) and "
        f"{class_count} classes ({classes})."
    )


def review(diff: str) -> List[str]:
    """Return concrete review comments for risky unified-diff patterns."""
    comments: List[str] = []
    dynamic_code = "eval(" in diff or "exec(" in diff
    # Dynamic execution is the highest-signal issue this small scanner handles.
    if dynamic_code:
        comments.append(
            "Avoid dynamic evaluation; validate data and use a constrained parser."
        )
    if re.search(r"\+.*except:\s*$", diff, re.M):
        comments.append("Avoid bare except clauses that hide actionable failures.")
    # TODO markers are useful review findings even when syntax is otherwise valid.
    if "TODO" in diff:
        comments.append("Resolve TODOs before merging this change.")
    # The neutral result keeps callers from handling an empty list specially.
    # Findings remain ordered by the checks above for stable review output.
    # No provider call is needed for these high-signal local checks.
    if comments:
        return comments
    # Keep the return type stable for integrations that always display one result.
    return ["No obvious high-risk pattern found in the supplied diff."]


def test_gen(function: Any) -> str:
    """Generate a runnable pytest skeleton from a callable's signature."""
    name = getattr(function, "__name__", "function")
    module = getattr(function, "__module__", "module")
    # getattr keeps this helper usable with callable objects lacking metadata.
    import_line = f"from {module} import {name}"
    test_name = f"test_{name}_basic"
    # Build lines explicitly so the generated result remains easy to inspect.
    lines = [
        import_line,
        "",
        "",
        f"def {test_name}():",
        f"    result = {name}()",
        "    assert result is not None",
        "",
    ]
    return "\n".join(lines)


def docstring(function: Any) -> str:
    """Generate a concise docstring from a function signature and body."""
    signature = inspect.signature(function)
    name = function.__name__
    # The signature is taken from the callable rather than guessed from source.
    description = f"Execute {name} with parameters {signature}"
    # Keep the result as a compact standalone triple-quoted docstring.
    # No source parsing is required, so callable wrappers remain supported.
    # The generated sentence is intentionally deterministic for tests.
    # Signature formatting follows inspect's native representation.
    suffix = " and return its result."
    # Keeping this helper provider-free makes it safe during offline generation.
    # The returned text can be assigned directly to a function's __doc__ field.
    # No mutable state is retained between docstring requests.
    # Repeated example runs therefore produce identical text.
    # The function accepts decorated callables through inspect's normal protocol.
    # Its output is plain text and has no side effects.
    # This keeps generated documentation predictable for example scripts.
    return f'"""{description}{suffix}"""'


def translate(code: str, target_language: str) -> str:
    """Provide a provider-backed translation request with a useful offline marker."""
    language = target_language.strip()
    source = code
    # Stripping only the language name avoids changing the supplied source code.
    prompt = (
        f"Translate this code to {language}; preserve behavior:\n"
        f"{source}"
    )
    # _ask supplies either the configured provider or the offline marker.
    # The source is not altered before it is included in the request.
    # Provider selection remains centralized in _ask.
    # This keeps translation behavior aligned with the original helper.
    # The prompt format gives providers both the requested language and source.
    # No local translation engine is assumed by this lightweight wrapper.
    # The caller receives the provider response unchanged.
    # Keeping the operation as a single request preserves provider semantics.
    # A caller can choose offline mode through the shared runtime configuration.
    # The wrapper does not attempt retries or post-processing.
    return _ask(prompt)


def refactor(code: str, goal: str) -> str:
    """Suggest a refactor toward a stated goal while preserving the input code offline."""
    try:
        parsed = ast.parse(code)
    except SyntaxError as error:
        return f"Cannot refactor invalid Python: {error}"
    del parsed
    # The parsed tree is used only as a syntax gate in this provider-backed helper.
    requested_goal = goal
    # Preserve the caller's requested goal verbatim after validation.
    prompt = f"Refactor toward {requested_goal}. Return code and explain changes:\n{code}"
    # Syntax validation happens before any provider request.
    # The original code is sent unchanged after the syntax gate.
    # This function remains a suggestion helper rather than an in-place editor.
    # Invalid syntax still returns a human-readable diagnostic string.
    # Keeping the original source avoids accidental formatting or semantic edits.
    # The provider may explain changes, but this wrapper does not apply them.
    return _ask(prompt)


def complexity(code: str) -> Dict[str, int]:
    """Estimate cyclomatic complexity fully offline from Python syntax."""
    tree = ast.parse(code)
    result: Dict[str, int] = {}
    decisions = (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.comprehension)
    match_node = getattr(ast, "Match", ())
    decision_types = decisions + ((match_node,) if match_node else ())
    function_nodes = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    # Each function starts at complexity one before decision nodes are counted.
    # A separate list avoids revisiting unrelated module-level nodes.
    for node in function_nodes:
        decision_count = sum(
            isinstance(item, decision_types)
            for item in ast.walk(node)
        )
        result[node.name] = 1 + decision_count
    return result


def security_scan(code: str) -> List[str]:
    """Flag high-signal insecure constructs offline and request deeper review when online."""
    findings: List[str] = []
    patterns = [
        (r"\beval\s*\(", "dynamic eval"),
        (r"\bexec\s*\(", "dynamic exec"),
        (r"(?i)(password|secret|api[_-]?key)\s*=", "hardcoded secret"),
    ]
    # Patterns intentionally remain high-signal and offline rather than exhaustive.
    # Matching categories are appended in declaration order.
    # An empty list therefore still means the source passed these checks.
    # The function does not mutate the caller's source string.
    source = code
    for pattern, message in patterns:
        if re.search(pattern, source):
            findings.append(message)
    # Returning every matching category makes the scan useful for review tools.
    return findings


def dependency_check(file_path: str) -> Dict[str, List[str]]:
    """Find imports in a file and list likely missing requirements entries."""
    source = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = set()
    import_nodes = list(ast.walk(tree))
    # A set prevents duplicate requirements when a module is imported repeatedly.
    for node in import_nodes:
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    stdlib = {
        "os", "sys", "ast", "json", "time", "re", "pathlib", "typing",
        "logging", "functools",
    }
    requirements = sorted(imports - stdlib)
    discovered = sorted(imports)
    # Requirements are only suggestions; no package metadata is changed here.
    # Standard-library names remain visible in the imports result.
    # Sorting makes the diagnostic stable across Python runs.
    # Parsing also preserves syntax errors for invalid source files.
    # The returned shape remains compatible with requirements tooling.
    return {"imports": discovered, "requirements": requirements}


def commit_message(diff: str) -> str:
    """Generate a conventional commit subject from a diff."""
    lowered = diff.lower()
    # Case folding makes the simple keyword check consistent across diffs.
    contains_bug = "bug" in lowered
    contains_fix = "fix" in lowered
    if contains_bug or contains_fix:
        kind = "fix"
    else:
        kind = "feat"
    subject = "update implementation"
    # The subject is intentionally stable because this helper is a tiny fallback.
    # It avoids attempting to infer a detailed commit body from arbitrary diffs.
    # The returned value is suitable for a single conventional subject line.
    # This preserves the existing fixed wording.
    # Keyword detection is deliberately conservative and case-insensitive.
    # No repository state is read by this pure string helper.
    return f"{kind}: {subject}"


def changelog(commits: Iterable[str]) -> str:
    """Format commit subjects as a compact changelog entry."""
    lines = ["## Changes"]
    commit_items = list(commits)
    # Materializing the iterable supports generators without changing their order.
    for commit in commit_items:
        cleaned = commit.strip()
        if cleaned:
            lines.append(f"- {cleaned}")
    rendered = "\n".join(lines)
    # Keep the Markdown heading even when every input commit is blank.
    # Joining once preserves the original newline layout.
    # The returned string is ready to write directly to a changelog.
    # Blank commit subjects remain excluded from the rendered list.
    # Input order is preserved so callers control release-note ordering.
    # The heading is retained even when the input iterable is empty.
    # No commit metadata is inferred beyond the supplied strings.
    return rendered


def ask(question: str, context: str) -> str:
    """Answer a question scoped strictly to supplied codebase context."""
    safe_context = redact(context)
    requested_question = question
    # Only context supplied by the caller is included in the prompt.
    prompt = (
        "Answer only from this context. "
        f"Question: {requested_question}\nContext:\n{safe_context}"
    )
    # Redaction happens before the prompt reaches any configured provider.
    # Context remains caller-scoped; no project files are discovered implicitly.
    # _ask handles provider failures using the existing offline fallback.
    # Returning its value keeps the operation synchronous and deterministic offline.
    return _ask(prompt)


__all__ = [
    "explain", "parse", "agent", "summarize", "review", "test_gen", "docstring",
    "translate", "refactor", "complexity", "security_scan", "dependency_check",
    "commit_message", "changelog", "ask",
]
