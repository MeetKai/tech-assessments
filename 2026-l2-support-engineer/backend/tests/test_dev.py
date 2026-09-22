import importlib.util
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "dev.py"
spec = importlib.util.spec_from_file_location("dev", SCRIPT)
dev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dev)


def test_port_check_allows_immediate_restart():
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", 0))
        port = server.getsockname()[1]
        server.listen()
        with socket.create_connection(("127.0.0.1", port)) as client:
            connection, _ = server.accept()
            connection.close()
            assert client.recv(1) == b""
    dev.check_port(port)


def test_port_check_rejects_active_listener():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        with pytest.raises(OSError):
            dev.check_port(server.getsockname()[1])


def test_cleanup_stops_child_even_after_parent_exits(tmp_path):
    ready = tmp_path / "port"
    child = """
import signal, socket, sys, time
from pathlib import Path
signal.signal(signal.SIGTERM, signal.SIG_IGN)
server = socket.socket()
server.bind(('127.0.0.1', 0))
server.listen()
Path(sys.argv[1]).write_text(str(server.getsockname()[1]))
while True: time.sleep(.05)
"""
    wrapper = "import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', sys.argv[1], sys.argv[2]]); time.sleep(60)"
    process = subprocess.Popen([sys.executable, "-c", wrapper, child, str(ready)], start_new_session=True)
    try:
        deadline = time.monotonic() + 5
        while not ready.exists() and time.monotonic() < deadline:
            time.sleep(.02)
        assert ready.exists(), "Child did not start"
        port = int(ready.read_text())
        process.terminate()
        process.wait(timeout=3)
        dev.stop_processes([process], timeout=.2)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", port)) != 0:
                    break
            time.sleep(.02)
        else:
            pytest.fail("The child server is still listening after cleanup")
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=3)


def test_root_make_forwards_dev_to_assessment():
    root = SCRIPT.parents[2]
    result = subprocess.run(["make", "-n", "dev"], cwd=root, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "2026-l2-support-engineer" in result.stdout


def test_environment_lives_outside_document_workspace():
    import tempfile

    environment = dev.environment_path()
    assert environment.is_relative_to(Path(tempfile.gettempdir()))
    assert not environment.is_relative_to(dev.ROOT)


def test_python_bytecode_lives_outside_document_workspace():
    import tempfile

    cache = dev.bytecode_path()
    assert cache.is_relative_to(Path(tempfile.gettempdir()))
    assert not cache.is_relative_to(dev.ROOT)
