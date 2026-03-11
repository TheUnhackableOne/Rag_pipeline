import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent
DOCS_DIR = PROJECT_ROOT / "data" / "documents"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
STATE_FILE = PROJECT_ROOT / ".ingest_state.json"


def _compute_documents_fingerprint() -> str:
    """Create a stable fingerprint from PDF names, sizes, and mtimes."""
    pdf_files = sorted(DOCS_DIR.glob("*.pdf"), key=lambda p: p.name.lower())
    payload = []
    for pdf in pdf_files:
        stat = pdf.stat()
        payload.append({
            "name": pdf.name,
            "size": stat.st_size,
            "mtime": int(stat.st_mtime),
        })

    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _needs_ingestion() -> bool:
    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Documents folder not found: {DOCS_DIR}")

    pdf_files = list(DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {DOCS_DIR}")

    if not VECTOR_DB_DIR.exists() or not any(VECTOR_DB_DIR.iterdir()):
        return True

    current_fingerprint = _compute_documents_fingerprint()
    state = _load_state()
    return state.get("docs_fingerprint") != current_fingerprint


def _run_ingestion(python_exe: str) -> None:
    print("[1/3] Running ingestion pipeline...")
    cmd = [python_exe, str(PROJECT_ROOT / "rag_pipeline.py")]
    completed = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if completed.returncode != 0:
        raise RuntimeError("Ingestion failed. Please check pipeline errors above.")

    _save_state({"docs_fingerprint": _compute_documents_fingerprint()})
    print("[1/3] Ingestion complete.")


def _start_process(name: str, cmd: list[str]) -> subprocess.Popen[Any]:
    print(f"Starting {name}...")
    return subprocess.Popen(cmd, cwd=PROJECT_ROOT)


def main() -> None:
    python_exe = sys.executable
    print(f"Using Python: {python_exe}")

    if _needs_ingestion():
        _run_ingestion(python_exe)
    else:
        print("[1/3] Documents unchanged. Skipping ingestion.")

    print("[2/3] Starting API server...")
    api_proc = _start_process(
        "FastAPI",
        [python_exe, "-m", "uvicorn", "api.main:app", "--reload", "--port", "8000"],
    )

    print("[3/3] Starting Streamlit UI...")
    ui_proc = _start_process(
        "Streamlit",
        [python_exe, "-m", "streamlit", "run", "ui/app.py", "--server.port", "8501"],
    )

    time.sleep(2)
    webbrowser.open("http://localhost:8501")

    print("\nAll services started:")
    print("- API: http://localhost:8000")
    print("- UI : http://localhost:8501")
    print("\nPress Ctrl+C here to stop both services.")

    try:
        while True:
            if api_proc.poll() is not None:
                raise RuntimeError("FastAPI process exited unexpectedly.")
            if ui_proc.poll() is not None:
                raise RuntimeError("Streamlit process exited unexpectedly.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        for proc in (api_proc, ui_proc):
            if proc.poll() is None:
                if os.name == "nt":
                    proc.send_signal(signal.CTRL_BREAK_EVENT)
                    time.sleep(1)
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    main()
