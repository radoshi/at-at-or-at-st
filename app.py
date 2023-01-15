# Path: app.py
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
from pathlib import Path

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

# create a post route for /check that gets a file as a post request
@app.route('/check', methods=['POST'])
def check():
    # get the file from the post request
    file = request.files['file']

    # save the file to the uploads folder
    uploads = Path(app.instance_path)/'uploads'
    if not uploads.exists():
        os.makedirs(uploads)
    
    filename = uploads/secure_filename(file.filename)
    file.save(filename)

    print(f'File saved to {filename}')
    return render_template('result.html')

