# God AI / Aura

<p align="center"><strong>A hybrid AI assistant for your terminal and your Python programs.</strong></p>

<p align="center">
<a href="https://pypi.org/project/god-ai/"><img src="https://img.shields.io/pypi/v/god-ai.svg" alt="PyPI"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
<img src="https://img.shields.io/badge/python-3.9%2B-yellow.svg" alt="Python 3.9+"></p>

God AI gives you two interfaces to the same provider and system-detection engine. Type `god "your task"` or import `aura` to add model-assisted healing, parsing, optimization, ghost execution, and test-driven development to Python code.

> Version 1.0.0 is designed for safe experimentation. Terminal commands require confirmation, and generated Python is guarded but is not a security sandbox.

## 5-Minute Quick Start

### Step 1: Open a terminal

- **VS Code:** open VS Code, choose **Terminal > New Terminal**, and run the commands below.
- **macOS/Linux:** open Terminal.
- **Windows:** open PowerShell.

### Step 2: Install God AI

```sh
python -m pip install god-ai
```

Check that it works:

```sh
god --help
```

On Windows, use `py -m pip install god-ai` if `python` is not recognized.

### Step 3: Choose a model

You can use a free OpenRouter route or a local model. The local option keeps requests on your computer after download.

#### Free OpenRouter option

1. Create an account at [openrouter.ai](https://openrouter.ai/).
2. Create an API key in your dashboard.
3. Set it in your terminal.

macOS/Linux/Termux/iSH:

```sh
export AURA_PROVIDER=openrouter
export AURA_API_KEY="paste-your-key-here"
export AURA_MODEL=openrouter/auto
```

Windows PowerShell:

```powershell
$env:AURA_PROVIDER="openrouter"
$env:AURA_API_KEY="paste-your-key-here"
$env:AURA_MODEL="openrouter/auto"
```

Run a free-tier request:

```sh
god --free "Reply with exactly: God AI is connected"
```

The key is not stored by God AI unless you put it in a `.env` file. Never commit that file.

#### Local Ollama option

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Download and run a model:

```sh
ollama run llama3
```

3. Configure God AI:

```sh
export AURA_PROVIDER=ollama
export AURA_BASE_URL=http://localhost:11434/v1
export AURA_MODEL=llama3
god "Reply with exactly: local model connected"
```

If no OpenRouter key is configured, God AI automatically falls back to local Ollama at `http://localhost:11434/v1`.

## What Is God AI?

The `god` and `aura` commands are autonomous terminal assistants. They can inspect a project, explain errors, write files, propose websites, and return shell commands; every command asks for `[Y/n]` confirmation before it runs.

The `aura` Python package is the developer SDK:

```python
from god_ai import aura

aura.configure(provider="ollama", model="llama3")
print(aura.system.os_name)
```

## Terminal Assistant

```sh
god "explain the files in this project"
god "write a Python script that converts CSV to JSON"
god "create an HTML website and tell me how to host it"
aura --free "suggest a test plan for this project"
```

When the model returns a fenced shell command, God AI displays it and asks for approval. Type `y` to run it or press Enter to skip it. The command executor captures output and can ask the model for a repair after a failure.

For the localhost browser interface:

```sh
god --web
```

Open `http://127.0.0.1:8000`.

## Python SDK

### Configuration

```python
from god_ai import aura

# OpenRouter automatic routing.
aura.configure(
    provider="openrouter",
    api_key="your-key",
    model="openrouter/auto",
)

# Free-tier routing.
aura.configure(
    provider="openrouter",
    api_key="your-key",
    free_only=True,
)

# Ollama or LM Studio.
aura.configure(
    provider="ollama",
    base_url="http://localhost:11434/v1",
    model="llama3",
)
```

Supported providers are OpenRouter, OpenAI, Gemini, Anthropic, Groq, Ollama, and LM Studio. OpenAI-compatible local endpoints use `/v1` and the exact model name returned by the server.

### `@aura.heal`

The decorator catches a runtime exception, sends the traceback and function source to the model, logs the diagnosis, retries according to the configured retry count, and re-raises the original exception if the retry still fails.

```python
import logging
from god_ai import aura

logging.basicConfig(level=logging.INFO)
aura.configure(provider="ollama", model="llama3", heal_retries=1)

@aura.heal
def parse_number(value: str) -> int:
    return int(value)

print(parse_number("42"))
```

It does not silently rewrite your source file. Review the logged diagnosis before changing production code.

### `aura.do()`

Ghost execution turns an instruction into transient Python, validates its AST, blocks imports and process/filesystem primitives, and returns the value assigned to `result`.

```python
from god_ai import aura

aura.configure(provider="ollama", model="llama3")
answer = aura.do(
    "Return the average temperature",
    context={"temperatures": [18, 21, 24]},
)
print(answer)
```

This is guarded execution, not a sandbox. Use trusted model servers and avoid sending secrets in context.

### `aura.agent()`

The agent runs `python -m pytest -q`, sends failures to the configured model, and repeats up to a limit. Edits are disabled by default. Enable them explicitly only in a disposable branch or workspace.

```python
from god_ai import aura

result = aura.agent(
    "Fix the failing unit tests",
    root=".",
    max_iterations=3,
    allow_edits=False,
)
print(result.passed, result.output)
```

With `allow_edits=True`, only model-returned unified diffs are passed to the local `patch` command. Review Git changes after every iteration.

### `@aura.optimize`

The decorator measures runtime. Calls taking at least 100 milliseconds receive a model-generated optimization suggestion in the logger.

```python
from god_ai import aura

@aura.optimize
def slow_sum(values):
    return sum(values)
```

### `aura.parse()`

The parser asks the model for JSON and can validate the response with a Pydantic model.

```python
from pydantic import BaseModel
from god_ai import aura

class Person(BaseModel):
    name: str
    age: int

person = aura.parse("Ada is 36 years old", Person)
print(person.name, person.age)
```

Without a model class, `aura.parse(text)` returns a dictionary or list.

### `aura.system`

```python
from god_ai import aura

print(aura.system.os_name)
print(aura.system.package_manager)
print(aura.system.is_termux)
print(aura.system.is_ish)
```

Detection is read-only and safe on Linux, macOS, Windows, Android Termux, and iSH.

## Local Models in Detail

### Ollama

Install from [ollama.com](https://ollama.com/), then:

```sh
ollama pull llama3
ollama run llama3
curl http://localhost:11434/v1/models
```

Use `AURA_BASE_URL=http://localhost:11434/v1`. Ollama does not need an API key.

### LM Studio

Install from [lmstudio.ai](https://lmstudio.ai/), download a model, load it, open **Local Server**, and click **Start Server**. LM Studio commonly uses port `1234`:

```sh
curl http://localhost:1234/v1/models
```

Then configure:

```sh
export AURA_PROVIDER=local
export AURA_BASE_URL=http://localhost:1234/v1
export AURA_MODEL=the-exact-id-from-v1-models
god "Reply with exactly: LM Studio connected"
```

`Connection refused` means the server is not running. `404` usually means the base URL is missing `/v1`. A model error usually means the model ID is not exact.

## Device Setup

| Device | Install commands |
| --- | --- |
| Windows | `py -m pip install god-ai` |
| macOS | `python3 -m pip install god-ai` |
| Linux | `python3 -m pip install god-ai` |
| Android Termux | `pkg update && pkg install python git && python -m pip install god-ai` |
| iPhone/iPad iSH | `apk update && apk add python3 py3-pip git && python3 -m pip install --break-system-packages god-ai` |

Termux uses `pkg`, iSH uses Alpine `apk`, and neither environment should assume `sudo` or `systemd`. On small mobile devices, prefer a small local model and avoid running multiple heavy services at once.

## Source Development

```sh
git clone https://github.com/ayushgiriai21-cmd/God.git
cd God
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m py_compile $(find src -name '*.py')
god --help
```

Build the PyPI artifacts:

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
```

## Publishing Version 1.0.0

The workflow in `.github/workflows/publish.yml` runs when a GitHub Release is published or a `v*` tag is pushed. It builds `.tar.gz` and `.whl` files and publishes them using the `PYPI_API_TOKEN` repository secret.

```sh
git add .
git commit -m "Release God AI 1.0.0"
git tag v1.0.0
git push origin main --tags
```

Create `PYPI_API_TOKEN` under GitHub repository **Settings > Secrets and variables > Actions**. Never place the token in code.

## Contributing

Create a branch, make a focused change, run compilation and `git diff --check`, update the documentation for public APIs, and open a pull request. Keep generated commands confirmation-gated and preserve safe behavior by default.

## License

God AI is released under the MIT License. See [LICENSE](LICENSE).
