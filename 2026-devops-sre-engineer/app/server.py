"""Gateway de inferência simulado.

Serve respostas fixas imitando a API de geração da plataforma. Não chama
nenhum modelo real e não precisa de rede externa.
"""

import argparse
import json
import os
import signal
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "dev")
PORT = int(os.environ.get("PORT", "8080"))
WARMUP_SECONDS = float(os.environ.get("WARMUP_SECONDS", "3"))

_started_at = time.monotonic()
_counts: dict[tuple[str, str], int] = {}
_lock = threading.Lock()


def log(**fields):
    fields = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "version": VERSION, **fields}
    print(json.dumps(fields, ensure_ascii=False), flush=True)


def _count(route: str, code: int):
    with _lock:
        key = (route, str(code))
        _counts[key] = _counts.get(key, 0) + 1


def _metrics() -> str:
    lines = [
        "# HELP http_requests_total Requisições HTTP atendidas.",
        "# TYPE http_requests_total counter",
    ]
    with _lock:
        for (route, code), value in sorted(_counts.items()):
            lines.append(f'http_requests_total{{route="{route}",code="{code}"}} {value}')
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    server_version = "gateway"

    def log_message(self, *args):
        pass

    def _send(self, code: int, body: str, content_type="application/json"):
        payload = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _handle(self):
        started = time.monotonic()
        path = self.path.split("?", 1)[0]
        route = path

        if path == "/healthz":
            code, body = 200, '{"status":"ok"}'
        elif path == "/readyz":
            ready = time.monotonic() - _started_at >= WARMUP_SECONDS
            code = 200 if ready else 503
            body = json.dumps({"ready": ready})
        elif path == "/metrics":
            code, body = 200, _metrics()
        elif path == "/v1/generate":
            code = 200
            body = json.dumps(
                {
                    "model": "mka1-mini",
                    "version": VERSION,
                    "output": "Resposta de demonstração gerada localmente.",
                },
                ensure_ascii=False,
            )
        else:
            route = "other"
            code, body = 404, '{"error":"not found"}'

        content_type = "text/plain; version=0.0.4" if path == "/metrics" else "application/json"
        self._send(code, body, content_type)
        _count(route, code)
        if path not in ("/metrics",):
            log(
                level="info" if code < 400 else "warn",
                msg="request",
                method=self.command,
                path=path,
                status=code,
                duration_ms=round((time.monotonic() - started) * 1000, 2),
                client=self.client_address[0],
            )

    do_GET = _handle
    do_POST = _handle


def serve():
    token = os.environ.get("GATEWAY_API_TOKEN", "")
    if not token:
        log(level="error", msg="GATEWAY_API_TOKEN ausente; encerrando")
        sys.exit(1)

    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)

    def stop(*_):
        log(level="info", msg="encerrando")
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    log(level="info", msg="iniciado", port=PORT, warmup_seconds=WARMUP_SECONDS)
    httpd.serve_forever()


def traffic(url: str, interval: float):
    """Gera tráfego contínuo e registra o resultado de cada chamada."""
    log(level="info", msg="gerador de tráfego iniciado", target=url)
    while True:
        started = time.monotonic()
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                status, error = resp.status, None
        except urllib.error.HTTPError as exc:
            status, error = exc.code, None
        except Exception as exc:  # conexão recusada, timeout, DNS
            status, error = 0, type(exc).__name__
        log(
            level="info" if status == 200 else "error",
            msg="probe",
            target=url,
            status=status,
            error=error,
            duration_ms=round((time.monotonic() - started) * 1000, 2),
        )
        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--traffic", metavar="URL")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if args.traffic:
        traffic(args.traffic, args.interval)
    else:
        serve()
