# cPanel Deployment Guide (FastAPI)

This guide deploys the project publicly on cPanel using **Setup Python App** (Passenger).

## Security Note

- Do not share cPanel URLs that include temporary `cpsess...` tokens.
- Use your normal cPanel login URL only.

## Prerequisites

- A hosting plan with **Setup Python App** enabled.
- A domain/subdomain to publish the API (example: `api.yourdomain.com`).
- Project code available in cPanel (Git clone or uploaded ZIP).

## 1) Create Public URL

1. In cPanel, open **Domains** or **Subdomains**.
2. Create a subdomain like `api.yourdomain.com`.
3. Set document root to a folder such as:
   - `/home/twmpathway/public_html/business_api`

## 2) Upload or Clone Project

Open cPanel Terminal (or SSH), then:

```bash
cd /home/twmpathway/public_html/business_api
```

Option A (Git clone):

```bash
git clone https://github.com/singh071986/BusinessSystemsReadinessModelAPI-.git .
```

Option B (ZIP):

- Upload ZIP in File Manager.
- Extract into `/home/twmpathway/public_html/business_api`.

## 3) Create Python App in cPanel

1. Open **Setup Python App**.
2. Click **Create Application**.
3. Use:
   - Python version: `3.10` or `3.11`
   - Application root: `/home/twmpathway/public_html/business_api`
   - Application URL: `api.yourdomain.com`
   - Application startup file: `passenger_wsgi.py`
   - Application entry point: `application`

   requirements.txt
4. Click **Create**.

## 4) Install Dependencies

In **Setup Python App**, copy the venv activation command and run it in Terminal. Then run:

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install a2wsgi
```

## 5) Add Passenger WSGI Adapter

Create file `passenger_wsgi.py` in app root with:

```python
import os
import sys
from a2wsgi import ASGIMiddleware

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.api import app as fastapi_app

application = ASGIMiddleware(fastapi_app)
```

## 6) Ensure Model File Exists

The app needs:

- `models/pathway_classifier.pkl`

If missing, train it:

```bash
python src/train_model.py
```

## 7) Restart Python App

1. Go back to **Setup Python App**.
2. Click **Restart** for the app.

## 8) Test Public Endpoints

Health check:

```bash
curl https://api.yourdomain.com/health
```

Prediction test:

```bash
curl -X POST https://api.yourdomain.com/predict \
  -H "Content-Type: application/json" \
  -d '{"responses":{"q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C","q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"}}'
```

## 9) Enable SSL (Required for Public Use)

1. Run **AutoSSL** for `api.yourdomain.com`.
2. Verify HTTPS endpoint works.

## 10) If Setup Python App Is Missing

1. Your hosting plan may not support Python Passenger.
2. Ask hosting support to enable **Python App (CloudLinux Passenger)**.
3. If not possible, deploy to a platform like Render/Railway/VPS.

## 11) Quick Update Flow (After Code Changes)

```bash
cd /home/twmpathway/public_html/business_api
git pull origin main
pip install -r requirements.txt
```

Then restart app from cPanel **Setup Python App**.

## Common Troubleshooting

### Module import errors

- Re-activate cPanel virtual environment and reinstall:

```bash
pip install -r requirements.txt
pip install a2wsgi
```

### 500 error on `/predict`

- Confirm model exists at `models/pathway_classifier.pkl`.
- If missing, run:

```bash
python src/train_model.py
```

### CORS issues from frontend

Set allowed origins before restart:

```bash
export CORS_ALLOW_ORIGINS="https://yourfrontend.com"
```

If your host does not preserve shell exports, set env vars through cPanel Python App environment configuration (if available) and restart.
