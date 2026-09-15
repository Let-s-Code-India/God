# God AI / AURA 1.0.0

<p align="center"><strong>A confirmation-gated AI terminal assistant and a typed Python automation SDK.</strong></p>

<p align="center"><a href="https://pypi.org/project/god-ai/"><img src="https://img.shields.io/pypi/v/god-ai.svg" alt="PyPI"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a> <img src="https://img.shields.io/badge/python-3.9%2B-yellow.svg" alt="Python 3.9+"></p>

[Open the interactive documentation portal](https://ayushgiriai21-cmd.github.io/God/) or continue here for the complete setup guide.

God AI has two faces. The `god` and `aura` commands help you work from a terminal, while `from god_ai import aura` gives Python developers configuration, self-healing diagnostics, structured parsing, guarded dynamic execution, optimization suggestions, and a bounded test agent.

> Safety default: model-generated terminal commands ask for confirmation. `aura.do()` validates generated Python but is not a security sandbox. Use a disposable workspace for experiments.

## Contents

- [Five-Minute Setup](#five-minute-setup)
- [Providers and Environment Variables](#providers-and-environment-variables)
- [Local LLMs](#local-llms)
- [CLI](#cli)
- [Python SDK](#python-sdk)
- [Real-World Examples](#real-world-examples)
- [Device Setup](#device-setup)
- [Architecture and Reliability](#architecture-and-reliability)
- [Testing and Development](#testing-and-development)
- [PyPI Release](#pypi-release)

## Five-Minute Setup

### 1. Open a terminal

In VS Code choose **Terminal > New Terminal**. On macOS or Linux open Terminal. On Windows open PowerShell. You do not need to understand Python yet; copy one command at a time.

### 2. Install Python

Use Python 3.9 or newer. Python 3.11 or 3.12 is recommended.

- Windows: download Python from [python.org](https://www.python.org/downloads/windows/) and select **Add Python to PATH** during installation.
- macOS: install from [python.org](https://www.python.org/downloads/macos/) or run `brew install python`.
- Ubuntu/Debian: run `sudo apt update && sudo apt install -y python3 python3-pip python3-venv`.
- Termux: run `pkg update && pkg install python git`.
- iSH: run `apk update && apk add python3 py3-pip git`.

Check it:

```sh
python --version
```

If that command fails on macOS/Linux, try `python3 --version`. If it fails on Windows, try `py --version`.

### 3. Install God AI

```sh
python -m pip install --upgrade god-ai
```

Windows alternative:

```powershell
py -m pip install --upgrade god-ai
```

Check the command:

```sh
god --help
aura --help
```

Both commands run the same assistant.

### 4. Choose a provider

#### Free OpenRouter key

Open [openrouter.ai/keys](https://openrouter.ai/keys), create an account, create a key, and set it in your terminal.

Bash, Zsh, macOS, Linux, Termux, or iSH:

```sh
export AURA_PROVIDER=openrouter
export AURA_API_KEY="your-key-here"
export AURA_MODEL=openrouter/auto
```

PowerShell:

```powershell
$env:AURA_PROVIDER="openrouter"
$env:AURA_API_KEY="your-key-here"
$env:AURA_MODEL="openrouter/auto"
```

Command Prompt:

```bat
set AURA_PROVIDER=openrouter
set AURA_API_KEY=your-key-here
set AURA_MODEL=openrouter/auto
```

Try the free route:

```sh
god --free "Reply with exactly: God AI is connected"
```

Other provider key pages:

| Provider | Key or account page | Provider value |
| --- | --- | --- |
| OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) | `openrouter` |
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/) | `gemini` |
| Groq | [console.groq.com](https://console.groq.com/) | `groq` |
| OpenAI | [platform.openai.com](https://platform.openai.com/) | `openai` |
| Anthropic | [console.anthropic.com](https://console.anthropic.com/) | `anthropic` |

Do not paste a key into a public repository, issue, screenshot, or chat transcript.

### 5. Ask your first question

```sh
god "explain the files in this folder"
god "write a Python script that says hello"
god "create a responsive dashboard and tell me how to run it"
```

When a response contains a shell command, God AI prints a confirmation prompt. Type `y` or `yes` to run it. Press Enter to skip it.

## Providers and Environment Variables

You can configure once in a `.env` file in your project directory. Create a file named exactly `.env`:

```dotenv
AURA_PROVIDER=openrouter
AURA_API_KEY=replace-with-your-key
AURA_MODEL=openrouter/auto
AURA_BASE_URL=https://openrouter.ai/api/v1
AURA_FREE_ONLY=false
AURA_REQUEST_TIMEOUT=120
AURA_HEAL_RETRIES=1
AURA_GHOST_TIMEOUT=30
```

For Ollama:

```dotenv
AURA_PROVIDER=ollama
AURA_API_KEY=
AURA_BASE_URL=http://localhost:11434/v1
AURA_MODEL=llama3
```

For LM Studio:

```dotenv
AURA_PROVIDER=local
AURA_API_KEY=
AURA_BASE_URL=http://localhost:1234/v1
AURA_MODEL=the-exact-model-id
```

Environment variables override `.env` values. `aura.configure(...)` values override environment values for the current Python process.

| Variable | Meaning |
| --- | --- |
| `AURA_PROVIDER` | `openrouter`, `openai`, `gemini`, `anthropic`, `groq`, `ollama`, or `local`. |
| `AURA_API_KEY` | Cloud provider credential. Empty for local models. |
| `AURA_BASE_URL` | Custom endpoint. OpenAI-compatible endpoints normally end in `/v1`. |
| `AURA_MODEL` | Model identifier. OpenRouter defaults to `openrouter/auto`; local fallback uses `llama3`. |
| `AURA_FREE_ONLY` | Set `true` to append `:free` to eligible OpenRouter model IDs. |
| `AURA_REQUEST_TIMEOUT` | HTTP timeout in seconds. |
| `AURA_HEAL_RETRIES` | Number of decorator retries. |
| `AURA_GHOST_TIMEOUT` | Maximum seconds for generated in-memory code. |

### Provider fallback

The handler retries HTTP 429, 500, 502, 503, and 504 responses with exponential backoff. If the primary provider still fails, it tries OpenRouter when a key exists, otherwise it tries local Ollama at `http://localhost:11434/v1`. A local provider does not recurse into another fallback.

## Local LLMs

### Ollama

Download Ollama from [ollama.com](https://ollama.com/). Then:

```sh
ollama pull llama3
ollama run llama3
curl http://localhost:11434/api/tags
curl http://localhost:11434/v1/models
```

Connect the CLI:

```sh
export AURA_PROVIDER=ollama
export AURA_BASE_URL=http://localhost:11434/v1
export AURA_MODEL=llama3
god "Reply with exactly: local model connected"
```

Connect Python:

```python
from god_ai import aura

aura.configure(
    provider="ollama",
    base_url="http://localhost:11434/v1",
    model="llama3",
)
```

The first `ollama run` downloads the model. Use a smaller model on a phone or low-memory computer.

### LM Studio

Download [LM Studio](https://lmstudio.ai/), download a model, load it, open **Local Server**, and click **Start Server**. Check its exact model ID:

```sh
curl http://localhost:1234/v1/models
```

Configure it:

```sh
export AURA_PROVIDER=local
export AURA_BASE_URL=http://localhost:1234/v1
export AURA_MODEL=exact-id-from-v1-models
god "Reply with exactly: LM Studio connected"
```

Troubleshooting:

- `Connection refused`: start the local server.
- `404`: include `/v1` in the base URL.
- `model not found`: use the ID returned by `/v1/models`, not the display name.
- slow response: use a smaller quantized model or increase `AURA_REQUEST_TIMEOUT`.

## CLI

```text
god [--free] [--web] prompt...
aura [--free] [--web] prompt...
```

Examples:

```sh
god "find the likely cause of this test failure"
god --free "draft a README section about installation"
god --web
```

`--web` starts the optional localhost interface at `http://127.0.0.1:8000`. The CLI is intentionally confirmation-gated. It does not claim that generated code has been tested unless it actually ran a command and captured the result.

## Python SDK

### Configure

```python
from god_ai import aura

settings = aura.configure(
    provider="openrouter",
    api_key="your-key",
    model="openrouter/auto",
    free_only=True,
    request_timeout=60,
    heal_retries=2,
    ghost_timeout=10,
)
print(settings.provider, settings.model)
```

### `@aura.heal`

The decorator captures function source, positional arguments, keyword arguments, locals available in the traceback, and the full traceback for model diagnosis. It logs the diagnosis, retries the original function, and re-raises the original exception if the retry fails.

```python
import logging
from god_ai import aura

logging.basicConfig(level=logging.INFO)
aura.configure(provider="ollama", model="llama3", heal_retries=1)

@aura.heal
def parse_port(value: str) -> int:
    return int(value)

print(parse_port("8000"))
```

The decorator does not silently edit source files. A diagnosis is guidance for a developer.

### `aura.do()`

The ghost runtime asks for Python that assigns a result to `result`, parses it with `ast`, rejects imports, `eval`, `exec`, filesystem access, process access, and dynamic code, and runs it with a small builtins allowlist.

```python
from god_ai import aura

aura.configure(provider="ollama", model="llama3")
answer = aura.do(
    "Return the average and maximum",
    context={"values": [3, 8, 5]},
)
print(answer)
```

The execution has a configurable time limit. AST validation reduces risk but cannot make Python a complete security sandbox. Run in a container or low-privilege user for untrusted workloads.

### `aura.agent()`

The agent runs `python -m pytest -q` in a selected root, sends failures to the configured model, and repeats up to `max_iterations`. It only applies unified diffs when `allow_edits=True`.

```python
from pathlib import Path
from god_ai import aura

result = aura.agent(
    "Fix the failing unit tests",
    root=Path("."),
    max_iterations=3,
    allow_edits=False,
)
print(result.passed)
print(result.output)
```

Use `allow_edits=True` only on a branch or disposable workspace. Inspect `git diff` after each run.

### `@aura.optimize`

Calls taking at least 100 milliseconds get a model-assisted optimization suggestion in the `god_ai.optimize` logger.

```python
from god_ai import aura

@aura.optimize
def expensive_operation(values):
    return sorted(values)
```

The decorator does not replace the function automatically; it measures first and leaves the engineering decision to you.

### `aura.parse()`

The parser asks the model for valid JSON, removes a fenced wrapper if present, repairs can be retried by the provider fallback path, and validates with Pydantic when a model class is supplied.

```python
from pydantic import BaseModel
from god_ai import aura

class Person(BaseModel):
    name: str
    age: int

person = aura.parse("Ada Lovelace is 36 years old", Person)
print(person.name, person.age)
```

Without a model, the return value is a Python dictionary or list.

### `aura.system`

```python
from god_ai import aura

print(aura.system.os_name)
print(aura.system.package_manager)
print(aura.system.is_termux)
print(aura.system.is_ish)
print(aura.system.as_dict())
```

Detection is read-only and does not install packages or execute commands.

## Real-World Examples

Install the optional example dependencies:

```sh
python -m pip install "god-ai[examples]"
```

### 1. Self-healing PyTorch pipeline

File: `examples/01_pytorch_healer.py`

```sh
python examples/01_pytorch_healer.py
```

The example builds a tiny convolutional network expecting NCHW tensors with shape `N x C x H x W`, deliberately presents NHWC data on the first call, and logs the traceback and diagnosis through `@aura.heal`. The retry uses a contiguous corrected batch and completes a real cross-entropy calculation. NumPy generates deterministic input data and PyTorch performs the forward/backward pass.

### 2. FastAPI scraper and structured API

File: `examples/02_fastapi_agent.py`

```sh
python examples/02_fastapi_agent.py
```

The server exposes `GET /articles` and `POST /articles/scrape?url=...`. `requests` downloads text, `aura.parse()` asks the configured model for JSON, and Pydantic validates `Article(title, summary, source_url)` before the object is stored. This example requires a running model because natural-language extraction is intentionally delegated to Aura.

### 3. Resilient matrix microservice core

File: `examples/03_resilient_microservice.py`

```sh
python examples/03_resilient_microservice.py
```

The service performs a real NumPy covariance operation and probes the configured cloud/local provider. The shared client retries transient failures and falls back from cloud to OpenRouter or Ollama. This separation means numerical work can continue locally even when an LLM network call is unavailable.

### 4. Confirmation-gated dashboard scaffolder

File: `examples/04_terminal_scaffolder.py`

```sh
python examples/04_terminal_scaffolder.py
```

The example accepts the intent “Create a responsive dashboard using Tailwind CSS and JavaScript”, creates `god-dashboard/index.html`, `style.css`, and `app.js`, and starts a local Python HTTP server only after confirmation. Visit `http://127.0.0.1:8765`.

## Device Setup

| Device | Commands |
| --- | --- |
| Windows PowerShell | `py -m pip install god-ai` |
| macOS | `python3 -m pip install god-ai` |
| Linux | `python3 -m pip install god-ai` |
| Android Termux | `pkg update && pkg install python git && python -m pip install god-ai` |
| iPhone/iPad iSH | `apk update && apk add python3 py3-pip git && python3 -m pip install --break-system-packages god-ai` |

Termux uses `pkg`; iSH uses Alpine `apk`. Avoid assumptions about `sudo`, `systemd`, GNU-only flags, or desktop packages on mobile devices. Prefer JSON or small local models when device storage or memory is limited.

## Architecture and Reliability

```text
CLI / Python SDK
       |
configuration + system detector
       |
provider client -- retry 429/5xx --> primary provider
       |                         \--> OpenRouter or Ollama fallback
       |
heal / parse / do / agent / optimize
       |
confirmation-gated command executor and optional web UI
```

The source uses a `src/` package layout and PEP 621 metadata. HTTP transport uses the standard library so the base provider path remains lightweight. Cloud SDK dependencies are declared for ecosystem compatibility, while routing and errors remain explicit.

## Testing and Development

From a source checkout:

```sh
git clone https://github.com/ayushgiriai21-cmd/God.git
cd God
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m py_compile $(find src -name '*.py')
python -m god_ai.cli --help
python -c "from god_ai import aura; print(aura.system.as_dict())"
git diff --check
```

Build distributions:

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
```

Run the portal locally:

```sh
python -m http.server 8080 --directory docs
```

Open `http://127.0.0.1:8080`.

## PyPI Release

The workflow `.github/workflows/publish.yml` runs for tags matching `v*`, builds both an sdist and wheel, validates them with Twine, and publishes using `PYPI_API_TOKEN`.

For the requested 1.0.0 release sequence:

```sh
git add .
git commit -m "feat: 100x enterprise release v1.0.0 - PyTorch/NumPy real projects, deep web docs, and PyPI auto-publish"
ggit tag v1.0.0
git push origin main --tags
```

Create the repository secret at GitHub **Settings > Secrets and variables > Actions**:

```text
Name: PYPI_API_TOKEN
Value: your PyPI token
```

Never commit the token. The tag must be unique on PyPI; if version `1.0.0` is already published, increment the package version before creating a new tag.

## License

God AI is available under the MIT License. See [LICENSE](LICENSE).
