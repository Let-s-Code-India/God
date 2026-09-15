# God-main (AURA)

God-main is a small, cross-platform AI workbench. It gives you one assistant name, one configuration file, and two ways to work:

- **Terminal mode** for asking questions, generating commands, and completing coding tasks in the current folder.
- **Localhost web mode** for chatting from a browser while keeping the model connection and command execution on your own computer.

The project is intentionally lightweight. It uses Python's standard library for HTTP requests, SQLite or JSON for memory, and optional packages only for the web server and terminal presentation.

## How the Pieces Fit Together

```text
Your prompt
    |
    v
main.py ---------------------------> Terminal output or web_server.py
    |                                      |
    +--> memory_manager.py                +--> static/index.html
    |       SQLite or JSON                |
    +--> system_detector.py              |
    |       platform constraints          +--> LLMHandler
    +--> llm_handler.py                  +--> CommandExecutor
            cloud/local API                     Safe or God mode
```

### Main modules

| File | Responsibility |
| --- | --- |
| `main.py` | Unified command-line entry point and web launcher. |
| `config.py` | Loads `.env`, validates settings, and supplies defaults. |
| `system_detector.py` | Detects Windows, macOS, Linux, Termux, iSH, shell, CPU, and package manager. |
| `llm_handler.py` | Sends chat requests to OpenAI-compatible APIs, Gemini, or Anthropic. |
| `command_executor.py` | Extracts fenced shell commands, asks for confirmation, runs them, and supports repair retries. |
| `memory_manager.py` | Stores chat history and project facts in SQLite or JSON. |
| `web_server.py` | Serves the browser UI and `/api/chat` and `/api/health` endpoints. |
| `termux_features.py` | Optional Termux:API speech and text-to-speech helpers. |
| `static/index.html` | Browser chat interface. |

## Before You Begin

You need:

- Python 3.10 or newer. Python 3.11 or 3.12 is recommended.
- Git.
- A supported model provider: a cloud API key or a local model server.
- Internet access for installation and cloud providers. Local models can run without an internet connection after download.

Supported environments include Linux, macOS, Windows, Android Termux, and iSH on Alpine Linux. On mobile devices, choose JSON memory if SQLite is unavailable or too resource-intensive.

## Install

### Linux, macOS, Termux, or iSH

```sh
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git god-main
cd god-main
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On systems where the command is `python` rather than `python3`, replace `python3` with `python`.

### Windows PowerShell

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git god-main
Set-Location god-main
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate the environment again.

## Configure AURA

The setup wizard is the easiest route:

```sh
python setup.py
```

It asks for the assistant name, provider, model, API key or local URL, interface, execution security, memory backend, and optional Termux voice features. It writes `.env` in the project directory.

You can also configure the project manually:

```sh
cp .env.example .env
```

On Windows PowerShell use `Copy-Item .env.example .env`. Never commit `.env`; it may contain a secret. `.env.example` is safe to commit.

Important settings:

| Variable | Example | Meaning |
| --- | --- | --- |
| `AURA_PROVIDER` | `local` | `openai`, `gemini`, `anthropic`, `groq`, or `local`. |
| `AURA_API_KEY` | `...` | Cloud provider key. Usually empty for local models. |
| `AURA_BASE_URL` | `http://localhost:11434/v1` | Optional provider or local server URL. |
| `AURA_MODEL` | `llama3.2` | Model name accepted by the selected provider. |
| `AURA_MODE` | `cli` | `cli` or `web`. |
| `AURA_SECURITY_MODE` | `safe` | `safe` asks before shell commands; `god` runs them automatically. |
| `AURA_MEMORY_BACKEND` | `sqlite` | Use `json` on constrained devices. |
| `AURA_PORT` | `8000` | Local web port. |

## Local LLM Setup (Recommended for Privacy)

AURA can talk to local servers using the OpenAI-compatible `/v1/chat/completions` format. The easiest choices are Ollama and LM Studio.

### Option A: Ollama

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Start the Ollama service. The installer normally starts it automatically.
3. Download and run a model:

```sh
ollama run llama3.2
```

The first run downloads the model. Ollama normally listens at `http://localhost:11434` and exposes the OpenAI-compatible API at `http://localhost:11434/v1`.

4. Configure AURA:

```dotenv
AURA_PROVIDER=local
AURA_BASE_URL=http://localhost:11434/v1
AURA_MODEL=llama3.2
AURA_API_KEY=
```

Or run `python setup.py` and select **Local LLM**.

5. Test Ollama directly:

```sh
curl http://localhost:11434/v1/models
```

Then test AURA:

```sh
python main.py "Reply with exactly: local model connected"
```

If Ollama says the model is missing, run `ollama pull llama3.2` and retry.

### Option B: LM Studio

1. Download LM Studio from [lmstudio.ai](https://lmstudio.ai/).
2. Open the app, search for a model, download it, and load it in the chat or server view.
3. Open the **Local Server** tab and click **Start Server**. LM Studio commonly uses `http://localhost:1234/v1`.
4. Set these values in `.env`:

```dotenv
AURA_PROVIDER=local
AURA_BASE_URL=http://localhost:1234/v1
AURA_MODEL=your-loaded-model-id
AURA_API_KEY=
```

Use the exact model identifier shown by LM Studio. Verify the server with:

```sh
curl http://localhost:1234/v1/models
```

Then run the AURA test command shown in the Ollama section.

### Local model troubleshooting

- `Connection refused`: start Ollama or LM Studio and check the port.
- `404 Not Found`: ensure `AURA_BASE_URL` ends in `/v1` for an OpenAI-compatible server.
- Model not found: use the exact installed model name, not a display nickname.
- Slow responses: choose a smaller quantized model and increase `AURA_REQUEST_TIMEOUT`.
- Termux or iSH memory pressure: use a small model, JSON memory, and avoid running the web UI and model together on very small devices.

## Cloud Providers

Run `python setup.py`, select a provider, and paste its API key. The supported routes are:

- OpenAI: `https://api.openai.com/v1`
- Groq: `https://api.groq.com/openai/v1`
- Google Gemini: `https://generativelanguage.googleapis.com/v1beta/models`
- Anthropic: `https://api.anthropic.com/v1`

For a compatible gateway, set `AURA_PROVIDER=local` or `groq` and provide its OpenAI-compatible base URL.

## Use AURA

### Terminal mode

```sh
python main.py "explain this project and suggest a test plan"
python main.py "build a QR code generator site and host it"
```

The assistant may return fenced shell commands. Safe mode asks before each command. A failed command can be sent back to the model for up to three repair attempts, controlled by `AURA_MAX_DEBUG_RETRIES`.

### Web mode

```sh
python main.py --web
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. You can also set `AURA_MODE=web` and run `python main.py`, or start the server directly:

```sh
python web_server.py
```

The health endpoint is [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health). A successful response shows the assistant name, provider, and security mode.

### Create an `ai` command

Linux, macOS, Termux, and iSH:

```sh
echo "alias ai='python /absolute/path/to/god-main/main.py'" >> ~/.bashrc
```

For zsh, append it to `~/.zshrc`, then open a new terminal. On Windows PowerShell:

```powershell
function ai { python C:\absolute\path\to\god-main\main.py @args }
```

## Security Notes

Safe mode is the default and should remain enabled while learning the project. God mode executes model-generated shell commands without confirmation. It is not a sandbox and should only be used in a disposable or trusted directory. AURA does not grant administrator privileges, but a command can still damage files that your user account can access.

Keep API keys only in `.env` or environment variables. Do not paste them into prompts, commit them, or place them in `memory/`.

## Testing and Diagnostics

Run these checks from the project root:

```sh
python -m py_compile *.py
python main.py --help
python -c "from system_detector import detect_system; print(detect_system().as_dict())"
python -c "from config import Settings; print(Settings.from_env().validate() or 'configuration valid')"
```

For a live model test, first verify the local server with `/v1/models`, then run:

```sh
python main.py "Reply with exactly: connection test passed"
```

## Git: Commit and Push to `main`

Review the files before committing:

```sh
git status
git diff
```

Then commit and push:

```sh
git add .
git commit -m "Improve AURA architecture and documentation"
git branch -M main
git push -u origin main
```

If `origin` is not configured yet:

```sh
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

If the remote already has commits that are not local:

```sh
git pull --rebase origin main
git push origin main
```

Resolve any conflicts, run the tests again, and then push. Do not use `git push --force` on a shared `main` branch.
