# God AI / AURA — v1.1.1

<p align="center">
  <img src="assets/logo.svg" alt="God AI logo" width="180" />
</p>

<p align="center">
  <strong>A hybrid, confirmation-gated terminal assistant, a typed Python SDK, and the <code>god_ai.aura</code> runtime for resilient, model-assisted developer workflows.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/god-ai/"><img src="https://img.shields.io/pypi/v/god-ai.svg" alt="PyPI version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license" /></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python 3.9+" />
  <a href="https://github.com/ayushgiriai21-cmd/God/actions/workflows/publish.yml"><img src="https://img.shields.io/badge/CI-publish.yml-informational.svg" alt="Publish workflow" /></a>
</p>

God AI (package name on PyPI: **`god-ai`**, import name: **`god_ai`**) is three things in one repository:

1. **A terminal assistant** — the `god` / `aura` console commands. You describe a task in plain English, the assistant proposes shell commands, and *you* confirm every command before it runs.
2. **A typed Python SDK** (`from god_ai import ...`) — configuration, an LLM router across six providers, guarded code generation, self-healing decorators, structured parsing, and safe system inspection.
3. **The `god_ai.aura` namespace** — a curated, backward-compatible surface over the same SDK, purpose-built for import ergonomics (`from god_ai import aura`) and for the 1.1.1 extension suite (tracing, sandboxed execution, benchmarking, cost profiling, and a bounded autonomous pytest agent).

Every "AI-assisted" feature in this project degrades honestly: if a provider call fails, the original exception is preserved and re-raised — nothing is silently swallowed or faked as a success.

---

## Table of contents

- [What's new in 1.1.1](#whats-new-in-111)
- [Installation](#installation)
- [Configuration](#configuration)
- [Architecture — what each module does](#architecture--what-each-module-does)
- [CLI reference](#cli-reference)
- [Python SDK reference](#python-sdk-reference)
  - [Configuration API](#configuration-api)
  - [Self-healing](#self-healing-aurahealheal)
  - [Diagnostics — trace and auto-patch](#diagnostics--trace-and-auto-patch)
  - [Ghost execution — natural language to Python](#ghost-execution--natural-language-to-python)
  - [Sandboxed execution and expression evaluation](#sandboxed-execution-and-expression-evaluation)
  - [Structured parsing](#structured-parsing)
  - [Performance tooling](#performance-tooling)
  - [Autonomous agent](#autonomous-agent-auraagent)
  - [System detection](#system-detection)
  - [LLM client — the provider router](#llm-client--the-provider-router)
  - [Conversation memory](#conversation-memory)
  - [Command execution](#command-execution)
  - [Web dashboard API](#web-dashboard-api)
- [Examples — all 14 runnable files, in full](#examples--all-14-runnable-files-in-full)
- [Documentation portal](#documentation-portal)
- [Development and verification](#development-and-verification)
- [Release process](#release-process)
- [Project structure](#project-structure)
- [Credits](#credits)
- [License](#license)

---

## What's new in 1.1.1

- Expanded `god_ai.aura` exports: `trace_exceptions`, `auto_patch`, `exec_sandboxed`, `eval_expr`, `to_pydantic`, `to_dataclass`, `benchmark`, and `cost_profiler`, on top of the original `configure`, `heal`, `do`, `parse`, `optimize`, `agent`, and `system`.
- Lightweight core install (`rich`, `requests`, `python-dotenv`, `pydantic`) with opt-in extras: `aura`, `torch`, `web`, `cloud`, and `examples`.
- 14 runnable example files: the 4 original compatibility examples plus 10 new integration blueprints covering PyTorch, TensorFlow, NumPy, FastAPI, Flask, Turtle graphics, an autonomous pytest bot, a pandas data pipeline, structured "multimodal" parsing, and a full-stack scaffolder.
- A static documentation portal under `docs/`, deployable as-is to GitHub Pages, with a provider setup wizard, full API reference, and every example embedded inline.
- Tag-triggered PyPI publishing via `.github/workflows/publish.yml`, which regenerates logo assets, builds the sdist/wheel, and validates them with Twine before upload.
- Backward-compatible root-level shims (`main.py`, `config.py`, `llm_handler.py`, `memory_manager.py`, `command_executor.py`, `web_server.py`) so any code written against the pre-package layout keeps working unmodified.

## Installation

```bash
python -m pip install god-ai
```

Install optional capability groups as needed — the core install intentionally excludes heavy ML/web dependencies:

```bash
python -m pip install "god-ai[aura]"      # numpy, torch, tensorflow*, flask, fastapi, uvicorn, and every cloud SDK
python -m pip install "god-ai[torch]"     # numpy, torch, torchvision only
python -m pip install "god-ai[web]"       # fastapi, uvicorn, flask only
python -m pip install "god-ai[cloud]"     # openai, google-generativeai, anthropic, groq SDKs
python -m pip install "god-ai[examples]"  # everything the examples/ folder needs, plus pytest
```

`tensorflow` is pulled in only when `platform_machine != 'arm64'` and `python_version < '3.13'` — Apple Silicon and Python 3.13+ environments skip it automatically. The `turtle` example (`06_turtle_ai_generative_art.py`) uses Python's standard-library `turtle` module and needs no extra install, but it does need a display (it will not run headless).

## Configuration

Configuration is process-wide, immutable per call, and resolved in this order: `aura.configure(**kwargs)` keyword arguments **override** environment variables, which in turn override the built-in defaults. A `.env` file in the current working directory (or the repository root) is loaded automatically the first time `configure()` runs.

Only five settings have environment-variable equivalents — the rest are Python-only keyword arguments:

| Setting | Environment variable | Keyword argument | Default |
|---|---|---|---|
| Provider | `AURA_PROVIDER` | `provider` | `"openrouter"` |
| API key | `AURA_API_KEY` | `api_key` | `""` |
| Base URL | `AURA_BASE_URL` | `base_url` | `""` (auto-resolved) |
| Model | `AURA_MODEL` | `model` | `"openrouter/auto"` |
| Free-tier routing | `AURA_FREE_ONLY` (`"1"`/`"true"`/`"yes"`) | `free_only` | `False` |
| Request timeout (seconds) | *(none — Python only)* | `request_timeout` | `120` |
| Heal retries | *(none — Python only)* | `heal_retries` | `1` |
| Ghost execution timeout (seconds) | *(none — Python only)* | `ghost_timeout` | `30` |

`configure()` also accepts the aliases `name` (→ `model`) and `timeout` (→ `request_timeout`).

**Automatic normalization** (`GodConfig.normalized()`), applied on every `configure()` call:

- `provider="ollama"` is treated as `provider="local"`.
- `provider="openrouter"` with **no** `api_key` silently falls back to `provider="local"` — this is what lets the CLI and examples "just work" without any key on a machine running Ollama.
- If the resolved provider is `local` and `model` is still the default `"openrouter/auto"`, the model becomes `"llama3"`.
- If the resolved provider is `local` and `base_url` is empty (or still points at `openrouter.ai`), it's rewritten to `http://localhost:11434/v1`.
- If the resolved provider is `openrouter` and `base_url` is empty, it becomes `https://openrouter.ai/api/v1`.

**Validation** (`GodConfig.validate()`) raises `ValueError` from `configure()` if: the provider isn't one of `openai`, `openrouter`, `gemini`, `anthropic`, `groq`, `local` (or the `ollama` alias); the model is blank; `request_timeout < 5`; `heal_retries < 0`; or `ghost_timeout < 1`.

### OpenRouter

```bash
export AURA_PROVIDER=openrouter
export AURA_API_KEY="your-key"
export AURA_MODEL="openrouter/auto"
export AURA_BASE_URL="https://openrouter.ai/api/v1"
```

### Ollama (local, no API key)

```bash
export AURA_PROVIDER=ollama
export AURA_BASE_URL=http://localhost:11434/v1
export AURA_MODEL=llama3
```

### Any other OpenAI-compatible local server

Use its `/v1` endpoint and the exact model ID returned by `GET /v1/models`:

```bash
export AURA_PROVIDER=local
export AURA_BASE_URL=http://localhost:1234/v1
export AURA_MODEL=exact-model-id
```

**Troubleshooting:** a refused connection means the local server isn't running; an HTTP 404 almost always means `/v1` is missing from `AURA_BASE_URL`.

### OpenAI, Gemini, Anthropic, Groq

```bash
export AURA_PROVIDER=anthropic        # or openai / gemini / groq
export AURA_API_KEY="your-key"
export AURA_MODEL="claude-3-5-sonnet-latest"   # any valid model ID for that provider
```

## Architecture — what each module does

```text
src/god_ai/
├── __init__.py        # Public package surface: GodConfig, configure, heal, do, LLMClient,
│                       # system, the `god` facade object, and `aura = import_module("god_ai.aura")`
├── config.py           # GodConfig dataclass, .env loading, normalization, validation
├── llm.py              # LLMClient — the provider router (OpenAI-compatible, Gemini, Anthropic)
├── llm_handler.py       # LLMHandler — thin LLMClient subclass with a `free_only` convenience flag
├── decorators.py       # @heal — diagnose-then-retry decorator
├── ghost.py            # do() — guarded natural-language-to-Python execution (AST-validated)
├── executor.py         # extract_commands / run_commands / ExecutionResult — confirmation-gated shell
├── command_executor.py # Public re-export of executor.py
├── memory.py           # Memory — SQLite or JSON conversation store
├── system.py           # detect() / SystemSnapshot — read-only, side-effect-free host detection
├── cli.py               # main() — the `god` / `aura` console-script entry point
├── web.py               # create_app() / serve() — optional FastAPI localhost dashboard
├── web_server.py        # Public re-export of web.py
├── static/              # index.html + generated logo PNGs, bundled with the wheel
└── aura/                 # The curated `god_ai.aura` namespace
    ├── __init__.py       # Re-exports everything below under one flat namespace
    ├── config.py         # Facade over ../config.py
    ├── ghost.py           # Facade over ../ghost.py
    ├── heal.py             # Facade over ../decorators.py
    ├── system.py           # Facade over ../system.py (with its own eagerly evaluated `system`)
    ├── agent.py            # agent() — bounded autonomous pytest diagnose/repair loop
    ├── optimize.py         # @optimize — timing + model-suggested speed-up decorator
    ├── parse.py            # parse() — natural language → JSON / Pydantic model
    └── extra.py            # trace_exceptions, auto_patch, exec_sandboxed, eval_expr,
                            # to_pydantic, to_dataclass, benchmark, cost_profiler
```

Root-level files (`main.py`, `config.py`, `llm_handler.py`, `memory_manager.py`, `command_executor.py`, `system_detector.py`, `web_server.py`, `termux_features.py`) are **compatibility shims only** — each simply re-exports the real implementation from `src/god_ai/`, so old scripts written against a pre-packaging layout of this project keep importing successfully.

## CLI reference

Installing the package registers two identical console scripts, `god` and `aura` (both point at `god_ai.cli:main`):

```text
god [--free] [--web] prompt...
aura [--free] [--web] prompt...
```

| Flag | Effect |
|---|---|
| `--web` | Starts the local FastAPI dashboard at `http://127.0.0.1:8000` instead of running a one-shot prompt. |
| `--free` | Forces OpenRouter free-tier routing (appends `:free` to the model ID when the provider is OpenRouter). |
| `prompt...` | The task text. Multiple words are joined with spaces; if omitted (and `--web` isn't set), the CLI prints `--help` and exits. |

```bash
god "find the likely cause of this test failure"
god --free "draft a README section about installation"
god --web
```

What actually happens on a normal `god "..."` call:

1. `configure(free_only=args.free)` resolves the active provider (raising a clear `argparse` error on invalid configuration).
2. The prompt is recorded in a JSON-backed `Memory` under session `GOD_SESSION_ID` (default: `"cli"`).
3. `LLMClient.chat()` is called with a system prompt built from `system_prompt()` (platform constraints — see [System detection](#system-detection)) plus recent conversation history.
4. The reply is pretty-printed as Markdown via `rich` if it's installed, otherwise printed as plain text.
5. Any fenced shell/PowerShell code blocks in the reply are extracted and run **one at a time, only after you type `y`/`yes`** at an `Execute command? [y/N]` prompt. A failing command is automatically handed back to the model for a corrected one-line fix, up to `heal_retries` times.
6. The assistant's reply is appended to the same session's memory.

Generated code is only ever described as "tested" when the CLI actually ran a command and captured its exit code — nothing is presented as verified without an actual execution.

## Python SDK reference

### Configuration API

```python
from god_ai import GodConfig, configure, get_config

settings = configure(provider="openrouter", api_key="your-key", model="openrouter/auto")
current = get_config()          # returns the same process-wide GodConfig
```

- **`configure(**values) -> GodConfig`** — merges keyword arguments over environment variables over defaults, normalizes, validates, and stores the result as the process-wide config. Raises `ValueError` on invalid settings.
- **`get_config() -> GodConfig`** — returns the currently active `GodConfig` without changing it.
- **`GodConfig`** — a frozen dataclass: `provider`, `api_key`, `base_url`, `model`, `request_timeout`, `heal_retries`, `ghost_timeout`, `free_only`. Also exposed identically as `aura.get_config()` / `aura.configure()`.

### Self-healing (`@heal` / `aura.heal`)

```python
from god_ai import heal
# or: from god_ai import aura; @aura.heal

@heal
def parse_port(value: str) -> int:
    return int(value)
```

On an exception, `@heal`:
1. Captures the failing function's source, `repr()` of its arguments, a `repr()` snapshot (truncated to 500 characters) of every local variable across the traceback's frames, and the full formatted traceback.
2. Sends all of that as one prompt to the configured LLM asking for a root-cause diagnosis, and logs the diagnosis at `logging.ERROR` under the `"god_ai"` logger name.
3. Retries the **original** call up to `config.heal_retries` times (default `1`).
4. If every retry still fails, **re-raises the original exception** — a diagnosis is never used to fabricate a fake success, and no source file is ever edited automatically.

If the diagnosis request itself fails (`LLMError`), that's logged as a warning and the retries still proceed.

### Diagnostics — trace and auto-patch

```python
from god_ai import aura

@aura.trace_exceptions
def risky(): ...

@aura.auto_patch
def flaky(): ...
```

- **`aura.trace_exceptions`** — wraps a function; on an exception it sends the formatted traceback to the model for a concise root-cause summary (logged, not returned), then **re-raises** the original exception unchanged.
- **`aura.auto_patch`** — on an exception, asks the model to return a corrected version of the *entire function*, `exec`s that returned source in a fresh namespace, finds the first callable object defined in it, and calls that instead with the original arguments. This is the one decorator in the SDK that executes model-generated code as a real replacement function body — use it only against trusted providers and for functions you're comfortable seeing rewritten at runtime.

### Ghost execution — natural language to Python

```python
from god_ai import aura

context = {"matrix": ..., "vector": ...}
result = aura.do(
    "Create a matrix transform that returns the dot product of matrix and vector, "
    "then normalizes it, and assigns it to result.",
    context=context,
)
```

`aura.do(instruction, context=None)` (also importable as `god_ai.do`):

1. Asks the model for one fenced Python block whose final line assigns to a variable literally named `result`.
2. Parses the extracted code with `ast.parse` — a `SyntaxError` becomes `GhostExecutionError`.
3. Walks the AST and **rejects** the code (again raising `GhostExecutionError`) if it contains any `import`/`from ... import`, or any use of the names/attributes: `__import__`, `eval`, `exec`, `compile`, `open`, `input`, `breakpoint`, `system`, `popen`, `run`.
4. Executes the validated code in a namespace with only a small safe builtins subset (`len`, `str`, `int`, `float`, `bool`, `list`, `dict`, `sum`, `min`, `max`, `sorted`, `range`) plus whatever you passed in `context`.
5. On POSIX systems, a `SIGALRM`-based timeout (`config.ghost_timeout` seconds, default 30) aborts long-running generated code with `GhostExecutionError`. This timeout mechanism is a no-op on Windows, where `signal.SIGALRM` doesn't exist.
6. Returns `namespace["result"]`, or raises `GhostExecutionError` if the code never assigned one.

**AST validation reduces risk but is not a complete sandbox** — run untrusted workloads in a container or a low-privilege process regardless.

### Sandboxed execution and expression evaluation

```python
from god_ai import aura

value = aura.exec_sandboxed("result = sum(x for x in range(10))")
total = aura.eval_expr("1 + 2 * 3")
```

- **`aura.exec_sandboxed(code, context=None, timeout_seconds=15)`** — a general-purpose sibling of `aura.do()` for code *you* wrote (not model-generated). Blocks `import`/`from import` statements and calls/attributes named `eval`, `exec`, `compile`, `open`, `input`, `__import__`, `breakpoint`, `system`, `popen`, `subprocess`, `os`, `shutil`, `pathlib`, or `socket`. The sandbox namespace includes a wider safe builtins set (`abs`, `all`, `any`, `enumerate`, `round`, `set`, `zip`, …) plus the standard-library `math` and `statistics` modules pre-imported for you. Returns `namespace["result"]` if set, otherwise the whole namespace dict. Note: the `timeout_seconds` check happens **after** execution completes (it raises `TimeoutError` retroactively) — it does not interrupt a runaway loop.
- **`aura.eval_expr(expression, context=None)`** — evaluates a single expression with `ast.parse(mode="eval")`, blocking the names `__import__`, `open`, `eval`, `exec`, `compile`. Namespace includes `math` and the same restricted builtins subset.

### Structured parsing

```python
from pydantic import BaseModel
from god_ai import aura

class Person(BaseModel):
    name: str
    age: int

person = aura.parse("Ada Lovelace is 36 years old", Person)
print(person.name, person.age)   # Ada Lovelace 36
```

- **`aura.parse(text, model=None)`** — asks the model to return only valid JSON for the given text. If the raw reply isn't valid JSON, it's sent back to the model once for a repair pass. If `model` is `None`, the parsed JSON (`dict`/`list`) is returned as-is. If `model` is a Pydantic `BaseModel` subclass, `model.model_validate(data)` is used; otherwise `pydantic.TypeAdapter(model).validate_python(data)` handles arbitrary typed containers (e.g. `list[Person]`, `dict[str, int]`).
- **`aura.to_pydantic(data, model)`** — thin wrapper over `model.model_validate(data)` for data you already have as a `dict`/`list` (no model call).
- **`aura.to_dataclass(data, cls)`** — instantiates a `@dataclass` type from a `dict` via `cls(**data)`; raises `TypeError` if `cls` isn't a dataclass.

### Performance tooling

```python
from god_ai import aura

@aura.optimize
def slow_function(): ...

@aura.benchmark
def timed_function(): ...

@aura.cost_profiler
def measured_function(): ...
```

- **`@aura.optimize`** — times every call; if it takes ≥ 0.1s, asks the model for an optimization suggestion and logs it at `INFO` under `"god_ai.optimize"` (never changes behavior or return value).
- **`@aura.benchmark`** — times every call and `print()`s `"{qualname} completed in {elapsed:.4f}s"`.
- **`@aura.cost_profiler`** — times every call and `print()`s an approximate "cost unit" figure (`elapsed_seconds * 1000`), useful as a placeholder proxy for token/compute cost accounting.

### Autonomous agent (`aura.agent`)

```python
from god_ai import aura

result = aura.agent(
    "Fix any failing pytest issues in the workspace while keeping behavior stable.",
    root=Path("."),
    max_iterations=2,
    allow_edits=False,
)
print(result.passed, result.iterations, result.output)
```

`aura.agent(goal, root=None, max_iterations=3, allow_edits=False) -> AgentResult`:

1. Runs `pytest -q` in `root` (defaults to the current working directory).
2. If it passes, returns immediately with `AgentResult(goal, passed=True, iterations, output)`.
3. If it fails, asks the model for a unified diff that would fix it.
4. With `allow_edits=False` (the default), the suggested diff is returned as text inside `AgentResult.output` — **nothing is written to disk**.
5. With `allow_edits=True`, the diff is written to a temporary `.god-ai.patch` file and applied with `patch -p1 --forward --batch`; the loop repeats up to `max_iterations` times. The patch file is always deleted afterward, whether or not it applied successfully.

Editing is opt-in specifically because generated file changes need human review before they're trusted.

### System detection

```python
from god_ai import system            # module-level singleton, computed once at import time
from god_ai import aura
aura.system                          # a second, independently computed singleton in the aura facade
```

`SystemSnapshot` (frozen dataclass): `os_name`, `architecture`, `kernel`, `environment` (`"Termux"` / `"iSH"` / `"Desktop"`), `package_manager`, `shell`, `cpu_count`, `termux_api_available`, plus the properties `is_termux`, `is_ish`, and the methods `as_dict()` and `prompt_constraints()`. Detection is entirely read-only (`platform.*`, `os.getenv`, `shutil.which`) — it never installs anything or shells out. `prompt_constraints()` produces the platform guidance string that both the CLI and the web dashboard prepend to every model request (e.g. "avoid sudo, systemd, desktop GUI packages" on Termux; PowerShell-style guidance on Windows).

### LLM client — the provider router

```python
from god_ai import LLMClient, LLMError, LLMResponse

response: LLMResponse = LLMClient().chat(
    [{"role": "user", "content": "Reply with the active provider name only."}],
    system="You are terse.",
)
print(response.text)
```

`LLMClient(config=None)` normalizes the given (or process-wide) `GodConfig` and dispatches `.chat(messages, system="")` to one of three request shapes based on `config.provider`:

| Providers | Request shape | Default base URL |
|---|---|---|
| `openai`, `local`, `groq`, `openrouter` | OpenAI-compatible `POST /chat/completions` | see table below |
| `gemini` | Google `generateContent` REST call | `https://generativelanguage.googleapis.com/v1beta/models` |
| `anthropic` | Anthropic Messages API (`anthropic-version: 2023-06-01`) | `https://api.anthropic.com/v1` |

Built-in default base URLs (used whenever `base_url` is empty): `openrouter → https://openrouter.ai/api/v1`, `openai → https://api.openai.com/v1`, `groq → https://api.groq.com/openai/v1`, `local → http://localhost:11434/v1`, plus the Gemini and Anthropic URLs above.

**Retries and fallback:**
- Every HTTP request retries up to 3 attempts total with exponential backoff (`2**attempt` seconds) on HTTP `429`/`500`/`502`/`503`/`504`, connection errors, or timeouts.
- If the primary provider call still raises `LLMError`, `.chat()` automatically tries **one fallback provider**: if an `api_key` is configured, the fallback is OpenRouter with `model="openrouter/auto"`; otherwise the fallback is local Ollama (`llama3` at `http://localhost:11434/v1`). If the fallback also fails, both error messages are combined into a single `LLMError`. There is no fallback at all when the primary provider is already `local`.
- `LLMResponse` is a frozen dataclass: `text` (the extracted reply string) and `raw` (the full parsed provider JSON, for callers who need usage/token metadata).
- **`LLMHandler`** (`god_ai.llm_handler.LLMHandler`) is an `LLMClient` subclass kept for compatibility; its only addition is a `free_only: bool` constructor argument that flips `GodConfig.free_only` without you building a new `GodConfig` by hand.

### Conversation memory

```python
from god_ai.memory import Memory

memory = Memory("json")             # or "sqlite" (default)
memory.add("session-id", "user", "hello")
memory.add("session-id", "assistant", "hi there")
print(memory.context("session-id"))       # "user: hello\nassistant: hi there"
recent = memory.recent("session-id", limit=12)
```

`Memory(backend="sqlite", root=None)` stores each message with `session`, `role`, `content`, and a UTC ISO timestamp. The `sqlite` backend writes to `<root>/god_ai.sqlite3`; the `json` backend writes a pretty-printed array to `<root>/conversations.json`. `root` defaults to `./memory` (created automatically). `recent(session, limit=12)` returns the most recent messages for that session in chronological order; `context(session)` joins them into a single `"role: content"` block per line, ready to splice into a system prompt.

### Command execution

```python
from god_ai.executor import extract_commands, run_commands, ExecutionResult

commands = extract_commands(model_reply_text)   # pulls every fenced bash/sh/shell/powershell/pwsh block
results: list[ExecutionResult] = run_commands(model_reply_text, safe=True, retries=3)
```

- **`extract_commands(response)`** — regex-extracts every fenced ```` ```bash ````/```` ```sh ````/```` ```shell ````/```` ```powershell ````/```` ```pwsh ```` block (language tag optional) from a model's text reply.
- **`run_commands(response, safe=True, debug=None, retries=3)`** — for each extracted command: if `safe=True`, prompts `Execute command? [y/N] <command>` on the terminal and skips it (recording `"Skipped by user."`) unless you type `y`/`yes`. Otherwise runs it with `subprocess.run(shell=True, timeout=300)`. On a non-zero exit code, if a `debug` callback was supplied, it's called with `(command, combined_stdout_stderr)` to get a corrected command, and the loop retries up to `retries` times.
- **`ExecutionResult`** (frozen dataclass): `command`, `output` (combined stdout+stderr), `returncode`, `attempts`.

### Web dashboard API

```python
from god_ai.web import create_app, serve
serve()   # equivalent to `god --web`
```

`create_app()` requires `fastapi`, `uvicorn`, and `pydantic` (install with `god-ai[web]`) and raises `RuntimeError` immediately if they're missing. It exposes:

| Method & path | Behavior |
|---|---|
| `GET /` | Serves the bundled `static/index.html` single-page dashboard. |
| `GET /api/health` | Returns `{"status": "ok", "provider": ..., "model": ...}` for the active configuration. |
| `POST /api/chat` | Body: `{"message": str, "session_id": "web", "execute": true}`. Records the message in JSON-backed memory, calls the LLM with the same platform-aware system prompt as the CLI, optionally runs any fenced commands in the reply (with `safe=True`, so it will only execute — the web UI has no interactive TTY prompt, meaning execution effectively requires `execute=false` or a client that pipes confirmation), and returns `{"response": str, "executions": [ExecutionResult, ...]}`. |

`serve()` calls `configure()` and starts `uvicorn.run(create_app(), host="127.0.0.1", port=8000)` — the dashboard is never exposed beyond localhost by default.

## Examples — all 14 runnable files, in full

Every example in `examples/` is reproduced here in full so you can read, copy, and run them without needing to browse the GitHub repository. They're grouped exactly as they exist on disk: the 4 original compatibility examples, then the 10 files added in 1.1.1.

Run any of them from the repository root, e.g. `python examples/03_numpy_matrix_ghost.py`. Each file documents its own optional-dependency requirements in its module docstring where one exists. The Turtle example opens a desktop window and needs a display.

### Original compatibility examples

#### `examples/01_pytorch_healer.py`

```python
"""Self-healing PyTorch shape-mismatch training example.

Run after installing the optional dependencies:
    python -m pip install torch numpy
    python examples/01_pytorch_healer.py
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import torch
from torch import nn

from god_ai import aura

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


class TinyCNN(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(nn.Conv2d(3, 8, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1)))
        self.classifier = nn.Linear(8, 2)

    def forward(self, batch: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(batch).flatten(1))


_attempts = 0


@aura.heal
def train_step(model: nn.Module, batch: torch.Tensor, target: torch.Tensor) -> float:
    """Demonstrate diagnosis of NCHW versus NHWC input and a repaired retry."""
    global _attempts
    _attempts += 1
    if _attempts == 1:
        # Deliberately provide NHWC data to an NCHW convolution.
        model(batch.permute(0, 2, 3, 1))
    else:
        # The retry represents the fix identified by the model diagnosis.
        batch = batch.contiguous()
    prediction = model(batch)
    loss = nn.functional.cross_entropy(prediction, target)
    loss.backward()
    return float(loss.detach())


def main() -> None:
    aura.configure(provider="ollama", model="llama3", heal_retries=1)
    rng = np.random.default_rng(7)
    batch = torch.tensor(rng.normal(size=(4, 3, 16, 16)), dtype=torch.float32)
    target = torch.tensor([0, 1, 0, 1])
    model = TinyCNN()
    try:
        loss = train_step(model, batch, target)
    except RuntimeError as exc:
        print(f"The model diagnosis was logged, but the retry still needs a corrected batch: {exc}")
        fixed_batch = batch.contiguous()
        loss = float(nn.functional.cross_entropy(model(fixed_batch), target).detach())
    print(f"NCHW batch shape: {tuple(batch.shape)}; training loss: {loss:.4f}")


if __name__ == "__main__":
    main()
```

#### `examples/02_fastapi_agent.py`

```python
"""Fetch text, parse it into Pydantic records, and expose a FastAPI endpoint.

Run:
    python -m pip install fastapi uvicorn requests pydantic
    python examples/02_fastapi_agent.py
"""

from __future__ import annotations

import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from god_ai import aura


class Article(BaseModel):
    title: str
    summary: str
    source_url: str


app = FastAPI(title="God AI Structured Article API")
_articles: list[Article] = []


def fetch_text(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.text[:12000]


def structure_article(raw: str, source_url: str) -> Article:
    parsed = aura.parse(
        f"Extract a short title and summary from this web text:\n{raw}",
        Article,
    )
    return parsed.model_copy(update={"source_url": source_url})


@app.get("/articles", response_model=list[Article])
def articles() -> list[Article]:
    return _articles


@app.post("/articles/scrape", response_model=Article)
def scrape(url: str) -> Article:
    try:
        article = structure_article(fetch_text(url), url)
    except (requests.RequestException, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    _articles.append(article)
    return article


def main() -> None:
    import uvicorn

    aura.configure(
        provider=os.getenv("AURA_PROVIDER", "ollama"),
        model=os.getenv("AURA_MODEL", "llama3"),
        base_url=os.getenv("AURA_BASE_URL", "http://localhost:11434/v1"),
    )
    uvicorn.run(app, host="127.0.0.1", port=int(os.getenv("PORT", "8001")))


if __name__ == "__main__":
    main()
```

#### `examples/03_resilient_microservice.py`

```python
"""Matrix service with model-provider fallback and NumPy processing.

Run:
    python -m pip install numpy
    python examples/03_resilient_microservice.py
"""

from __future__ import annotations

import logging
import os

import numpy as np

from god_ai import aura
from god_ai.llm import LLMClient, LLMError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def matrix_transform(matrix: np.ndarray) -> np.ndarray:
    """Use NumPy locally; the SDK remains available for model-assisted plans."""
    centered = matrix - matrix.mean(axis=0, keepdims=True)
    covariance = centered.T @ centered / max(1, matrix.shape[0] - 1)
    return covariance


def choose_provider() -> None:
    try:
        client = LLMClient()
        client.chat([{"role": "user", "content": "Reply with the active provider name only."}])
        logging.info("Cloud/local provider responded successfully")
    except LLMError as exc:
        logging.warning("All configured providers failed: %s", exc)


def main() -> None:
    aura.configure(
        provider=os.getenv("AURA_PROVIDER", "openrouter"),
        api_key=os.getenv("AURA_API_KEY", ""),
        model=os.getenv("AURA_MODEL", "openrouter/auto"),
        base_url=os.getenv("AURA_BASE_URL", ""),
    )
    choose_provider()
    data = np.arange(12, dtype=float).reshape(4, 3)
    covariance = matrix_transform(data)
    print("Input matrix:\n", data)
    print("Covariance matrix:\n", covariance)
    print("Configured fallback chain: primary -> OpenRouter -> Ollama")


if __name__ == "__main__":
    main()
```

#### `examples/04_terminal_scaffolder.py`

```python
"""Create and serve a responsive dashboard after a confirmation-gated prompt.

Run:
    python examples/04_terminal_scaffolder.py
"""

from __future__ import annotations

import http.server
import subprocess
import socketserver
from pathlib import Path


HTML = """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>God AI Dashboard</title><link rel='stylesheet' href='style.css'></head><body><main><p class='eyebrow'>God AI</p><h1>Operations dashboard</h1><section class='grid'><article><strong>Revenue</strong><b>$42,840</b><span>+12.4%</span></article><article><strong>Active users</strong><b>8,294</b><span>+8.1%</span></article><article><strong>System status</strong><b>Healthy</b><span>All services online</span></article></section><button id='refresh'>Refresh metrics</button><p id='status'></p></main><script src='app.js'></script></body></html>"""
CSS = """*{box-sizing:border-box}body{margin:0;background:#101827;color:#edf2f7;font:16px system-ui,sans-serif}main{max-width:960px;margin:0 auto;padding:12vh 1.5rem}.eyebrow{color:#67e8f9;text-transform:uppercase;letter-spacing:.2em;font-size:.75rem}h1{font-size:clamp(2.4rem,7vw,5rem);margin:.2rem 0 3rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem}.grid article{background:#182438;border:1px solid #334155;border-radius:14px;padding:1.25rem;display:grid;gap:.7rem}.grid b{font-size:2rem}.grid span{color:#67e8f9}button{margin-top:2rem;padding:.8rem 1rem;border:0;border-radius:8px;background:#67e8f9;color:#082f49;font-weight:700}"""
JS = """document.querySelector('#refresh').addEventListener('click',()=>{document.querySelector('#status').textContent='Metrics refreshed at '+new Date().toLocaleTimeString()})"""


def scaffold(root: Path) -> Path:
    project = root / "god-dashboard"
    project.mkdir(parents=True, exist_ok=True)
    (project / "index.html").write_text(HTML, encoding="utf-8")
    (project / "style.css").write_text(CSS, encoding="utf-8")
    (project / "app.js").write_text(JS, encoding="utf-8")
    return project


def main() -> None:
    instruction = "Create a responsive dashboard using Tailwind CSS and JavaScript"
    print(f"Requested: {instruction}")
    project = scaffold(Path.cwd())
    command = "python -m http.server 8765"
    if input(f"Run `{command}` in {project}? [Y/n] ").strip().lower() not in {"", "y", "yes"}:
        print(f"Dashboard files are in {project}; server launch skipped.")
        return
    process = subprocess.Popen(command.split(), cwd=project)
    print(f"Dashboard files are in {project}")
    print("Serving at http://127.0.0.1:8765; press Ctrl+C to stop.")
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()


if __name__ == "__main__":
    main()
```

### 1.1.1 extension examples

#### `examples/01_pytorch_neural_healer.py`

```python
from __future__ import annotations

import numpy as np
import torch
from torch import nn

from god_ai import aura


@aura.heal
@aura.trace_exceptions
def train_healer_example(batch_size: int = 8):
    x = np.random.randn(batch_size, 4).astype(np.float32)
    y = np.random.randn(batch_size, 2).astype(np.float32)
    model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 2),
    )
    loss_fn = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    inputs = torch.tensor(x)
    target = torch.tensor(y)
    for _ in range(4):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_fn(outputs, target)
        loss.backward()
        optimizer.step()

    if outputs.shape != target.shape:
        raise ValueError(f"Tensor shape mismatch: {outputs.shape} vs {target.shape}")

    return {"loss": float(loss.item()), "shape": list(outputs.shape)}


if __name__ == "__main__":
    result = train_healer_example()
    print("pytorch neural healer:", result)
```

#### `examples/02_tensorflow_model_optimizer.py`

```python
from __future__ import annotations

import numpy as np

try:
    import tensorflow as tf
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Install the aura extra: pip install 'god-ai[aura]' or install tensorflow") from exc

from god_ai import aura


@aura.optimize
@aura.cost_profiler
def build_and_train_classifier():
    (x_train, y_train), _ = tf.keras.datasets.mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    y_train = tf.keras.utils.to_categorical(y_train, 10)

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input((28, 28)),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    history = model.fit(x_train[:2048], y_train[:2048], epochs=2, batch_size=64, verbose=0)
    return {"accuracy": float(np.max(history.history["accuracy"])), "loss": float(np.min(history.history["loss"]))}


if __name__ == "__main__":
    print(build_and_train_classifier())
```

#### `examples/03_numpy_matrix_ghost.py`

```python
from __future__ import annotations

import numpy as np

from god_ai import aura


context = {
    "matrix": np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float64),
    "vector": np.array([5.0, 6.0], dtype=np.float64),
}


result = aura.do(
    "Create a matrix transform that returns the dot product of matrix and vector, then normalizes it, and assigns it to result.",
    context=context,
)

print("matrix ghost result:", result)


@aura.benchmark
def matrix_transform(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    projected = matrix @ vector
    normalized = projected / np.linalg.norm(projected)
    return normalized


if __name__ == "__main__":
    sample = np.array([[2.0, 1.0], [0.5, 3.0]], dtype=np.float64)
    vector = np.array([1.0, -1.0], dtype=np.float64)
    print(matrix_transform(sample, vector))
```

#### `examples/04_fastapi_unstructured_parser.py`

```python
"""Parse unstructured text into a validated Pydantic record and serve it over FastAPI.

Run:
    python -m pip install fastapi uvicorn pydantic
    python examples/04_fastapi_unstructured_parser.py
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from god_ai import aura


class ExtractedRecord(BaseModel):
    title: str
    summary: str
    entities: list[str] = Field(default_factory=list)
    priority: str = "medium"


text_blob = """
Acme Launches Edge Router
The team completed beta testing for the new edge router in North America.
Key stakeholders: product, infra, and security. This is a high-priority rollout.
"""


try:
    from fastapi import FastAPI

    app = FastAPI(title="Aura Unstructured Parser API")

    @app.get("/parse")
    def parse_endpoint() -> dict[str, object]:
        parsed = aura.parse(text_blob, ExtractedRecord)
        return parsed.model_dump()
except ImportError:  # pragma: no cover
    app = None


if __name__ == "__main__":
    if app is None:
        print(aura.parse(text_blob, ExtractedRecord))
    else:
        import uvicorn

        uvicorn.run(app, host="127.0.0.1", port=8000)
```

> **Fixed in this documentation pass:** earlier revisions of this file referenced `FastAPI` one line before importing it, which raised `NameError` unconditionally. The `app = FastAPI(...)` construction now happens only inside the `try` block, after the import — exactly as `04_fastapi_unstructured_parser.py` ships from this point on.

#### `examples/05_flask_resilient_microservice.py`

```python
from __future__ import annotations

import os
from typing import Any

from flask import Flask, jsonify, request

from god_ai import aura

app = Flask(__name__)

DEFAULT_ENDPOINT = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "provider": "local-ollama", "endpoint": DEFAULT_ENDPOINT}


@app.post("/infer")
def infer() -> Any:
    payload = request.get_json(silent=True) or {}
    prompt = str(payload.get("prompt", "Explain the system health in one sentence."))
    try:
        result = aura.do(
            "Return a one-sentence summary of the requested prompt and store it in result.",
            context={"prompt": prompt},
        )
        return jsonify({"response": result, "fallback": False})
    except Exception:
        return jsonify({"response": f"Fall back: {prompt} is being processed by the resilience layer.", "fallback": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

#### `examples/06_turtle_ai_generative_art.py`

```python
from __future__ import annotations

import turtle

from god_ai import aura


def generate_art(command: str) -> None:
    screen = turtle.Screen()
    screen.title("Aura Generative Art")
    artist = turtle.Turtle()
    artist.speed(0)
    artist.penup()
    artist.goto(-150, 0)
    artist.pendown()

    for index in range(12):
        artist.forward(60)
        artist.left(30)
        artist.circle(25)

    artist.hideturtle()
    screen.onkey(lambda: screen.bye(), "q")
    screen.listen()
    screen.mainloop()


if __name__ == "__main__":
    generate_art("Create a radial geometric pattern")
```

#### `examples/07_autonomous_pytest_bot.py`

```python
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from god_ai import aura


def run_bot() -> None:
    workspace = Path(__file__).resolve().parent.parent
    result = aura.agent(
        "Fix any failing pytest issues in the workspace while keeping behavior stable.",
        root=workspace,
        max_iterations=2,
        allow_edits=False,
    )
    print(result.output)
    print(f"passed={result.passed} iterations={result.iterations}")


if __name__ == "__main__":
    run_bot()
```

#### `examples/08_data_pipeline_transformer.py`

```python
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from god_ai import aura


def clean_records(data: list[dict[str, object]]) -> list[dict[str, object]]:
    df = pd.DataFrame(data)
    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].astype(str).str.strip()
    df = df.replace({"": np.nan, None: np.nan})
    df = df.dropna(how="any")
    return df.to_dict(orient="records")


sample = [{
    "id": 1,
    "name": " Alpha ",
    "score": "88",
    "country": "US",
}, {
    "id": 2,
    "name": "Beta",
    "score": "",
    "country": "CA",
}, {
    "id": 3,
    "name": "Gamma",
    "score": "91",
    "country": "US",
}]

if __name__ == "__main__":
    cleaned = clean_records(sample)
    print(json.dumps(cleaned, indent=2))
    parsed = aura.parse(json.dumps(cleaned), None)
    print(parsed)
```

#### `examples/09_multimodal_vision_generator.py`

```python
from __future__ import annotations

import json
import os

from god_ai import aura


def build_boilerplate_from_image_description(prompt: str) -> dict[str, object]:
    payload = {
        "summary": prompt,
        "language": "python",
        "framework": "fastapi",
        "components": ["routes", "models", "tests"],
    }
    parsed = aura.parse(json.dumps(payload), None)
    return parsed if isinstance(parsed, dict) else {"summary": prompt}


if __name__ == "__main__":
    print(build_boilerplate_from_image_description("A dashboard with a sidebar, chart panel, and API route definitions."))
```

#### `examples/10_terminal_fullstack_scaffolder.py`

```python
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from god_ai import aura


def scaffold_project(project_name: str, root: Path | None = None) -> dict[str, object]:
    target = (root or Path.cwd()) / project_name
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text("<!doctype html><html><body><h1>Hello from God AI</h1></body></html>", encoding="utf-8")
    (target / "styles.css").write_text("body{font-family:sans-serif;display:grid;place-items:center;height:100vh;}", encoding="utf-8")
    (target / "app.js").write_text("document.body.insertAdjacentHTML('beforeend', '<p>Generated by God AI</p>');", encoding="utf-8")
    return {"path": str(target), "files": ["index.html", "styles.css", "app.js"]}


if __name__ == "__main__":
    project = scaffold_project("demo_web_app", Path(__file__).resolve().parent)
    print(json.dumps(project, indent=2))
```

## Documentation portal

Serve the static portal locally with:

```bash
python -m http.server 8080 --directory docs
```

Then open `http://127.0.0.1:8080`. The portal (`docs/index.html`, `docs/styles.css`, `docs/app.js`) is a single static site — no build step, no bundler, no server-side code — so it deploys as-is to GitHub Pages from the `docs/` directory. It contains: a searchable full API reference for every function documented above, a provider setup wizard for all six providers, and every one of the 14 example files embedded and copy-able directly on the page (so browsing the GitHub repository is never required just to read an example).

## Development and verification

```bash
git clone https://github.com/ayushgiriai21-cmd/God.git
cd God
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
pytest -q
python -m py_compile $(find src examples scripts -name '*.py')
git diff --check
```

Build and validate distributions:

```bash
python -m pip install build twine
python scripts/process_logo.py
python -m build
python -m twine check dist/*
```

`scripts/process_logo.py` rasterizes `assets/logo.svg` (via `cairosvg`) into `logo_255x255.png`, `favicon_64x64.png`, and `badge_32x32.png`, writing identical copies into both `docs/assets/` and `src/god_ai/static/` so the PyPI README, the GitHub Pages portal, and the bundled web dashboard all show the same artwork.

## Release process

**v1.1.1 is tagged and published to PyPI.** Create the corresponding GitHub release from the existing tag, then use the same tag-triggered workflow for future version bumps.

The workflow `.github/workflows/publish.yml` triggers on any pushed tag matching `v*`. It checks out the source, sets up Python 3.12, installs `build`, `twine`, `pillow`, and `cairosvg`, regenerates the logo assets, builds the sdist and wheel with `python -m build`, validates both with `python -m twine check dist/*`, and publishes them to PyPI via `pypa/gh-action-pypi-publish` using the `PYPI_API_TOKEN` repository secret.

```bash
# Bump the version in pyproject.toml and src/god_ai/__init__.py first, then:
git add .
git commit -m "feat: release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

Never commit the PyPI token. The version and tag must be unique on PyPI — twine/PyPI will reject a re-upload of an already-published version.

## Project structure

```text
God/
├── assets/                 # source logo artwork (logo.svg)
├── docs/                   # static GitHub Pages documentation portal
│   ├── assets/              # generated logo PNGs for the portal
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── examples/               # 14 runnable SDK examples (see above, in full)
├── scripts/
│   └── process_logo.py      # regenerates all logo PNG sizes from the SVG source
├── src/god_ai/             # the installable `god_ai` package (see Architecture)
├── tests/
│   └── test_v110_contract.py   # version/export/asset contract tests
├── static/                 # standalone copy of the dashboard shell (root-level compatibility)
├── main.py, config.py, llm_handler.py, memory_manager.py,
│   command_executor.py, system_detector.py, termux_features.py,
│   web_server.py            # backward-compatible re-export shims over src/god_ai/
├── pyproject.toml          # package metadata, dependencies, and extras
├── setup.py                # legacy setuptools entry point (config lives in pyproject.toml)
├── requirements.txt        # flat pinning reference for the full feature set
└── .github/workflows/
    └── publish.yml          # tag-triggered build, validate, and PyPI publish
```

## Credits

- **Author / maintainer:** [Ayush Giri](https://github.com/ayushgiriai21-cmd) ([@ayushgiriai21-cmd](https://pypi.org/user/ayushgiriai21-cmd/) on PyPI) — repository owner, PyPI package maintainer, and copyright holder per [`LICENSE`](LICENSE).
- **Package author (per `pyproject.toml`):** God AI Contributors.
- **Repository:** [github.com/ayushgiriai21-cmd/God](https://github.com/ayushgiriai21-cmd/God)

This is the complete attribution information present in the project's own files (`LICENSE`, `pyproject.toml`, and the PyPI project page). If there are additional contributors you'd like credited by name or role, add them here.

## License

God AI is available under the MIT License. See [LICENSE](LICENSE).
