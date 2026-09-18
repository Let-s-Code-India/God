# godai

> Resilient AI tooling for healing Python calls, understanding code, surviving bad networks, and shipping developer integrations.

<p align="center">
  <img src="https://raw.githubusercontent.com/ayushgiriai21-cmd/God/main/assets/logo.png" alt="godai logo" width="180">
</p>

<p align="center">
  <a href="https://pypi.org/project/godai/"><img src="https://img.shields.io/pypi/v/godai.svg" alt="PyPI version"></a>
  <a href="https://github.com/ayushgiriai21-cmd/God/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ayushgiriai21-cmd/God.svg" alt="MIT license"></a>
  <img src="https://img.shields.io/pypi/pyversions/godai.svg" alt="Python versions">
  <a href="https://github.com/ayushgiriai21-cmd/God/actions"><img src="https://img.shields.io/github/actions/workflow/status/ayushgiriai21-cmd/God/ci.yml?label=CI" alt="CI status"></a>
</p>

`godai` is one installable package with four deliberately independent sub-libraries. Importing the root stays cheap: `aura`, `nexus`, `aether`, and `apex` load lazily on first access.

## What is godai?

- **Aura** provides decorators for healing, retrying, validating, tracing, caching, sandboxing, auditing, and rate-limiting Python calls.
- **Nexus** provides direct coding functions for explanation, structured parsing, project agents, reviews, test generation, refactoring, complexity, and security analysis.
- **Aether** provides resilience primitives for timeouts, circuits, offline queues, fallback providers, health checks, persistent caches, and degraded operation.
- **Apex** connects godai to pytest, pre-commit, GitHub Actions, web frameworks, CLI workflows, dashboards, metrics, tenants, and on-premise deployments.

The package is authored by **Ayush Giri**. The verified repository is [github.com/ayushgiriai21-cmd/God](https://github.com/ayushgiriai21-cmd/God). No separate project website URL is configured in the repository metadata; the static documentation site lives in [`docs/`](docs/).

## Dependencies

`pip install godai` installs these dependencies together. They are normal project dependencies, not optional extras.

| Dependency | Purpose |
| --- | --- |
| `rich>=13.7` | Rich terminal output for CLI-oriented integrations. |
| `requests>=2.31` | HTTP transport for provider and integration calls. |
| `python-dotenv>=1.0` | Loading provider configuration from `.env` files. |
| `pydantic>=2.0` | Input/output schemas and structured parsing. |
| `openai>=1.0` | OpenAI SDK compatibility. |
| `anthropic>=0.30` | Anthropic Claude integration. |
| `google-generativeai>=0.8` | Google Gemini integration. |
| `groq>=0.6` | Groq fast-inference integration. |
| `flask>=3.0` | Flask middleware integration. |
| `fastapi>=0.110` | FastAPI middleware integration. |
| `uvicorn>=0.29` | ASGI serving for FastAPI-based tooling. |
| `pytest>=7.0` | The Apex pytest plugin and test-oriented tooling. |

## Installation

### Normal environments

Use a virtual environment, especially on Linux distributions that enforce PEP 668:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install godai
```

Windows PowerShell equivalent:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install godai
```

### Installing on Termux (Android)

Installing directly in Termux is expected to fail when `pydantic-core` has no matching Android wheel and falls back to a Rust/maturin build. Errors commonly include `Unsupported Android architecture`. Use Ubuntu inside `proot-distro` instead:

```bash
pkg install proot-distro
proot-distro install ubuntu
proot-distro login ubuntu
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv
python3 -m venv godenv
source godenv/bin/activate
pip install godai
```

During `apt upgrade`, `tzdata` may show a timezone prompt. Select your geographic area and city when prompted. On a non-interactive setup, set `DEBIAN_FRONTEND=noninteractive` and `TZ=UTC` before the upgrade, or run `dpkg-reconfigure tzdata` later.

## Known Environment Issues

### Termux / Android

`pydantic-core` is a Rust extension and Android/Termux may not have a compatible prebuilt wheel. Maturin can report `Unsupported Android architecture`. Install through Ubuntu in `proot-distro` using the steps above; do not try to work around it by removing a required dependency.

### iSH / iPadOS terminal apps

iSH uses an Alpine/musl-based environment and often runs under x86 emulation. A matching `pydantic-core` wheel may not exist, and a usable Rust toolchain may not be available. Use a proper Linux VM/container or a cloud development environment such as GitHub Codespaces or Replit on iPad instead of installing this package directly in iSH.

### `externally-managed-environment` / PEP 668

Newer Debian and Ubuntu installations may reject system-wide pip writes. Create and activate a virtual environment first:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install godai
```

Do not remove the distribution's `EXTERNALLY-MANAGED` marker. `pip install --break-system-packages` is a last-resort system choice, not the recommended installation path.

### Rust, maturin, or missing wheel errors

On unsupported Python/platform combinations, pip may attempt to compile `pydantic-core` and fail with `cargo`, `rustc`, or `maturin` errors. Use a supported CPython release with a compatible wheel, preferably Python 3.10 or newer, and upgrade pip before retrying. The package metadata allows Python 3.9, but current `pydantic-core` releases declare Python 3.10+; Python 3.9 users may need a compatible dependency resolution or should use Python 3.10+.

### Dependency resolution conflicts

If pip reports `ResolutionImpossible`, inspect the first conflicting requirement and update pip in a fresh environment. Do not mix unrelated global packages into the install:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install godai
```

### Alpine, musl, emulated, or unusual architectures

Alpine's musl libc, iSH's emulated x86 environment, and less common CPU
architectures can all lack a compatible `pydantic-core` wheel. In that case
pip falls back to a native build even when the Python version is supported.
Prefer a glibc-based Ubuntu environment with CPython 3.10+ and a matching
wheel. If you must retry the build, make the build tools explicit first:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install godai
```

Termux package maintainers sometimes ship Rust-backed extensions as separate
native packages, but that does not make arbitrary pip builds on Android
reliable; the Ubuntu `proot-distro` route above remains the supported setup.

### TLS certificate failures

`SSLCertVerificationError`, `CERTIFICATE_VERIFY_FAILED`, and similar errors usually mean the host Python or corporate proxy lacks a trusted CA bundle. Update the operating-system CA certificates, configure the organization’s CA bundle as documented by its proxy, and retry in a fresh environment. Avoid disabling TLS verification.

### Missing provider or system dependency

Provider SDKs are installed by default, but an environment can still have a broken or incomplete installation. godai’s dependency helper raises a clear `ImportError` naming the exact command, such as `python -m pip install torch`, rather than hiding the problem behind a raw traceback. Install the named package in the active virtual environment and retry.

## Examples

Run examples from the repository root, inside an activated environment where godai is installed:

```bash
python3 examples/aura_examples.py
python3 examples/nexus_examples.py
python3 examples/aether_examples.py
python3 examples/apex_examples.py
python3 examples/combined_examples.py
```

All five files use offline or local paths and run without an API key. The combined workflow touches all 60 public members.

## Quick Start

```python
from godai import aura, nexus, aether, apex

@aura.trace
@aura.heal(retries=1)
def add(left: int, right: int) -> int:
    return left + right

print(add(2, 3))
print(nexus.explain(KeyError("name")))
print(aether.heuristics(ZeroDivisionError()))
print(apex.redact("api_key=do-not-send-this"))
```

## API Reference

Every public member is listed below. The static site in [`docs/`](docs/) expands each entry with an executable example taken from the repository’s example files.

### Aura

| Member | Description |
| --- | --- |
| `heal` | Diagnoses runtime exceptions, logs an explanation, retries, and re-raises after failures. |
| `patch` | Requests corrected Python, strips fences, validates with `ast.parse()`, and executes the replacement in a controlled namespace. |
| `retry` | Retries transient/network errors with exponential backoff and fails fast on logic errors. |
| `validate` | Validates inputs and outputs against a Pydantic model or dictionary schema. |
| `trace` | Logs arguments, return value, exceptions, and elapsed time. |
| `cache` | Memoizes results with optional whitespace-normalized semantic caching. |
| `async_heal` | Async-compatible healing decorator for coroutine functions. |
| `sandbox` | Runs a decorated function with a restricted builtins mapping. |
| `explain` | Adds a plain-English explanation note to raised exceptions. |
| `benchmark` | Measures and logs function execution timing and wrapper overhead. |
| `guard` | Blocks execution with a clear message when environment variables or packages are missing. |
| `dry_run` | Logs configured side-effect interception for safe test paths. |
| `audit` | Writes calls, successes, and exceptions to a JSON-lines audit file. |
| `fallback` | Returns a fallback function result or default after a failure. |
| `rate_limit` | Uses a token bucket to throttle calls and cap provider cost. |

### Nexus

| Member | Description |
| --- | --- |
| `explain` | Produces a plain-English diagnosis for an exception or traceback. |
| `parse` | Extracts schema-shaped values from text and validates a Pydantic model. |
| `agent` | Inspects a project directory and gates edits behind `allow_edits`. |
| `summarize` | Summarizes functions, classes, and the public shape of Python code. |
| `review` | Flags risky patterns in a unified diff. |
| `test_gen` | Generates a runnable pytest skeleton for a callable. |
| `docstring` | Generates a concise docstring from a function signature. |
| `translate` | Requests a behavior-preserving translation to another language. |
| `refactor` | Requests a refactor toward a stated goal after syntax validation. |
| `complexity` | Estimates cyclomatic complexity offline using `ast`. |
| `security_scan` | Flags `eval`, `exec`, and likely hardcoded secrets offline. |
| `dependency_check` | Finds imports and suggests non-stdlib requirements entries. |
| `commit_message` | Generates a conventional commit subject from a diff. |
| `changelog` | Formats commit subjects into a changelog entry. |
| `ask` | Answers a question scoped to supplied code context. |

### Aether

| Member | Description |
| --- | --- |
| `timeout` | Enforces a hard deadline and raises `TimeoutError` promptly. |
| `circuit_breaker` | Tracks provider failures, opens a circuit, and fails fast during cooldown. |
| `offline_queue` | Persists failed JSON requests in SQLite for later replay. |
| `heuristics` | Diagnoses common Python exceptions without network access. |
| `fallback_provider` | Tries configured providers in order and returns the first success. |
| `degraded_mode` | Detects unavailable networking and logs an offline-mode warning. |
| `lazy_load` | Imports a heavy module only at first actual use. |
| `zero_overhead` | Benchmarks decorated fast-path overhead. |
| `network_probe` | Measures connection quality and recommends timeout/retry values. |
| `missing_dependency_helper` | Raises an exact pip command for an unavailable dependency. |
| `cache_store` | Provides bounded TTL disk-and-memory caching. |
| `debounce` | Suppresses repeated identical calls during a configured window. |
| `status` | Reports online, offline, degraded, or circuit-open health. |
| `rust_core` | Uses a future compiled extension when present and a Python reference otherwise. |
| `config` | Centralizes timeout, retry, circuit, and cache settings. |

### Apex

| Member | Description |
| --- | --- |
| `pytest_plugin` | Returns a pytest hook plugin that diagnoses failed tests. |
| `pre_commit_hook` | Reviews staged Python diffs and returns a hook status code. |
| `github_action` | Posts suggested fixes to GitHub using `GITHUB_TOKEN`. |
| `django_middleware` | Captures and diagnoses unhandled Django exceptions with guarded imports. |
| `flask_middleware` | Registers a Flask exception diagnosis handler. |
| `fastapi_middleware` | Adds FastAPI middleware that observes unhandled failures. |
| `cli` | Provides `godai fix`, `godai explain`, and `godai agent` commands. |
| `vscode_extension` | Serves a documented local JSON-RPC-style editor endpoint. |
| `redact` | Removes likely secrets and PII before code leaves the process. |
| `on_prem` | Describes self-hosted OpenAI-compatible endpoint configuration. |
| `multi_tenant` | Stores tenant keys, quotas, and usage counters. |
| `shared_cache` | Exposes a shared-backend cache adapter. |
| `metrics` | Produces Prometheus-compatible call counters. |
| `dashboard` | Renders an HTML history view from audit events. |
| `docker_ready` | Validates required environment variables without prompting. |

## Supported LLM Providers

Set the provider and its credential before making an online call. `offline` and `local` are safe defaults for examples.

| Provider | Environment variables |
| --- | --- |
| Anthropic Claude | `GODAI_PROVIDER=anthropic`, `ANTHROPIC_API_KEY=...` |
| OpenAI GPT | `GODAI_PROVIDER=openai`, `OPENAI_API_KEY=...` |
| Google Gemini | `GODAI_PROVIDER=gemini`, `GOOGLE_API_KEY=...` |
| Groq | `GODAI_PROVIDER=groq`, `GROQ_API_KEY=...` |
| xAI Grok | `GODAI_PROVIDER=xai`, `XAI_API_KEY=...` |
| Ollama | `GODAI_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434` |
| Qwen | `GODAI_PROVIDER=qwen`, `DASHSCOPE_API_KEY=...` |
| OpenRouter | `GODAI_PROVIDER=openrouter`, `OPENROUTER_API_KEY=...` |
| Generic OpenAI-compatible | `GODAI_PROVIDER=openai_compatible`, `GODAI_BASE_URL=https://host/v1`, `GODAI_API_KEY=...` |

For the provider-specific cloud entries, set the provider-specific key shown
above. The low-level OpenAI-compatible transport sends `GODAI_API_KEY` as its
Bearer token, so set that shared variable as well when using `openai`, `groq`,
`xai`, `qwen`, or `openrouter` with the built-in HTTP transport.

Optional model and resilience settings use `GODAI_MODEL`, `GODAI_TIMEOUT`, `GODAI_RETRIES`, `GODAI_CIRCUIT_THRESHOLD`, and `GODAI_CACHE_TTL`.

## License

godai is released under the [MIT License](LICENSE).

## Contributing

Open an issue or pull request on [ayushgiriai21-cmd/God](https://github.com/ayushgiriai21-cmd/God). Keep changes focused, add or update runnable examples for public behavior, and run the offline example suite before requesting review.

## About the Author

**Ayush Giri** · GitHub: [@ayushgiriai21-cmd](https://github.com/ayushgiriai21-cmd) · Repository: [github.com/ayushgiriai21-cmd/God](https://github.com/ayushgiriai21-cmd/God)

The repository does not currently declare a separate project website URL. The local documentation website is available from [`docs/index.html`](docs/index.html).
