# cPanel Production Deployment (Clear Step-by-Step)

Use this file as the only runbook. It has two flows:

1. Full reset and fresh deploy
2. Fresh deploy only

This guide assumes no cPanel terminal access and uses only cPanel UI.

## A) Values you must use everywhere

1. Domain: testapi.businessystem.com
2. App root in Setup Python App: business_api
3. Full folder path: /home/twmpathway/business_api
4. Startup file: passenger_wsgi.py
5. Entry point: application
6. Python version: 3.11

Do not change these values between screens.

## B) Full reset and fresh deploy

Use this if you already tried many times and want a clean start.

1. In Setup Python App:
2. Stop the existing app.
3. Delete the existing app entry.
4. In Domains, delete testapi.businessystem.com entry.
5. In File Manager, open /home/twmpathway/business_api.
6. Delete old project files from that folder.
7. Keep only system folders if present, such as .well-known and cgi-bin.
8. Delete old zip files, __MACOSX, and .DS_Store.
9. Recreate domain in Domains:
10. Domain: testapi.businessystem.com
11. Share document root: unchecked
12. Document root: business_api
13. Save.

After this, continue with section C.

## C) Fresh deploy only

Use this if domain already exists and points to /home/twmpathway/business_api.

1. In File Manager, open /home/twmpathway/business_api.
2. Upload project zip.
3. Extract zip in this same folder.
4. If extraction creates nested folder, move contents up into /home/twmpathway/business_api.
5. Ensure these are directly in /home/twmpathway/business_api:
6. passenger_wsgi.py
7. requirements.txt
8. src folder
9. models folder
10. data folder
11. Delete __MACOSX, .DS_Store, and the uploaded zip.

## D) Create Python app

1. Open Setup Python App and click Create Application.
2. Python version: 3.11
3. Application root: business_api
4. Application URL: testapi.businessystem.com
5. Startup file: passenger_wsgi.py
6. Entry point: application
7. Save.

## E) Install dependencies

1. In Setup Python App, under Configuration files, add requirements.txt.
2. Click Run Pip Install.
3. Wait for success.

Use pinned dependencies in requirements.txt:

1. scikit-learn==1.4.2
2. numpy==1.26.4
3. pydantic==2.7.1
4. joblib==1.3.2
5. fastapi==0.110.0
6. uvicorn==0.29.0
7. a2wsgi==1.10.8

## F) Create or verify startup file

Path: /home/twmpathway/business_api/passenger_wsgi.py

Content:

import os
import sys
from a2wsgi import ASGIMiddleware

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.api import app as fastapi_app

application = ASGIMiddleware(fastapi_app)

## G) Ensure model file exists

Required file:

/home/twmpathway/business_api/models/pathway_classifier.pkl

If missing:

1. In Setup Python App, Execute python script.
2. Script path: src/train_model.py
3. Click Run Script.
4. Confirm the pkl file appears in models.

## H) Add logging files

1. In File Manager, create folder /home/twmpathway/business_api/logs
2. Create files:
3. /home/twmpathway/business_api/logs/boot.log
4. /home/twmpathway/business_api/logs/api_debug.log

Useful commands:

```bash
tail -f /home/twmpathway/business_api/logs/boot.log
tail -f /home/twmpathway/business_api/logs/api_debug.log
```

Optional app logging snippets:

In passenger_wsgi.py add:

from datetime import datetime
with open("/home/twmpathway/business_api/logs/boot.log", "a") as f:
    f.write(f"boot hit: {datetime.utcnow().isoformat()}Z\\n")

In src/api.py add:

import logging
logging.basicConfig(
    filename="/home/twmpathway/business_api/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

## I) Restart app

1. Stop App
2. Start or Restart App

## J) DNS and SSL checks

1. Ensure DNS A record for testapi.businessystem.com points to your cPanel server IP.
2. In cPanel SSL/TLS Status, run AutoSSL for testapi.businessystem.com.
3. If local dig fails with timeout, test with public resolver from local machine:
4. dig +short testapi.businessystem.com @1.1.1.1
5. dig +short testapi.businessystem.com @8.8.8.8

## K) Test endpoints

1. Open in browser:
2. https://testapi.businessystem.com/health
3. Run predict test from local machine:

curl -i -X POST https://testapi.businessystem.com/predict -H "Content-Type: application/json" -d '{"responses":{"q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C","q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"}}'

## L) Quick failure guide

1. TLS unrecognized name:
2. DNS points to wrong server. Fix A record.
3. 405 empty body and no app logs:
4. Request not reaching FastAPI. Recheck domain mapping and host routing.
5. Application URL becomes testapi.businessystem.com.pathway.thewebsitemembership.com:
6. Domain created incorrectly. Delete and recreate exact domain.

## M) Final checklist

1. Domain exists as testapi.businessystem.com
2. Document root is business_api
3. App root is business_api
4. Startup file is passenger_wsgi.py
5. Entry point is application
6. Requirements installed successfully
7. Model file exists
8. App restarted
9. Health endpoint returns API response
10. Predict endpoint returns JSON

## N) Pre-deploy sanity commands (run locally before zip upload)

Run these from project root:

1. Validate tests:
2. python tests/test_api.py
3. python tests/prod_smoke_test.py
4. python tests/test_validation.py
5. Verify model exists:
6. ls -lh models/pathway_classifier.pkl
7. Verify dependency lock file:
8. cat requirements.txt
9. Create deploy zip (exclude local junk):
10. zip -r business_api_deploy.zip . -x "*.git*" "*.DS_Store" "__pycache__/*" "*.pytest_cache*" "*.mypy_cache*" "logs/*" "*.log" ".env*"

Expected outcome:

1. All tests pass
2. Model file present
3. Zip contains passenger_wsgi.py, requirements.txt, src/, models/, data/

## O) Runtime environment checklist (production-safe defaults)

Set these in cPanel Python App environment variables (or equivalent host env):

1. CORS_ALLOW_ORIGINS=https://your-ui-domain.com
2. API_EXPOSE_ERROR_DETAILS=false
3. SUMMARY_SOURCE=deterministic
4. ANTHROPIC_API_KEY=key-fromconsole
5. ANTHROPIC_MODEL=claude-sonnet-4-5
6. ANTHROPIC_MAX_TOKENS=1400
7. ANTHROPIC_TIMEOUT_SECONDS=25
8. NARRATIVE_PROMPT_DOCX_PATH=/home/twmpathway/business_api/data/narrative_assembly_prompt_draft3.docx

Notes:

1. Do not use CORS_ALLOW_ORIGINS=* in production unless required.
2. API_EXPOSE_ERROR_DETAILS=false prevents internal exception leakage in API responses.
3. If debugging a server issue temporarily, set API_EXPOSE_ERROR_DETAILS=true, test, then set back to false.
4. Keep SUMMARY_SOURCE=deterministic for fallback mode.
5. Switch SUMMARY_SOURCE=llm only after ANTHROPIC_API_KEY is set and app restart is completed.

## P) SSL and connectivity operations runbook

Use this section for day-to-day certificate and reachability checks.

### 1) How SSL works for UI to API calls

1. The UI calls https://testapi.businessystem.com.
2. Browser performs TLS handshake with the server.
3. Server presents certificate for testapi.businessystem.com.
4. Browser validates hostname, trust chain, and expiry.
5. If valid, traffic is encrypted and request proceeds.

Important:

1. You do not need manual certificate exchange between UI and API for standard HTTPS.
2. Manage server certificate on the API domain only.
3. CORS is separate from SSL and must still be configured.

### 2) Certificate management tasks

1. In cPanel, run AutoSSL for testapi.businessystem.com.
2. Confirm certificate is issued for exact hostname testapi.businessystem.com.
3. Confirm auto-renew is active.
4. Check expiry weekly in SSL/TLS Status.

### 3) Connectivity checks (copy and run)

1. DNS resolution:
2. dig +short testapi.businessystem.com @1.1.1.1
3. dig +short testapi.businessystem.com @8.8.8.8
4. TLS handshake:
5. curl -Iv https://testapi.businessystem.com/health
6. Health endpoint:
7. curl -i https://testapi.businessystem.com/health
8. Predict endpoint:
9. curl -i -X POST https://testapi.businessystem.com/predict -H "Content-Type: application/json" -d '{"first_name":"Sarah","responses":{"q1":"C","q2":"B","q3":"C","q4":"C","q5":"B","q6":"C","q7":"C","q8":"B","q9":"C","q10":"A","q11":"C","q12":"B"}}'

Expected:

1. DNS returns cPanel server IP.
2. curl -Iv shows valid certificate for testapi.businessystem.com.
3. /health returns HTTP 200 JSON.
4. /predict returns HTTP 200 JSON.

### 4) Fast failure diagnosis

1. curl: (6) Could not resolve host
2. DNS is not published or wrong nameserver/record.
3. curl: (60) SSL certificate problem or hostname mismatch
4. Certificate does not match testapi.businessystem.com or AutoSSL not complete.
5. HTML 404/5xx instead of JSON
6. Domain routing issue in cPanel or request not reaching FastAPI.
7. JSON 500 with MODEL_NOT_FOUND
8. models/pathway_classifier.pkl missing on server.

### 5) Operational ownership checklist

1. DNS owner keeps A record pointed to current server IP.
2. Hosting owner verifies AutoSSL issuance and renewal.
3. API owner verifies health and predict endpoints after every deploy.
4. UI owner verifies CORS origin is explicitly allowed and uses HTTPS API URL only.
