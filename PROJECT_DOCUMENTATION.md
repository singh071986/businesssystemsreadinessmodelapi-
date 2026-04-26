# Business Systems Readiness Assessment – Project Documentation

## Project Overview
This project is a branded, production-grade web application for the Business Systems Readiness Assessment. It enables users to answer a series of questions, receive a personalized business pathway, and download a PDF report. The app is styled to match Easy Artisan Websites branding and integrates with the business API as per the provided contract.

---

## Features
- **User Assessment Form**: Collects user responses and optional name.
- **API Integration**: Submits responses to the business API and displays the returned pathway and summary.
- **PDF Report Download**: Users can download a branded PDF report with a custom filename.
- **Loading Spinner**: Custom animated spinner for a professional user experience.
- **Clear Answers/Report**: Users can reset the form or clear the report.
- **Modern, Responsive UI**: Built with Bootstrap and custom CSS for desktop and mobile.

---

## Technology Stack
- **Backend**: Python 3, Flask
- **Frontend**: HTML, CSS (Bootstrap), JavaScript
- **PDF Generation**: xhtml2pdf
- **API Calls**: requests
- **Timezone Handling**: pytz
- **Templating**: Jinja2
- **Virtual Environment**: Python venv

---

## Folder Structure
```
flask_ui/
    app.py                  # Main Flask application
    templates/
        index.html          # Main UI template
        pdf_report.html     # PDF report template
    static/
        spinner_2.gif       # Custom loading spinner (sprite sheet)
        pdfdownload.jpeg    # PDF download button icon
    venv/                   # Python virtual environment
    ...
```

---


## Setup & Deployment
### Local Development
1. **Clone the repository** and navigate to the project folder.
2. **Create and activate the virtual environment**:
    ```sh
    cd flask_ui
    python3 -m venv venv
    source venv/bin/activate
    ```
3. **Install dependencies**:
    ```sh
    pip install -r ../requirements.txt
    ```
4. **Run the app**:
    ```sh
    python app.py
    ```
5. **Access the app** at `http://localhost:5000` in your browser.

### cPanel Deployment (Production Hosting)
1. **Upload the project** to your cPanel account (e.g., via File Manager or FTP). Place the code in a subfolder (e.g., `flask_ui`).
2. **Log in to cPanel** and open the "Setup Python App" tool (usually under the Software section).
3. **Create a new Python application**:
    - Select Python version (3.11+ recommended).
    - Set the application root to the `flask_ui` folder.
    - Set the application URL and entry point (e.g., `/flask_ui/app.py`).
    - The entry point should be: `app:app` (for Flask WSGI apps).
4. **Install dependencies**:
    - In the Python App setup, use the "Enter to install requirements" field:
      ```sh
      pip install -r /home/yourcpaneluser/path/to/requirements.txt
      ```
    - Or upload a requirements.txt file and install via the cPanel UI.
5. **Set environment variables** (if needed):
    - Use the cPanel Python App UI to add any required environment variables (e.g., API keys, FLASK_ENV).
6. **Restart the Python app** from the cPanel interface after making changes.
7. **Static files**:
    - Ensure the `static/` and `templates/` folders are in the app root.
    - If using a custom domain or subdomain, map it to the app’s public URL.
8. **Troubleshooting**:
    - Check the "Error Log" in cPanel for Python app errors.
    - Ensure file permissions are correct (typically 644 for files, 755 for folders).
    - If you see import/module errors, verify the virtual environment and installed packages.
    - For WSGI errors, confirm the entry point is `app:app` and the working directory is correct.

For more details, see cPanel’s official documentation or contact your hosting provider’s support.

---

## Maintenance & Future Management
- **Dependencies**: All required packages are listed in `requirements.txt`. Use `pip install -r requirements.txt` to update.
- **Python Version**: Use Python 3.11+ for best compatibility.
- **Environment**: Always activate the virtual environment before running the app.
- **API Changes**: If the business API contract changes, update the `API_URL` and payload logic in `app.py`.
- **Branding**: To update branding, replace logo URLs and static assets in the `static/` folder and update styles in `index.html`.
- **PDF Template**: To change the PDF layout, edit `pdf_report.html`.
- **Spinner**: To update the loading spinner, replace `spinner_2.gif` and adjust the JS/CSS in `index.html`.
- **Security**: Never commit real API keys or sensitive data. Use environment variables for secrets if needed.
- **Error Handling**: All errors are displayed to the user. For production, consider logging errors to a file or monitoring service.
- **Testing**: Manual testing is recommended after any major change. Automated tests can be added in the `tests/` folder.

---

## Handover & Support
- **Documentation**: This file should be shared with all future developers and stakeholders.
- **Support**: For technical support, ensure the new team has access to the codebase, this documentation, and any API credentials.
- **Non-Technical Handover**: Provide a walkthrough of the UI, key features, and how to reset or update branding.
- **Backup**: Regularly back up the project folder and database (if used in the future).

---

## Contact
For further questions or support, please contact the original developer or project manager.
