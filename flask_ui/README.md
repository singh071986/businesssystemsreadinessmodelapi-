# Flask UI for Business Systems Readiness API

This Flask app provides a web interface to submit assessment responses to the [business-api.thewebsitemembership.com](https://business-api.thewebsitemembership.com/) `/predict` endpoint, following the contract in `docs/api_interface_testapi.md`.

## Features
- Fill out 12-question assessment (q1–q12, A/B/C/D)
- Optional first name
- Submits to the deployed API and displays the result
- Uses sample data from `data/user_request_examples.json` for demo/prefill

## Setup

1. **Install dependencies:**

```bash
cd flask_ui
python3 -m venv venv
source venv/bin/activate
pip install flask requests
```

2. **Run the app:**

```bash
python app.py
```

3. **Open in browser:**

Go to [http://localhost:5000](http://localhost:5000)

## Notes
- Requires internet access to reach the deployed API.
- You can edit `../data/user_request_examples.json` to change the prefilled sample.
- For contract details, see `../docs/api_interface_testapi.md`.
