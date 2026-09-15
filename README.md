# AURA

AURA is a small cross-platform AI engine with one Python entry point for terminal tasks and a localhost web UI. It supports hosted OpenAI-compatible APIs, Gemini, Anthropic, Groq-compatible endpoints, and local OpenAI-compatible servers such as Ollama and LM Studio.

## Features

- Terminal mode: `python main.py "describe a task"`
- Localhost UI: `python main.py --web`
- Safe mode confirmation before shell execution, or explicit God mode
- Fenced shell command extraction with up to three debug retries
- SQLite memory by default, with JSON fallback for constrained devices
- Platform detection for Termux, iSH, macOS, Linux, and Windows
- Optional Termux:API speech-to-text and text-to-speech helpers
- No mandatory cloud SDK: HTTP calls use Python's standard library

## Install

```sh
git clone <your-repository-url> aura
cd aura
python -m venv .venv
. .venv/bin/activate                 # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python setup.py
```

`setup.py` creates `.env`. It is intentionally ignored by Git because it can contain an API key.

## Configuration

Copy `.env.example` to `.env`, or use onboarding:

```sh
cp .env.example .env                 # macOS/Linux/Termux/iSH
copy .env.example .env               # Windows cmd
Copy-Item .env.example .env          # Windows PowerShell
```

Important values are `AURA_PROVIDER` (`openai`, `gemini`, `anthropic`, `groq`, or `local`), `AURA_API_KEY`, `AURA_BASE_URL`, `AURA_MODEL`, `AURA_MODE` (`cli` or `web`), `AURA_SECURITY_MODE` (`safe` or `god`), and `AURA_MEMORY_BACKEND` (`sqlite` or `json`).

For local Ollama, use `AURA_PROVIDER=local`, `AURA_BASE_URL=http://localhost:11434/v1`, and an installed local model. Local models do not require an API key.

## Use

```sh
python main.py "build a QR code generator site and host it"
python main.py --web                         # open http://127.0.0.1:8000
```

Optional aliases:

```sh
alias ai='python /absolute/path/to/aura/main.py'
echo "alias ai='python /absolute/path/to/aura/main.py'" >> ~/.bashrc
# zsh users append the same line to ~/.zshrc
```

Windows PowerShell:

```powershell
function ai { python C:\absolute\path\to\aura\main.py @args }
```

## Mobile environments

Termux:

```sh
pkg update
pkg install python git
git clone <your-repository-url> aura && cd aura
python -m pip install -r requirements.txt
python setup.py
```

Install `termux-api` and the Termux:API Android app only for voice features. AURA detects Termux and tells the model to avoid `sudo`, `systemd`, and desktop-only packages.

iSH / Alpine:

```sh
apk update
apk add python3 py3-pip git
git clone <your-repository-url> aura && cd aura
python3 -m pip install --break-system-packages -r requirements.txt
python3 setup.py
```

AURA detects iSH and directs generated commands toward `apk`, POSIX shell syntax, and no `systemd` assumptions. On very small devices, select JSON memory instead of SQLite.

Linux and macOS can use `apt install python3 python3-venv git` or `brew install python git`. Windows users need Python 3.11+ and Git.

## Security

Safe mode is the default and asks before every extracted command. God mode executes commands automatically and should only be used in a disposable or trusted project directory. AURA does not sandbox subprocesses or grant privileges; use OS permissions, containers, and separate users for stronger isolation.

## Checks

```sh
python -m py_compile *.py
python main.py --help
python -c "from system_detector import detect_system; print(detect_system().as_dict())"
```

## Git: commit and push `main`

```sh
git status
git remote -v
git remote add origin https://github.com/OWNER/REPOSITORY.git  # only if origin is missing
git add .
git commit -m "Build AURA cross-platform AI engine"
git branch -M main
git push -u origin main
```

If the remote has commits, reconcile first with `git pull --rebase origin main`, then run `git push origin main`. Never commit `.env`; commit `.env.example` instead.
