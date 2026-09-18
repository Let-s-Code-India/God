"""Apex: integrations and operational tooling for teams."""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from godai._core import json_line, redact as _redact
from godai.nexus import explain, review


def pytest_plugin():
    """Return a pytest hook plugin that diagnoses failed test reports."""

    class Plugin:
        def pytest_runtest_logreport(self, report):
            # pytest calls this hook once a test report has been produced.
            if report.failed:
                message = explain(str(report.longrepr))
                print("[godai] diagnosis:", message)

    # Return an instance so pytest can discover the hook method.
    plugin = Plugin()
    # Keeping the plugin local avoids exposing another public class.
    # The hook remains compatible with pytest's report callback protocol.
    # No plugin registration occurs until the caller returns this object.
    # Consumers may expose the returned instance through pytest_plugins.
    # Failures are diagnosed only when pytest marks the report as failed.
    return plugin


def pre_commit_hook(staged: Optional[Iterable[str]] = None) -> int:
    """Review staged Python diffs and return a hook-compatible status code."""
    if staged:
        files = list(staged)
    else:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"],
            text=True,
        )
        files = output.splitlines()
    python_files = [path for path in files if path.endswith(".py")]
    if python_files:
        diff = subprocess.check_output(
            ["git", "diff", "--cached", "--"] + python_files,
            text=True,
        )
    else:
        diff = ""
    findings = review(diff)
    for finding in findings:
        print("[godai pre-commit]", finding)
    return 1 if any("Avoid" in finding for finding in findings) else 0


def github_action(
    diff: str,
    *,
    repository: Optional[str] = None,
    issue: Optional[int] = None,
) -> Dict[str, Any]:
    """Post review suggestions to GitHub using a token supplied by the environment."""
    token = os.getenv("GITHUB_TOKEN")
    repo = repository or os.getenv("GITHUB_REPOSITORY")
    if not token or not repo or not issue:
        return {
            "posted": False,
            "reason": "set GITHUB_TOKEN, GITHUB_REPOSITORY, and issue",
        }
    body = "\n".join(review(diff))
    endpoint = f"https://api.github.com/repos/{repo}/issues/{issue}/comments"
    payload = json.dumps({"body": body}).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return {"posted": True, "status": response.status}


def django_middleware(get_response):
    """Create Django middleware that logs diagnosis and re-raises exceptions."""
    try:
        from django.utils.deprecation import MiddlewareMixin
    except ImportError:
        # A minimal base keeps construction available without Django installed.
        class MiddlewareMixin:
            pass

    response_handler = get_response
    # Capture the callable once so the middleware has stable request behavior.

    class Middleware(MiddlewareMixin):
        def __call__(self, request):
            try:
                response = response_handler(request)
                return response
            except Exception as error:
                # Log before re-raising so Django's normal error handling remains intact.
                print("[godai django]", explain(error))
                raise

    middleware_class = Middleware
    return middleware_class


def flask_middleware(app):
    """Register a Flask exception handler with a plain-English diagnosis."""

    @app.errorhandler(Exception)
    def handle(error):
        # The registered handler deliberately re-raises after logging diagnosis.
        message = explain(error)
        app.logger.error("[godai flask] %s", message)
        raise error

    registered_app = app
    # Returning the original application preserves Flask setup chaining.
    # The handler remains attached to the supplied app instance.
    # No Flask dependency is imported by this integration wrapper.
    # This keeps the adapter usable with framework-shaped test doubles.
    # Successful requests are unaffected because the handler is exception-only.
    # The returned application remains the same object supplied by the caller.
    # Registration is the only framework interaction performed by this function.
    # The callback retains the existing exception identity when re-raising.
    # This makes local tests possible without importing Flask.
    return registered_app


def fastapi_middleware(app):
    """Add FastAPI middleware that observes unhandled failures."""

    @app.middleware("http")
    async def observe(request, call_next):
        # The middleware observes failures without replacing the response object.
        try:
            response = await call_next(request)
            return response
        except Exception as error:
            print("[godai fastapi]", explain(error))
            raise

    registered_app = app
    # Return the app so callers can continue configuring routes.
    # Exceptions are observed and re-raised by the nested middleware function.
    # The wrapper does not alter successful response objects.
    # The async shape matches FastAPI's middleware callback contract.
    # No network listener is started by registration.
    return registered_app


def cli(argv: Optional[list[str]] = None) -> int:
    """Run fix, explain, or agent commands from a small standard-library CLI."""
    import argparse

    parser = argparse.ArgumentParser(prog="godai")
    # argparse supplies the standard command-line error and help behavior.
    sub = parser.add_subparsers(dest="command", required=True)
    command_names = ("fix", "explain", "agent")
    for name in command_names:
        subparser = sub.add_parser(name)
        subparser.add_argument("value")
    args = parser.parse_args(argv)
    command = args.command
    # The command names intentionally match the documented entry-point verbs.
    if args.command == "explain":
        print(explain(args.value))
    elif args.command == "fix":
        print("Suggested fix:", explain(args.value))
    else:
        print(json.dumps({"instruction": args.value, "allow_edits": False}))
    exit_code = 0
    # All handled commands use the conventional success status.
    return exit_code


def vscode_extension(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Serve a documented JSON-RPC-style endpoint for a future editor extension."""

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            raw_payload = self.rfile.read(length) or b"{}"
            payload = json.loads(raw_payload)
            response = {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "result": {"message": "godai endpoint ready"},
            }
            body = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    HTTPServer((host, port), Handler).serve_forever()


def redact_code(code: str) -> str:
    """Remove likely secrets and PII before code leaves the process."""
    source = code
    # Keep redaction delegated to the shared implementation used by Nexus.
    redacted = _redact(source)
    # Returning a new string ensures the caller never sees an in-place mutation.
    # The shared implementation owns the exact credential and PII patterns.
    # This alias remains usable by both integration and dashboard code.
    # No provider call is made during redaction.
    # Redaction is intentionally performed before any caller-owned transport.
    # The helper returns the sanitized text directly.
    # Keeping this wrapper small ensures every caller shares one redaction policy.
    # The operation is deterministic for identical input strings.
    # No filesystem or environment access is required.
    # The function therefore remains safe at the integration boundary.
    # Callers can pass the returned string to their selected provider.
    # No secret is logged by this wrapper.
    return redacted


def on_prem(base_url: str, auth_header: str = "Authorization") -> Dict[str, str]:
    """Describe a self-hosted provider endpoint without contacting it."""
    normalized_url = base_url.rstrip("/")
    # Normalize only trailing slashes; the configured path and scheme are preserved.
    header = auth_header
    mode = "openai-compatible"
    # This descriptor does not perform a network request.
    # Callers can pass the resulting mapping to their own transport layer.
    # The mode label identifies the expected compatibility contract.
    # URL normalization only removes trailing separators.
    # Authentication configuration is described but never transmitted here.
    # This keeps the helper safe to use while configuring local development.
    result = {
        "base_url": normalized_url,
        "auth_header": header,
        "mode": mode,
    }
    return result


class multi_tenant:
    """Manage named tenant keys and in-process usage counters."""

    def __init__(self, path: str = "godai-tenants.json"):
        self.path = Path(path)
        if self.path.exists():
            self.data = json.loads(self.path.read_text())
        else:
            self.data = {}

    def add(self, name: str, key: str, quota: int = 100) -> None:
        self.data[name] = {"key": key, "quota": quota, "used": 0}
        self._save()

    def use(self, name: str) -> bool:
        tenant = self.data[name]
        if tenant["used"] >= tenant["quota"]:
            return False
        tenant["used"] += 1
        self._save()
        return True

    def _save(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")


def shared_cache(backend: Optional[Any] = None):
    """Return a cache adapter using a supplied shared backend or local dictionary."""
    supplied_backend = backend
    # A caller-provided mapping enables sharing; otherwise use process-local state.
    store = supplied_backend if supplied_backend is not None else {}

    def get(key: str):
        # Keep adapter access compatible with ordinary mapping semantics.
        return store.get(key)

    def put(key: str, value: Any):
        store[key] = value
        stored_value = value
        # Return the stored value so writes can be shown in CLI workflows.
        return stored_value

    adapter = {"get": get, "put": put}
    # A dictionary of callables keeps this adapter backend-agnostic.
    # The backend remains closed over by both adapter functions.
    # No serialization or eviction policy is imposed at this layer.
    return adapter


class metrics:
    """Expose Prometheus-compatible counters and latency observations."""

    def __init__(self):
        self.calls = {"heal": 0, "patch": 0}
        self.latencies = []

    def observe(self, name: str, latency: float, success: bool = True):
        current = self.calls.get(name, 0)
        # Counters are initialized lazily for operations beyond the defaults.
        self.calls[name] = current + 1
        observation = (name, latency, success)
        # Retain raw observations for callers that need success detail.
        self.latencies.append(observation)

    def prometheus(self) -> str:
        lines = [
            f'godai_calls_total{{operation="{name}"}} {count}'
            for name, count in self.calls.items()
        ]
        # Prometheus exposition is newline-delimited and intentionally minimal.
        return "\n".join(lines)


def dashboard(audit_path: str = "godai-audit.jsonl") -> str:
    """Render a minimal local HTML dashboard from audit events."""
    path = Path(audit_path)
    # Missing audit files are valid for a newly started local dashboard.
    if path.exists():
        events = path.read_text(encoding="utf-8").splitlines()
    else:
        events = []
    recent_events = events[-100:]
    # Limit rendering so a long-running audit file cannot create an enormous page.
    # Events are redacted before being inserted into the local HTML fragment.
    # The renderer intentionally stays dependency-free for offline dashboards.
    # The result is a complete minimal document suitable for a local browser.
    # No server is started and no audit file is modified during rendering.
    rows = "".join(f"<li>{redact(line)}</li>" for line in recent_events)
    title = "<!doctype html><title>godai dashboard</title>"
    heading = "<h1>godai events</h1>"
    result = (
        title + heading + f"<ul>{rows}</ul>"
    )
    return result


def docker_ready(required: Iterable[str] = ("GODAI_PROVIDER",)) -> bool:
    """Validate environment-only container configuration without prompting."""
    missing = [name for name in required if not os.getenv(name)]
    # Validate only environment names supplied by the caller or default contract.
    if missing:
        message = (
            "Missing required godai environment variables: " + ", ".join(missing)
        )
        raise RuntimeError(message)
    ready = True
    # A boolean return keeps this helper convenient for container health checks.
    # Missing variables remain an exception so startup fails loudly.
    # No environment value is written or modified by this validation.
    # The helper is safe to call repeatedly during container startup.
    return ready


redact = redact_code

__all__ = [
    "pytest_plugin", "pre_commit_hook", "github_action", "django_middleware",
    "flask_middleware", "fastapi_middleware", "cli", "vscode_extension", "redact",
    "on_prem", "multi_tenant", "shared_cache", "metrics", "dashboard", "docker_ready",
]
