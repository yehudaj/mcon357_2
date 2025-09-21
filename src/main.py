from flask import Flask, render_template, jsonify, request
from datetime import datetime
import platform
import os
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_message')
def get_message():
    # Get current timestamp in different formats
    current_time = datetime.now()
    
    # Create a complex JSON structure
    server_data = {
        "message": "Hello from the server! This message came through AJAX!",
        "timestamp": {
            "full": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "unix": int(current_time.timestamp())
        },
        "server_info": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "machine": platform.machine()
        },
        "request_data": {
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get('User-Agent'),
            "ip_address": request.remote_addr,
            "headers": dict(request.headers)
        },
        "environment": {
            "working_directory": os.getcwd(),
            "temp_directory": os.getenv('TEMP', 'Not Available'),
            "python_path": sys.executable
        }
    }
    
    return jsonify(server_data)

if __name__ == "__main__":
    # Allow running with a self-signed (adhoc) certificate for local testing.
    # Set environment variable FLASK_ADHOC_HTTPS=1 to enable HTTPS.
    use_https = os.getenv("FLASK_ADHOC_HTTPS", "0") == "1"

    if use_https:
        # ssl_context='adhoc' creates a temporary self-signed certificate.
        # On some systems you may need pyOpenSSL/cryptography installed in the venv.
        # Install with: pip install pyopenssl cryptography
        app.run(debug=True, host="0.0.0.0", port=5000, ssl_context='adhoc')
    else:
        app.run(debug=True, host="0.0.0.0", port=5000)
