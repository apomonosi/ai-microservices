from __future__ import annotations

import http.server
import json
import os
import threading
from pathlib import Path

import pytest

from tests.helpers import write_models_file

# GUI tests construct a QApplication; make sure that never tries to open a
# real display, in this sandbox or on a real machine running tests over SSH.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def services_dir(tmp_path: Path) -> Path:
    path = tmp_path / "services"
    path.mkdir()
    return path


@pytest.fixture
def models_file(tmp_path: Path) -> Path:
    """A models.yaml with a 'local' profile pointing at an unroutable
    address. Fine for list/show/search/validate/manage tests, which
    never actually call run_service over HTTP. Use `stub_models_file`
    for tests that do.
    """
    return write_models_file(tmp_path / "models.yaml")


class _EchoHandler(http.server.BaseHTTPRequestHandler):
    """Minimal OpenAI-compatible /v1/chat/completions stub: replies with
    the user message reversed, tagged with the requested model name, so
    tests can assert on the round trip without hard-coding a real model.
    """

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        user_content = body["messages"][-1]["content"]
        reply = f"ECHO[{body['model']}]: {user_content[::-1]}"
        payload = json.dumps({"choices": [{"message": {"content": reply}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - matches base class signature
        pass


@pytest.fixture
def stub_llm_server():
    server = http.server.HTTPServer(("127.0.0.1", 0), _EchoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/v1"
    finally:
        server.shutdown()
        thread.join()


@pytest.fixture
def stub_models_file(tmp_path: Path, stub_llm_server: str) -> Path:
    """A models.yaml with a 'local' profile pointing at a real (stub)
    running server, for tests exercising the full HTTP round trip.
    """
    return write_models_file(
        tmp_path / "models.yaml",
        local={"url": stub_llm_server, "model": "test-model", "timeout": 5},
    )
