import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def main():
    for port in (8000, 5173):
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                sys.exit(f"A porta {port} está ocupada. Encerre o serviço e tente novamente.")
    subprocess.run(["uv", "sync", "--frozen"], cwd=ROOT / "backend", check=True)
    subprocess.run(["npm", "ci", "--no-audit", "--no-fund"], cwd=ROOT / "frontend", check=True)
    processes = []
    def stop(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    try:
        processes.append(subprocess.Popen(["uv", "run", "--frozen", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], cwd=ROOT / "backend", start_new_session=True))
        processes.append(subprocess.Popen(["npm", "run", "dev"], cwd=ROOT / "frontend", start_new_session=True))
        print("Portal: http://127.0.0.1:5173 · Ctrl+C para encerrar", flush=True)
        while all(p.poll() is None for p in processes):
            time.sleep(.2)
        return next((p.returncode or 1 for p in processes if p.poll() is not None), 1)
    except KeyboardInterrupt:
        return 0
    finally:
        for process in processes:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()

if __name__ == "__main__":
    sys.exit(main())
