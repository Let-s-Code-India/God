# God AI / AURA 1.1.0

<p align="center">
  <img src="assets/logo_255x255.png" alt="God AI logo" width="180" />
</p>

<p align="center">
  <strong>Hybrid terminal assistant, Python SDK, and Aura runtime for AI-powered developer workflows.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/god-ai/"><img src="https://img.shields.io/pypi/v/god-ai.svg" alt="PyPI version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT license" /></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python 3.9+" />
</p>

God AI provides a confirmation-gated terminal assistant, a Python SDK, and the `god_ai.aura` namespace for resilient execution, structured parsing, system inspection, and model-assisted developer workflows.

## What's new in 1.1.0

- Expanded Aura exports for tracing, patch suggestions, sandboxed execution, expression evaluation, data conversion, benchmarking, and cost profiling.
- Lightweight core dependencies with opt-in `aura`, `torch`, `web`, `cloud`, and `examples` extras.
- Twenty runnable example files, including ten new real-world integration blueprints.
- A GitHub Pages documentation portal under `docs/`, with generated logo assets.
- Tag-triggered PyPI publishing through GitHub Actions.

## Installation

```bash
python -m pip install god-ai
```

Install optional capabilities as needed:

```bash
python -m pip install "god-ai[aura]"      # broad Aura/example integrations
python -m pip install "god-ai[torch]"     # NumPy, PyTorch, and torchvision
python -m pip install "god-ai[web]"       # FastAPI, Uvicorn, and Flask
python -m pip install "god-ai[cloud]"     # hosted provider SDKs
python -m pip install "god-ai[examples]"  # dependencies used by examples
```

The `turtle` example uses Python's standard-library `turtle` module and does not require a separate package.

## Configuration

Configuration can come from a `.env` file or environment variables. The provider defaults to local mode when no OpenRouter key is present.

For OpenRouter:

```bash
export AURA_PROVIDER=openrouter
export AURA_API_KEY="your-key"
export AURA_MODEL="openrouter/auto"
export AURA_BASE_URL="https://openrouter.ai/api/v1"
```

For Ollama:

```bash
export AURA_PROVIDER=ollama
export AURA_BASE_URL=http://localhost:11434/v1
export AURA_MODEL=llama3
```

For another OpenAI-compatible local server, use its `/v1` endpoint and the exact model ID returned by `/v1/models`:

```bash
export AURA_PROVIDER=local
export AURA_BASE_URL=http://localhost:1234/v1
export AURA_MODEL=exact-model-id
```

Useful settings include `AURA_FREE_ONLY`, `AURA_REQUEST_TIMEOUT`, `AURA_HEAL_RETRIES`, and `AURA_GHOST_TIMEOUT` when passed through the Python configuration API. A refused connection means the local server is not running; a 404 commonly means `/v1` is missing from the base URL.

## CLI

```text
god [--free] [--web] prompt...
aura [--free] [--web] prompt...
```

Examples:

```bash
god "find the likely cause of this test failure"
god --free "draft a README section about installation"
god --web
```

`--web` starts the optional local interface at `http://127.0.0.1:8000`. Shell commands remain confirmation-gated. Generated code is only described as tested when the CLI actually ran a command and captured its result.

## Python SDK

```python
from god_ai import aura

settings = aura.configure(
    provider="openrouter",
    api_key="your-key",
    model="openrouter/auto",
)

@aura.heal
def parse_port(value: str) -> int:
    return int(value)

print(parse_port("8000"))
```

The public Aura surface includes:

- `aura.configure()` and `aura.get_config()` for process-wide settings.
- `@aura.heal` for model diagnosis and bounded retries; it does not silently edit source files.
- `aura.trace_exceptions()` and `@aura.auto_patch` for diagnostic and model-suggested repair workflows.
- `aura.do()` and `aura.exec_sandboxed()` for constrained generated Python. AST validation reduces risk but is not a complete security boundary; use a container or low-privilege process for untrusted workloads.
- `aura.eval_expr()`, `aura.parse()`, `aura.to_pydantic()`, and `aura.to_dataclass()` for structured data workflows.
- `@aura.optimize`, `@aura.benchmark`, and `@aura.cost_profiler` for runtime measurement and suggestions.
- `aura.agent()` for iterative pytest diagnosis, with edits disabled by default.
- `aura.system` for read-only platform and package-manager detection.

Example structured parsing:

```python
from pydantic import BaseModel
from god_ai import aura

class Person(BaseModel):
    name: str
    age: int

person = aura.parse("Ada Lovelace is 36 years old", Person)
print(person.name, person.age)
```

## Examples

The repository contains 20 runnable example files. The original compatibility examples are:

```text
examples/01_pytorch_healer.py
examples/02_fastapi_agent.py
examples/03_resilient_microservice.py
examples/04_terminal_scaffolder.py
```

The 1.1.0 release adds:

```text
examples/01_pytorch_neural_healer.py
examples/02_tensorflow_model_optimizer.py
examples/03_numpy_matrix_ghost.py
examples/04_fastapi_unstructured_parser.py
examples/05_flask_resilient_microservice.py
examples/06_turtle_ai_generative_art.py
examples/07_autonomous_pytest_bot.py
examples/08_data_pipeline_transformer.py
examples/09_multimodal_vision_generator.py
examples/10_terminal_fullstack_scaffolder.py
```

Run an example from the repository root, for example:

```bash
python examples/03_numpy_matrix_ghost.py
python examples/08_data_pipeline_transformer.py
```

Some examples require optional dependencies or a configured model provider. Each file documents its own prerequisites and fallback behavior. The `turtle` example opens a desktop window and may not run in a headless environment.

## Documentation portal

Serve the static portal locally with:

```bash
python -m http.server 8080 --directory docs
```

Then open `http://127.0.0.1:8080`. The portal contains API and CLI search, provider configuration helpers, interactive examples, and the generated logo assets. It is suitable for GitHub Pages deployment from the `docs/` directory.

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

## Release process

The workflow `.github/workflows/publish.yml` runs for tags matching `v*`, regenerates package logo assets, builds an sdist and wheel, validates both with Twine, and publishes them to PyPI using the `PYPI_API_TOKEN` repository secret.

For this release:

```bash
git add .
git commit -m "feat: release v1.1.0 - Aura SDK expansion and documentation portal"
git tag v1.1.0
git push origin main --tags
```

Never commit the PyPI token. The package version and tag must be unique on PyPI.

## Project structure

```text
God/
├── assets/                 # source logo artwork
├── docs/                   # GitHub Pages portal
├── examples/               # runnable SDK examples
├── scripts/                # release asset generation
├── src/god_ai/             # installable package
├── tests/                  # contract tests
├── pyproject.toml          # package metadata and extras
└── .github/workflows/      # release automation
```

## License

God AI is available under the MIT License. See [LICENSE](LICENSE).
