# cPanel Temporary Domain Deployment (Step-by-Step)

Use this guide when you want to test the full FastAPI app on the temporary domain created by cPanel, such as:

- `artistic-maroon-dog.104-36-228-2.cpanel.site`

This is for testing only. Use your registered domain for production.

## A) What this guide is for

Use this runbook when:

1. cPanel already created a temporary domain for your account.
2. You already uploaded or extracted the project files into the folder tied to that temporary domain.
3. You want to run the full Python app through **Setup Python App** using the temporary domain URL.

This project is deployed as:

1. FastAPI app in `src/api.py`
2. Passenger startup file `passenger_wsgi.py`
3. Entry point `application`

## B) Important difference from registered domain deployment

For production, you use your real domain such as `api.businessystem.com`.

For temporary-domain testing, use the temporary cPanel domain everywhere instead, for example:

1. `artistic-maroon-dog.104-36-228-2.cpanel.site`

Also note:

1. `Not Redirected` in cPanel is normal for this setup.
2. Do not create a redirect unless you intentionally want the temporary domain to forward somewhere else.
3. The temporary domain must point to the same folder used as the Python app root.

## C) Values you must collect first

Before creating the Python app, gather these exact values from cPanel:

1. Temporary domain name
2. Temporary domain document root
3. Full folder path on the server

Example only:

1. Temporary domain: `artistic-maroon-dog.104-36-228-2.cpanel.site`
2. Document root: `temp_api_app`
3. Full path: `/home/USERNAME/temp_api_app`

Use your actual values, not the example above.

## D) Verify the temporary domain folder

In cPanel:

1. Open **Domains**.
2. Find the temporary domain.
3. Click **Manage**.
4. Note the **Document Root**.

Then open **File Manager** and go to that folder.

The app files must be directly inside that folder.

You should see these items at the top level:

1. `passenger_wsgi.py`
2. `requirements.txt`
3. `src/`
4. `models/`
5. `data/`
6. `tests/`

If you see an extra nested folder such as:

1. `temp_api_app/Ripponmar22/passenger_wsgi.py`

then move the contents of `Ripponmar22` up one level so that the file becomes:

1. `/home/USERNAME/temp_api_app/passenger_wsgi.py`

Do not leave the project nested one level deeper than the document root.

## E) Clean up common upload leftovers

In the temporary-domain folder, delete these if present:

1. uploaded zip files
2. `__MACOSX`
3. `.DS_Store`

These files are not needed and sometimes make the folder structure confusing.

## F) Create the Python app for the temporary domain

Open **Setup Python App** and click **Create Application**.

Use these settings:

1. Python version: `3.11`
2. Application root: the temporary-domain document root folder
3. Application URL: the full temporary domain
4. Startup file: `passenger_wsgi.py`
5. Entry point: `application`

Example only:

1. Python version: `3.11`
2. Application root: `temp_api_app`
3. Application URL: `artistic-maroon-dog.104-36-228-2.cpanel.site`
4. Startup file: `passenger_wsgi.py`
5. Entry point: `application`

Important:

1. The **Application root** must match the temporary domain document root folder.
2. The **Application URL** must be the temporary domain itself.
3. The startup file and entry point must match the values above exactly.

## G) If the temporary domain does not show in Setup Python App

Some hosts handle `cpanel.site` preview domains differently.

If you cannot select the temporary domain in **Setup Python App**:

1. Keep the project files where they are for now.
2. Create a normal subdomain in cPanel instead.
3. Point that subdomain to the same folder.
4. Create the Python app on that subdomain.

Example fallback:

1. `api.yourdomain.com`

This is the most reliable option if Passenger does not bind cleanly to the temporary domain.

## H) Install dependencies

After creating the app:

1. In **Setup Python App**, locate the virtual environment details.
2. Add or confirm `requirements.txt` if your host provides that option.
3. Run **Pip Install** or use the provided activation command in Terminal.

Install the dependencies from `requirements.txt`.

If you are using Terminal after activating the app environment, run:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This project requires at minimum:

1. `fastapi`
2. `uvicorn`
3. `a2wsgi`
4. `scikit-learn`
5. `numpy`
6. `pydantic`
7. `joblib`

## I) Verify the startup file

Path:

1. `/home/USERNAME/your_temp_domain_folder/passenger_wsgi.py`

The file should expose `application` and load FastAPI through `a2wsgi`.

Expected structure:

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

This repository already includes `passenger_wsgi.py`, so normally you only need to make sure it is in the correct folder.

## J) Ensure the model file exists

Required file:

1. `models/pathway_classifier.pkl`

If this file is missing, `/predict` will fail.

If needed, run this from the app environment:

```bash
python src/train_model.py
```

Then verify the model file exists inside `models/`.

## K) Restart the app

In **Setup Python App**:

1. Stop App
2. Start App or Restart App

Do this after:

1. creating the app
2. installing dependencies
3. generating the model file
4. changing startup settings

## L) Test the temporary domain in browser

Use your temporary domain URL.

Open these endpoints:

1. `https://YOUR_TEMP_DOMAIN/health`
2. `https://YOUR_TEMP_DOMAIN/docs`

Example:

1. `https://artistic-maroon-dog.104-36-228-2.cpanel.site/health`
2. `https://artistic-maroon-dog.104-36-228-2.cpanel.site/docs`

Expected result for `/health`:

```json
{
  "status": "ok",
  "service": "business-systems-readiness-api",
  "version": "1.2.0"
}
```

## M) Test the predict endpoint

Run this from your local machine, replacing the domain with your own temporary domain:

```bash
curl -i -X POST https://YOUR_TEMP_DOMAIN/predict \
  -H "Content-Type: application/json" \
  -d '{"responses":{"q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C","q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"}}'
```

Expected result:

1. HTTP `200 OK`
2. JSON response with pathway prediction data

## N) If the browser shows 404 or default page

This usually means the temporary domain is not hitting the Python app.

Check these in order:

1. The temporary domain document root is the same folder as the Python app root.
2. `passenger_wsgi.py` is directly inside that folder.
3. The app was created with the temporary domain as the Application URL.
4. The app was restarted after setup.

## O) If `/health` works but `/predict` fails

Most likely causes:

1. `models/pathway_classifier.pkl` is missing
2. dependencies were not installed in the cPanel Python environment
3. import error during app startup

Fixes:

1. run `pip install -r requirements.txt` in the app environment
2. run `python src/train_model.py`
3. restart the app

## P) If you get 500 Internal Server Error immediately

Check these first:

1. `a2wsgi` installed successfully
2. `fastapi` installed successfully
3. `scikit-learn`, `numpy`, `joblib`, and `pydantic` installed successfully
4. the project is not inside an extra nested folder

If your host provides app logs, review them after restart.

This repository already writes a boot marker log through `passenger_wsgi.py` if the `logs/` folder exists.

Optional helper setup:

1. create `logs/`
2. create `logs/boot.log`

Then restart the app and see whether `boot.log` gets updated.

## Q) Temporary-domain testing checklist

Before you start testing, confirm all of these are true:

1. temporary domain exists in cPanel
2. temporary domain document root is known
3. project files are directly inside that folder
4. `passenger_wsgi.py` is present in the app root
5. Python app is created in **Setup Python App**
6. Python version is `3.11`
7. Application URL is the temporary domain
8. Entry point is `application`
9. dependencies installed successfully
10. `models/pathway_classifier.pkl` exists
11. app restarted successfully
12. `/health` returns JSON
13. `/predict` returns JSON

## R) When to move from temporary domain to real domain

Move to the registered domain after these pass on the temporary domain:

1. `/health`
2. `/docs`
3. `/predict`
4. dependency install
5. model load

Then repeat the same app-root and Passenger setup on the real domain using the production runbook.