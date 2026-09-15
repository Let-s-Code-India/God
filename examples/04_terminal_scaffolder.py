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
