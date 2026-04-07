import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "api_debug.log"


def get_app_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(LOG_FILE, maxBytes=2_000_000, backupCount=5)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)sZ pid=%(process)d level=%(levelname)s logger=%(name)s message=%(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.info(json.dumps(payload, sort_keys=True, default=str))


def get_runtime_context() -> dict[str, Any]:
    return {
        "cwd": os.getcwd(),
        "hostname": os.getenv("HOSTNAME"),
        "logs_path": str(LOG_FILE),
        "python_version": os.sys.version.split()[0],
    }