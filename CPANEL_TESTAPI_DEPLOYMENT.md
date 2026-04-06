# cPanel Deployment for testapi.businessystem.com

Use this file to deploy the app on the registered subdomain `testapi.businessystem.com` using the code inside:

- `/home/twmpathway/business_api`

This guide assumes:

1. You will deploy through cPanel UI.
2. The app code will live in `/home/twmpathway/business_api`.
3. The public test URL will be `https://testapi.businessystem.com`.

## A) Exact values to use everywhere

Use these exact values consistently across Domains, File Manager, and Setup Python App:

1. Domain: `testapi.businessystem.com`
2. Document root: `business_api`
3. Full folder path: `/home/twmpathway/business_api`
4. Application root: `business_api`
5. Application URL: `testapi.businessystem.com`
6. Startup file: `passenger_wsgi.py`
7. Entry point: `application`
8. Python version: `3.11`

Do not mix these values with the temporary domain.

## B) Important note before you start

If you already created a Python app entry for the temporary domain or another domain that points to the same folder `business_api`, remove or stop that old app first.

Why:

1. It avoids cPanel routing confusion.
2. It ensures only one active Python app entry owns `/home/twmpathway/business_api` during testing.

If `api.businessystem.com` is not live yet, use only `testapi.businessystem.com` for now.

## C) Create the registered subdomain

In cPanel:

1. Open **Domains**.
2. Click **Create A New Domain** or **Create**.
3. Enter domain: `testapi.businessystem.com`
4. Make sure **Share document root** is unchecked.
5. Set **Document Root** to: `business_api`
6. Save.

After saving, the subdomain should point to:

1. `/home/twmpathway/business_api`

## D) Confirm DNS for the subdomain

If your DNS is managed by the same cPanel account, the subdomain record is often created automatically.

Still verify this:

1. `testapi.businessystem.com` resolves to your cPanel server IP.

If DNS is managed outside cPanel, create an `A` record for:

1. Host: `testapi`
2. Value: your cPanel server IP

Do not continue to final testing until DNS is correct.

## E) Prepare the deployment folder

Open **File Manager** and go to:

1. `/home/twmpathway/business_api`

This folder must contain the project files directly at the top level.

You should see:

1. `passenger_wsgi.py`
2. `requirements.txt`
3. `src/`
4. `models/`
5. `data/`
6. `docs/`
7. `tests/`

If you uploaded a zip and it extracted into a nested folder such as:

1. `/home/twmpathway/business_api/Ripponmar22/passenger_wsgi.py`

move the contents up one level so that the correct path becomes:

1. `/home/twmpathway/business_api/passenger_wsgi.py`

Delete these if present:

1. uploaded zip files
2. `__MACOSX`
3. `.DS_Store`

## F) Verify the startup file

Open this file in File Manager:

1. `/home/twmpathway/business_api/passenger_wsgi.py`

It should contain the FastAPI Passenger adapter and expose `application`.

Expected content:

```python
import os
import sys
from datetime import datetime

from a2wsgi import ASGIMiddleware

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
with open(os.path.join(logs_dir, "boot.log"), "a") as f:
    f.write(f"boot hit: {datetime.utcnow().isoformat()}Z\\n")

from src.api import app as fastapi_app

application = ASGIMiddleware(fastapi_app)
```

If the file is different, replace it with the content above.

## G) Create the Python app

Open **Setup Python App** and click **Create Application**.

Use these exact values:

1. Python version: `3.11`
2. Application root: `business_api`
3. Application URL: `testapi.businessystem.com`
4. Application startup file: `passenger_wsgi.py`
5. Application entry point: `application`

Then click **Create** or **Save**.

## H) Install dependencies

After the Python app is created:

1. In **Setup Python App**, add or confirm `requirements.txt` if your host shows that option.
2. Click **Run Pip Install** if that button is available.

If cPanel instead shows a virtualenv activation command, run that in Terminal and then run:

```bash
pip install --upgrade pip
pip install -r /home/twmpathway/business_api/requirements.txt
```

Required packages from the repo include:

1. `fastapi`
2. `uvicorn`
3. `a2wsgi`
4. `scikit-learn`
5. `numpy`
6. `pydantic`
7. `joblib`

## I) Ensure the model file exists

This file must exist:

1. `/home/twmpathway/business_api/models/pathway_classifier.pkl`

If it is missing:

1. In **Setup Python App**, use **Execute Python Script** if available.
2. Script path: `src/train_model.py`
3. Run the script.

Or run it from the app environment:

```bash
python /home/twmpathway/business_api/src/train_model.py
```

After that, verify the model file exists inside `models/`.

## J) Add optional logs folder

In File Manager, create:

1. `/home/twmpathway/business_api/logs`

The startup file will then write boot records to:

1. `/home/twmpathway/business_api/logs/boot.log`

This is helpful if the app does not start cleanly.

## K) Restart the app

In **Setup Python App**:

1. Stop App
2. Start App or Restart App

Wait 20 to 30 seconds after restart.

## L) Enable SSL for the subdomain

In cPanel:

1. Open **SSL/TLS Status**
2. Find `testapi.businessystem.com`
3. Run **AutoSSL**
4. Wait for the certificate to finish issuing

Unlike the `cpanel.site` temporary domain, your registered subdomain should be able to get a valid certificate.

## M) Test DNS from your local machine

Run one of these locally:

```bash
dig +short testapi.businessystem.com @1.1.1.1
dig +short testapi.businessystem.com @8.8.8.8
```

Expected result:

1. your cPanel server IP is returned

## N) Test the health endpoint

Once DNS and SSL are ready, run:

```bash
curl -i https://testapi.businessystem.com/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "business-systems-readiness-api",
  "version": "1.2.0"
}
```

## O) Test the predict endpoint

Run:

```bash
curl -i -X POST https://testapi.businessystem.com/predict \
  -H "Content-Type: application/json" \
  -d '{"responses":{"q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C","q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"}}'
```

Expected result:

1. HTTP `200 OK`
2. JSON prediction response

## P) If `/health` returns 404

Check these in order:

1. Domain is exactly `testapi.businessystem.com`
2. Document root is exactly `business_api`
3. Application root is exactly `business_api`
4. Application URL is exactly `testapi.businessystem.com`
5. `passenger_wsgi.py` is directly in `/home/twmpathway/business_api`
6. App was restarted after creation

## Q) If `/health` returns 500

Check these in order:

1. dependencies installed successfully
2. `a2wsgi` installed successfully
3. model file exists
4. startup file content is correct
5. `logs/boot.log` was updated after restart

## R) If `/predict` returns 500 but `/health` works

That usually means the API is running but the model layer is not ready.

Check:

1. `/home/twmpathway/business_api/models/pathway_classifier.pkl` exists
2. `scikit-learn`, `numpy`, and `joblib` installed in the Python app environment
3. app restarted after model creation

## S) Final checklist

Deployment is complete only when all of these are true:

1. `testapi.businessystem.com` exists in Domains
2. Document root is `business_api`
3. Full folder path is `/home/twmpathway/business_api`
4. Python app exists in Setup Python App
5. Python version is `3.11`
6. Application root is `business_api`
7. Application URL is `testapi.businessystem.com`
8. Startup file is `passenger_wsgi.py`
9. Entry point is `application`
10. dependencies installed successfully
11. model file exists
12. SSL issued successfully
13. `https://testapi.businessystem.com/health` returns JSON
14. `https://testapi.businessystem.com/predict` returns JSON