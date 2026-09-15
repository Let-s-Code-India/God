# God AI

<p align="center">
  <strong>One AI copilot for your terminal, your Python code, and your local models.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/god-ai/"><img src="https://img.shields.io/pypi/v/god-ai.svg" alt="PyPI"></a>
  <a href="https://github.com/ayushgiriai21-cmd/God/actions"><img src="https://github.com/ayushgiriai21-cmd/God/actions/workflows/publish.yml/badge.svg" alt="Build"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-yellow.svg" alt="Python 3.9+">
</p>

God AI is a hybrid Python package for developers who want an AI assistant at the command line and inside their own applications. Use a cloud provider, Ollama, or LM Studio through one configuration surface.

> **Status:** `0.1.0` is an alpha release. Review generated code and keep command execution in safe mode while evaluating the project.

## Contents

- [What You Get](#what-you-get)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Local LLM Setup](#local-llm-setup)
- [CLI Mode](#cli-mode)
- [Python SDK](#python-sdk)
- [Device Setup](#device-setup)
- [Security](#security)
- [Development](#development)
- [Release to PyPI](#release-to-pypi)
- [Contributing](#contributing)

## What You Get

### Mode 1: Terminal assistant

After installation, ask God AI to inspect a project, explain an error, or plan a change:

```sh
god "explain this project and suggest a test plan"
god "build a web app in the current directory"
```

The legacy checkout command also works:

```sh
python main.py "summarize the current project"
```

### Mode 2: Python library

Import the same runtime into your application:

```python
from god_ai import god

god.configure(provider="ollama", model="llama3")
answer = god.do("Return a list of the prime numbers below 20")
print(answer)
```

The SDK exposes four intentionally small capabilities:

| API | Purpose |
| --- | --- |
| `god.configure(...)` | Select a cloud provider or local model endpoint. |
| `@god.heal` | Diagnose a runtime exception with the LLM and retry the function. |
| `god.do(...)` | Turn a natural-language instruction into guarded in-memory Python. |
| `god.system` | Read stable OS, Termux, iSH, shell, and package-manager facts. |

## Architecture

```text
                    +----------------------+
                    |  god CLI / Python SDK |
                    +----------+-----------+
                               |
             +-----------------+------------------+
             |                                    |
       LLMClient                             system
   cloud or local API                  platform constraints
             |
   +---------+----------+
   |                    |
  heal                 do
 diagnostics       guarded Python
   |
 memory / command execution / optional localhost web UI
```

The canonical source lives under `src/god_ai/`. Root-level Python files are thin compatibility entry points for older checkouts. `pyproject.toml` is the source of packaging truth.

## Installation

### From PyPI

```sh
python -m pip install --upgrade god-ai
```

Verify the installation:

```sh
god --help
python -c "from god_ai import god; print(god.system.as_dict())"
```

### From source

```sh
git clone https://github.com/ayushgiriai21-cmd/God.git god-ai
cd god-ai
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Windows PowerShell:

```powershell
git clone https://github.com/ayushgiriai21-cmd/God.git god-ai
Set-Location god-ai
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Configuration

Configuration is process-wide and can be supplied directly in Python, through environment variables, or in a root `.env` file.

```python
from god_ai import god

god.configure(
    provider="openai",
    api_key="your-api-key",
    model="gpt-4o-mini",
)
```

Available provider names are `openai`, `gemini`, `anthropic`, `groq`, `local`, and the convenience alias `ollama`. Local providers do not require an API key.

Example `.env`:

```dotenv
AURA_PROVIDER=local
AURA_BASE_URL=http://localhost:11434/v1
AURA_MODEL=llama3
AURA_API_KEY=
```

Useful variables:

| Variable | Meaning |
| --- | --- |
| `AURA_PROVIDER` | Provider route. |
| `AURA_API_KEY` | Cloud provider credential. Keep it private. |
| `AURA_BASE_URL` | Custom or local OpenAI-compatible endpoint. |
| `AURA_MODEL` | Model identifier accepted by that provider. |
| `AURA_REQUEST_TIMEOUT` | Network timeout in seconds. |
| `AURA_MAX_DEBUG_RETRIES` | CLI command repair attempts. |

## Local LLM Setup

Local inference keeps prompts on your device after the model is downloaded. God AI uses the OpenAI-compatible chat endpoint, so the connection has three important values: provider, base URL, and model identifier.

### Option A: Ollama

1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Open a terminal and download a model by running it:

```sh
ollama run llama3
```

The first run downloads the model. Ollama usually starts its server automatically at `http://localhost:11434`.

3. Confirm the model server:

```sh
curl http://localhost:11434/api/tags
curl http://localhost:11434/v1/models
```

4. Connect God AI from the CLI:

```sh
export AURA_PROVIDER=ollama
export AURA_BASE_URL=http://localhost:11434/v1
export AURA_MODEL=llama3
god "Reply with exactly: Ollama connected"
```

PowerShell:

```powershell
$env:AURA_PROVIDER="ollama"
$env:AURA_BASE_URL="http://localhost:11434/v1"
$env:AURA_MODEL="llama3"
god "Reply with exactly: Ollama connected"
```

5. Connect from Python:

```python
from god_ai import god

god.configure(
    provider="ollama",
    base_url="http://localhost:11434/v1",
    model="llama3",
)
print(god.do("Return the string 'Ollama connected'"))
```

For a smaller device, choose a smaller model and expect slower first-token latency. `ollama list` shows installed models; `ollama pull llama3` downloads without starting an interactive chat.

### Option B: LM Studio

1. Download LM Studio from [lmstudio.ai](https://lmstudio.ai/).
2. Download a model in the Discover tab.
3. Load the model in the Chat tab.
4. Open **Local Server**, select the loaded model, and click **Start Server**.
5. LM Studio commonly listens at `http://localhost:1234/v1`.
6. Inspect the exact model identifier:

```sh
curl http://localhost:1234/v1/models
```

7. Configure the CLI or `.env`:

```dotenv
AURA_PROVIDER=local
AURA_BASE_URL=http://localhost:1234/v1
AURA_MODEL=the-model-id-returned-by-lm-studio
AURA_API_KEY=
```

8. Configure the SDK:

```python
from god_ai import god

god.configure(
    provider="local",
    base_url="http://localhost:1234/v1",
    model="the-model-id-returned-by-lm-studio",
)
print(god.do("Return a JSON-like dictionary with status='connected'"))
```

### Local model troubleshooting

- **Connection refused:** start the Ollama or LM Studio server.
- **404 from chat completions:** use the OpenAI-compatible URL ending in `/v1`.
- **Model not found:** copy the exact ID from `/v1/models`; display names are not always IDs.
- **Timeout:** use a smaller model or increase `AURA_REQUEST_TIMEOUT`.
- **Port conflict:** update `AURA_BASE_URL` to the server's actual port.

## Python SDK

### Self-healing decorator

`@god.heal` catches an exception, sends the traceback and available function source to the configured model for diagnosis, logs the diagnosis, retries according to `heal_retries`, and re-raises the original failure if the retry still fails.

```python
import logging
from god_ai import god

logging.basicConfig(level=logging.INFO)
god.configure(provider="ollama", model="llama3", heal_retries=1)

@god.heal
def parse_port(value: str) -> int:
    return int(value)

print(parse_port("8000"))
```

Healing is diagnostic assistance, not magic code mutation. It does not silently rewrite your source file.

### Ghost function execution

`god.do()` asks the model for a Python block assigning its final value to `result`, validates the AST, blocks imports and process/filesystem primitives, then executes it in memory.

```python
from god_ai import god

god.configure(provider="ollama", model="llama3")
result = god.do(
    "Calculate the average and maximum temperature",
    context={"temperatures": [18, 21, 19, 24]},
)
print(result)
```

Treat generated code as untrusted input. The guard reduces the attack surface but is not a security sandbox. Do not use `god.do()` with untrusted model servers or sensitive data.

### System detection

```python
from god_ai import god

print(god.system.os_name)
print(god.system.package_manager)
print(god.system.is_termux)
print(god.system.is_ish)
print(god.system.as_dict())
```

Detection is read-only and does not install packages or execute shell commands. Termux and iSH constraints can be included in prompts with `god_ai.system_prompt()`.

## CLI Device Setup

### Linux

```sh
sudo apt update
sudo apt install -y python3 python3-venv git
python3 -m venv .venv
. .venv/bin/activate
python -m pip install god-ai
```

### macOS

Install Python and Git with [Homebrew](https://brew.sh/), then:

```sh
brew install python git
python3 -m pip install god-ai
god "inspect this directory"
```

### Windows

Install Python 3.9+ and Git, then in PowerShell:

```powershell
py -3 -m pip install god-ai
god "inspect this directory"
```

### Android Termux

```sh
pkg update
pkg install python git
python -m pip install god-ai
god "use Termux-compatible commands"
```

Avoid `sudo` and `systemd`. For voice helpers, install the Termux:API package and the companion Android application. Small phones may need a lightweight local model or a cloud provider.

### iSH on iPhone or iPad

```sh
apk update
apk add python3 py3-pip git
python3 -m pip install --break-system-packages god-ai
god "use portable Alpine commands"
```

Prefer JSON or lightweight workflows on constrained iSH environments. Avoid assuming GNU utilities or `systemd`.

## Security

Safe defaults matter because a model can generate destructive commands or unsafe code.

- CLI shell commands should be reviewed before execution.
- Do not enable automatic command execution in a directory containing secrets.
- Never commit `.env`, API keys, model credentials, or memory files.
- `god.do()` is guarded execution, not a container or operating-system sandbox.
- Use a separate user, container, or disposable workspace for experiments.
- Use a trusted local model server and restrict its network exposure to localhost.

## Development

```sh
git clone https://github.com/ayushgiriai21-cmd/God.git
cd God
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m py_compile $(find src -name '*.py')
god --help
python -c "from god_ai import god; print(god.system.as_dict())"
```

Build distributions locally:

```sh
python -m pip install build twine
python -m build
python -m twine check dist/*
```

The package uses `src/` layout, PEP 621 metadata, `setuptools`, and the console entry point `god = god_ai.cli:main`.

## Release to PyPI

1. Update the version in `pyproject.toml`.
2. Run the compile checks and build validation.
3. Commit the version change.
4. Create and push a version tag:

```sh
git add pyproject.toml README.md src
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main --tags
```

5. Or create a GitHub Release for the tag. The workflow at `.github/workflows/publish.yml` runs on a published release or any `v*` tag, builds an sdist and wheel, checks them with Twine, and publishes with `PYPI_API_TOKEN`.
6. Add the repository secret at **Settings -> Secrets and variables -> Actions -> New repository secret** with the name `PYPI_API_TOKEN`.

Never put a PyPI token in source code or commit history.

## Contributing

Open an issue for a bug or design proposal. For a pull request:

```sh
git checkout -b feature/your-change
python -m py_compile $(find src -name '*.py')
git diff --check
git add .
git commit -m "Describe the change"
git push -u origin feature/your-change
```

Please keep public APIs typed, avoid platform-specific assumptions, add a focused smoke test for behavior changes, and document new configuration variables.
