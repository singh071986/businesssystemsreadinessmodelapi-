import os
import sys
from datetime import datetime

from a2wsgi import ASGIMiddleware

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Optional boot marker for cPanel troubleshooting.
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
with open(os.path.join(logs_dir, "boot.log"), "a") as f:
    f.write(f"boot hit: {datetime.utcnow().isoformat()}Z\n")

from src.logging_utils import get_app_logger, get_runtime_context, log_event

app_logger = get_app_logger("business_api.passenger")
log_event(app_logger, "passenger_boot_marker", base_dir=BASE_DIR, **get_runtime_context())

try:
    from src.api import app as fastapi_app

    _asgi_app = ASGIMiddleware(fastapi_app)
    log_event(app_logger, "passenger_application_ready", base_dir=BASE_DIR)
except Exception:
    app_logger.exception("passenger_boot_failure")
    raise


def application(environ, start_response):
    """
    WSGI entry point — fires for every incoming HTTP request.
    Logged here to confirm LiteSpeed/Passenger is actually calling this code.
    If curl times out and no wsgi_invoked entry appears, the web server is NOT
    routing requests to the Python app.
    """
    app_logger.info(
        '{"event": "wsgi_invoked", "method": "%s", "path": "%s", "query": "%s", "server_name": "%s"}'
        % (
            environ.get("REQUEST_METHOD", ""),
            environ.get("PATH_INFO", ""),
            environ.get("QUERY_STRING", ""),
            environ.get("SERVER_NAME", ""),
        )
    )
    return _asgi_app(environ, start_response)
