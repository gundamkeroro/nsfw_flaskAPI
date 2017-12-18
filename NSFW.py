import os
import uuid
from flask import Flask, request
from werkzeug.utils import secure_filename
import json
import Model
import subprocess

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/nsfw', methods=['POST'])
def nsfw():
    if 'file' not in request.files:
        return 'Error!'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = str(uuid.uuid4()) + '.jpg'
        file.save(os.path.join('/home/ubuntu/open_nsfw/', filename))
        res = Model.run(filename)
        subprocess.call("rm " + filename, shell=True)        
        return json.dumps({"probs" : res})
    return 'no such file'

if __name__ == '__main__':
    app.run(host= '0.0.0.0')

