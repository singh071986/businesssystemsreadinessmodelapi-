import asyncio
import os
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Boot marker
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
with open(os.path.join(logs_dir, "boot.log"), "a") as f:
    f.write(f"boot hit: {datetime.utcnow().isoformat()}Z\n")

from src.logging_utils import get_app_logger, get_runtime_context, log_event

app_logger = get_app_logger("business_api.passenger")
log_event(app_logger, "passenger_boot_marker", base_dir=BASE_DIR, **get_runtime_context())

try:
    from src.api import app as fastapi_app
    log_event(app_logger, "passenger_application_ready", base_dir=BASE_DIR)
except Exception:
    app_logger.exception("passenger_boot_failure")
    raise


_STATUS_TEXTS = {
    200: "OK", 201: "Created", 204: "No Content",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
    404: "Not Found", 405: "Method Not Allowed",
    422: "Unprocessable Entity", 500: "Internal Server Error",
}


class _ASGIToWSGI:
    """
    Minimal ASGI-to-WSGI bridge.

    a2wsgi.ASGIMiddleware deadlocks in Passenger/LiteSpeed because it spins up
    background threads with their own event loops — which conflicts with the
    Passenger worker threading model.  This bridge instead creates a fresh
    event loop in the *calling* thread, runs the ASGI app to completion
    synchronously, then closes the loop.  No threads, no shared loop state.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        app_logger.info(
            '{"event": "wsgi_invoked", "method": "%s", "path": "%s"}'
            % (environ.get("REQUEST_METHOD", ""), environ.get("PATH_INFO", ""))
        )
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self._handle(environ, start_response))
        except Exception:
            app_logger.exception(
                '{"event": "wsgi_bridge_error", "path": "%s"}'
                % environ.get("PATH_INFO", "")
            )
            start_response(
                "500 Internal Server Error",
                [("Content-Type", "application/json")],
            )
            return [b'{"code":"INTERNAL_ERROR","message":"WSGI bridge error","details":null}']
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    async def _handle(self, environ, start_response):
        # Build ASGI headers list from WSGI environ
        headers = []
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                name = key[5:].lower().replace("_", "-").encode("latin-1")
                headers.append((name, value.encode("latin-1")))
        for wsgi_key, header_name in (
            ("CONTENT_TYPE", b"content-type"),
            ("CONTENT_LENGTH", b"content-length"),
        ):
            if environ.get(wsgi_key):
                headers.append((header_name, environ[wsgi_key].encode("latin-1")))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": environ.get("SERVER_PROTOCOL", "HTTP/1.1").split("/")[-1],
            "method": environ.get("REQUEST_METHOD", "GET").upper(),
            "headers": headers,
            "path": environ.get("PATH_INFO", "/"),
            "query_string": environ.get("QUERY_STRING", "").encode("latin-1"),
            "root_path": environ.get("SCRIPT_NAME", ""),
            "server": (
                environ.get("SERVER_NAME", "localhost"),
                int(environ.get("SERVER_PORT", 80)),
            ),
            "client": None,
        }

        # Read body once upfront
        content_length = int(environ.get("CONTENT_LENGTH") or 0)
        body = environ["wsgi.input"].read(content_length) if content_length > 0 else b""

        # Starlette may call receive() again during response handling to check
        # for disconnects. In WSGI we cannot detect real client disconnects, so
        # we wait until the response is fully sent before returning disconnect.
        _body_consumed = False
        _response_complete = asyncio.Event()

        async def receive():
            nonlocal _body_consumed
            if not _body_consumed:
                _body_consumed = True
                return {"type": "http.request", "body": body, "more_body": False}
            await _response_complete.wait()
            return {"type": "http.disconnect"}

        response_status = []
        response_headers = []
        body_chunks = []

        async def send(message):
            if message["type"] == "http.response.start":
                response_status.append(message["status"])
                response_headers.extend(message.get("headers", []))
            elif message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                if chunk:
                    body_chunks.append(chunk)
                if not message.get("more_body", False):
                    _response_complete.set()

        await self.app(scope, receive, send)

        status_code = response_status[0] if response_status else 500
        status_str = f"{status_code} {_STATUS_TEXTS.get(status_code, 'Unknown')}"
        wsgi_headers = [
            (k.decode("latin-1"), v.decode("latin-1"))
            for k, v in response_headers
        ]
        start_response(status_str, wsgi_headers)
        return body_chunks


application = _ASGIToWSGI(fastapi_app)
