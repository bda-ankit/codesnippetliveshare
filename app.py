from flask import Flask, request, render_template, redirect, url_for, abort, jsonify
import time
import os
import json
import random
import string

app = Flask(__name__, template_folder='templates')

# Directory to store the content files
CONTENT_DIR = 'content_files'
os.makedirs(CONTENT_DIR, exist_ok=True)

# Duration for which content is valid (10 seconds for demo purposes)
CONTENT_EXPIRY_DURATION = 24*60*60

def get_content_file_path(url):
    return os.path.join(CONTENT_DIR, f"{url}.json")

def is_content_expired(timestamp):
    return (time.time() - timestamp) > CONTENT_EXPIRY_DURATION

def generate_unique_id(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@app.route('/generate', methods=['POST'])
def generate():
    unique_id = generate_unique_id()
    file_path = get_content_file_path(unique_id)
    
    if request.is_json:
        data = request.get_json()
        content = data.get('content', '')
        timestamp = time.time()
        with open(file_path, 'w') as f:
            json.dump({'content': content, 'timestamp': timestamp}, f)
        
        return jsonify({'url': f'/{unique_id}'})

    if is_content_expired(data['timestamp']):
        os.remove(file_path)
        return abort(404, description="Content expired.")
    return abort(400, description="Invalid request")

@app.route('/<path:endpoint>', methods=['GET', 'POST'])
def handle_content(endpoint):
    file_path = get_content_file_path(endpoint)

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            content = data.get('content', '')
            timestamp = time.time()
            with open(file_path, 'w') as f:
                json.dump({'content': content, 'timestamp': timestamp}, f)
            return jsonify({'status': 'success'})

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        content = data['content']
        if is_content_expired(data['timestamp']):
            os.remove(file_path)
            return abort(404, description="Content expired.")
    else:
        content = ""

    return render_template('index.html', content=content)

if __name__ == '__main__':
    app.run(debug=True)