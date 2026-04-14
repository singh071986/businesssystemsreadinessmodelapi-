from flask import Flask, render_template, request, jsonify, send_file, make_response
from datetime import datetime
import requests
import json
import io
from xhtml2pdf import pisa

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
    else:
        # On GET/refresh, always clear result and error
        result = None
        error = None
    return render_template('index.html', sample=sample, result=result, error=error, questions=QUESTIONS)


# PDF generation route
@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    # Get the result data from the POST request
    result = request.json.get('result')
    if not result:
        return make_response('No result data provided', 400)
    # Add PDF generation datetime
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_name = result.get('name', '')
    # Render the result as HTML using a template
    html = render_template('pdf_report.html', result=result, generated_at=generated_at, client_name=client_name)
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)
    if pisa_status.err:
        return make_response('PDF generation failed', 500)
    pdf.seek(0)
    return send_file(pdf, mimetype='application/pdf', as_attachment=True, download_name='assessment_report.pdf')

if __name__ == '__main__':
    app.run(debug=True)
