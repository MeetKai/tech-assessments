import os
from pathlib import Path
import hashlib
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def environment_path():
    repository_key = hashlib.sha256(str(ROOT.resolve()).encode()).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "meetkai-base-conhecimento" / repository_key / "venv"


def bytecode_path():
    return environment_path().parent / "pycache"


def frontend_cache_path():
    return environment_path().parent / "frontend"


def sync_frontend(source, target):
    source = Path(source)
    target = Path(target)
    paths = [name for name in ("index.html", "vite.config.ts", "tsconfig.json", "package.json", "package-lock.json") if (source / name).is_file()]
    for folder in ("src", "public"):
        if (source / folder).exists():
            paths.extend(path.relative_to(source) for path in (source / folder).rglob("*") if path.is_file())
    for relative in paths:
        original = source / relative
        cached = target / relative
        cached.parent.mkdir(parents=True, exist_ok=True)
        if (not cached.exists() or cached.stat().st_mtime_ns != original.stat().st_mtime_ns or
                cached.stat().st_size != original.stat().st_size):
            shutil.copy2(original, cached)
    for folder in ("src", "public"):
        cached_folder = target / folder
        if cached_folder.exists():
            for cached in cached_folder.rglob("*"):
                if cached.is_file() and cached.relative_to(target) not in paths:
                    cached.unlink()


def check_port(port):
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.0.1", port))


def signal_group(process, signum):
    try:
        os.killpg(process.pid, signum)
        return True
    except ProcessLookupError:
        return False


def stop_processes(processes, timeout=3):
    for process in processes:
        signal_group(process, signal.SIGTERM)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for process in processes:
            process.poll()
        if not any(signal_group(process, 0) for process in processes):
            break
        time.sleep(.05)
    for process in processes:
        signal_group(process, signal.SIGKILL)
        process.wait()


def main(frontend_only=False):
    processes = []
    stopping = False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True

    def start(command, cwd, env=None):
        if stopping:
            raise InterruptedError
        process = subprocess.Popen(command, cwd=cwd, env=env, start_new_session=True)
        processes.append(process)
        return process

    def install(command, cwd, env=None):
        process = start(command, cwd, env=env)
        while process.poll() is None:
            if stopping:
                raise InterruptedError
            time.sleep(.1)
        if stopping:
            raise InterruptedError
        if process.returncode:
            raise RuntimeError(f"O comando {' '.join(command)} terminou com código {process.returncode}.")
        processes.remove(process)

    def wait_ready(port):
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if stopping:
                raise InterruptedError
            if any(process.poll() is not None for process in processes):
                raise RuntimeError("Um serviço encerrou durante a inicialização. Confira a saída acima.")
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=.2):
                    return
            except OSError:
                time.sleep(.1)
        raise RuntimeError(f"O serviço na porta {port} não iniciou em 60 segundos.")

    for port in ((5173,) if frontend_only else (8000, 5173)):
        try:
            check_port(port)
        except OSError as error:
            print(f"Não foi possível usar a porta {port}: {error}. Confira com: lsof -nP -iTCP:{port} -sTCP:LISTEN", file=sys.stderr)
            return 1
    previous_handlers = {sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        if not frontend_only:
            print("Preparando dependências…", flush=True)
            python_environment = environment_path()
            uv_environment = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(python_environment)}
            install(["uv", "sync", "--frozen"], ROOT / "backend", uv_environment)
        frontend = ROOT / "frontend"
        frontend_cache = frontend_cache_path()
        print("Preparando interface…", flush=True)
        sync_frontend(frontend, frontend_cache)
        dependency_hash = hashlib.sha256(
            (frontend_cache / "package.json").read_bytes() +
            (frontend_cache / "package-lock.json").read_bytes()
        ).hexdigest()
        marker = frontend_cache / ".meetkai-dependencies"
        vite = frontend_cache / "node_modules/vite/bin/vite.js"
        if not vite.exists() or not marker.exists() or marker.read_text() != dependency_hash:
            install(["npm", "ci", "--no-audit", "--no-fund"], frontend_cache)
            marker.write_text(dependency_hash)
        if not frontend_only:
            print("Iniciando API…", flush=True)
            api_environment = {**os.environ, "PYTHONPYCACHEPREFIX": str(bytecode_path())}
            start([str(python_environment / "bin/python"), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"], ROOT / "backend", api_environment)
            wait_ready(8000)
        print("Iniciando interface…", flush=True)
        start(["node", str(vite), "--host", "127.0.0.1", "--port", "5173", "--strictPort"], frontend_cache)
        wait_ready(5173)
        label = "Interface" if frontend_only else "Portal"
        print(f"{label}: http://127.0.0.1:5173 · Ctrl+C para encerrar", flush=True)
        next_sync = time.monotonic()
        while not stopping and all(p.poll() is None for p in processes):
            if time.monotonic() >= next_sync:
                sync_frontend(frontend, frontend_cache)
                next_sync = time.monotonic() + 1
            time.sleep(.2)
        if stopping:
            return 0
        print("Um serviço encerrou. Encerrando os demais serviços.", file=sys.stderr)
        return next((p.returncode or 1 for p in processes if p.poll() is not None), 1)
    except InterruptedError:
        return 0
    except (OSError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        stop_processes(processes)
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)

if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--frontend-only"]):
        sys.exit("Uso: python3 scripts/dev.py [--frontend-only]")
    sys.exit(main(frontend_only=sys.argv[1:] == ["--frontend-only"]))
