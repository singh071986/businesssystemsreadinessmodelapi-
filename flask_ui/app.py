from flask import Flask, render_template, request, jsonify
import requests
import json

from questions import QUESTIONS

app = Flask(__name__)

API_URL = "https://business-api.thewebsitemembership.com/predict"

# Load sample data for prefill/demo
def load_sample_responses():
    try:
        with open(os.path.join(os.path.dirname(__file__), '../data/user_request_examples.json')) as f:
            data = json.load(f)
            # Expecting a list of dicts with 'responses' and optional 'first_name'
            return data[0] if isinstance(data, list) and data else {}
    except Exception:
        return {}

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    sample = load_sample_responses()
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        responses = {f"q{i}": request.form.get(f"q{i}") for i in range(1, 13)}
        payload = {"responses": responses}
        if first_name:
            payload["first_name"] = first_name
        try:
            api_resp = requests.post(API_URL, json=payload, timeout=60)
            if api_resp.headers.get('Content-Type', '').startswith('application/json'):
                result = api_resp.json()
            else:
                error = f"Non-JSON response: {api_resp.text[:200]}"
        except Exception as e:
            error = str(e)
    return render_template('index.html', sample=sample, result=result, error=error, questions=QUESTIONS)

if __name__ == '__main__':
    app.run(debug=True)
