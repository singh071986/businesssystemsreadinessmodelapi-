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

from src.api import app as fastapi_app

application = ASGIMiddleware(fastapi_app)
