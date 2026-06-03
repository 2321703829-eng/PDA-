from __future__ import annotations

import argparse
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


def parse_mapping(raw: str) -> tuple[str, tuple[str, int]]:
    host, backend = raw.split("=", 1)
    backend_host, backend_port = backend.rsplit(":", 1)
    return host.lower().strip(), (backend_host.strip(), int(backend_port))


class ReverseProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    routes: dict[str, tuple[str, int]] = {}

    def _resolve_backend(self) -> tuple[str, int] | None:
        host = (self.headers.get("Host") or "").split(":", 1)[0].lower().strip()
        return self.routes.get(host)

    def _forward(self) -> None:
        backend = self._resolve_backend()
        if not backend:
            self.send_error(404, "Unknown tenant host")
            return

        backend_host, backend_port = backend
        body = b""
        content_length = self.headers.get("Content-Length")
        if content_length:
            body = self.rfile.read(int(content_length))

        path = self.path
        split = urlsplit(path)
        upstream_path = split.path or "/"
        if split.query:
            upstream_path = f"{upstream_path}?{split.query}"

        headers = {}
        for key, value in self.headers.items():
            lowered = key.lower()
            if lowered in HOP_BY_HOP_HEADERS or lowered == "host":
                continue
            headers[key] = value
        headers["Host"] = self.headers.get("Host", "")
        headers["X-Forwarded-Host"] = self.headers.get("Host", "")
        headers["X-Forwarded-Proto"] = "http"
        headers["X-Forwarded-For"] = self.client_address[0]
        headers["Connection"] = "close"

        conn = http.client.HTTPConnection(backend_host, backend_port, timeout=120)
        try:
            conn.request(self.command, upstream_path, body=body or None, headers=headers)
            resp = conn.getresponse()
            payload = resp.read()
            self.send_response(resp.status, resp.reason)
            for key, value in resp.getheaders():
                lowered = key.lower()
                if lowered in HOP_BY_HOP_HEADERS:
                    continue
                if lowered == "location":
                    self.send_header(key, value)
                    continue
                self.send_header(key, value)
            self.send_header("Connection", "close")
            self.end_headers()
            if payload:
                self.wfile.write(payload)
        except Exception as exc:  # pragma: no cover - local utility
            message = f"Proxy error: {exc}".encode("ascii", "replace").decode("ascii")
            self.send_error(502, message)
        finally:
            conn.close()

    def do_GET(self) -> None:  # noqa: N802
        self._forward()

    def do_POST(self) -> None:  # noqa: N802
        self._forward()

    def do_PUT(self) -> None:  # noqa: N802
        self._forward()

    def do_DELETE(self) -> None:  # noqa: N802
        self._forward()

    def do_PATCH(self) -> None:  # noqa: N802
        self._forward()

    def do_HEAD(self) -> None:  # noqa: N802
        self._forward()


def main() -> None:
    parser = argparse.ArgumentParser(description="Local host-based reverse proxy for tenant validation")
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen-port", type=int, default=8090)
    parser.add_argument(
        "--map",
        action="append",
        required=True,
        help="Host to backend mapping, e.g. kebi.tianshu.test=127.0.0.1:8070",
    )
    args = parser.parse_args()

    ReverseProxyHandler.routes = dict(parse_mapping(item) for item in args.map)
    server = ThreadingHTTPServer((args.listen_host, args.listen_port), ReverseProxyHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
