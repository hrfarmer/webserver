import os
import sys
import json
from flask import Flask, request, redirect, url_for, send_from_directory, abort
from werkzeug.utils import secure_filename
from db import Database

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["UPLOAD_FOLDER"] = './uploads'
server_url = "http://hrfarmer.live"

database = Database()

try:
    _x = sys.argv[1]
    print(_x)
    if _x == "test":
        server_url = "http://127.0.0.1:5000"
except IndexError:
    pass
    
try:
    f = open('keys.json')
    keys = json.load(f)
except:
    print("json file broke")
    exit()

key_list = list(keys.values())

@app.errorhandler(400)
def no_permission(error):
    return {"error": "The key provided is invalid"}, 400

@app.errorhandler(401)
def no_key(error):
    return {"error": "No key provided"}, 401

@app.errorhandler(403)
def file_error(error):
    return {"erorr": "There is an issue with the file provided, please try again or try a differnt file."}, 403

@app.route('/', methods=['GET'])
def home():
    return "welcome to my amazing website"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'Auth' in request.headers:
        if request.headers['Auth'] in key_list:
            prefix = list(keys.keys())[list(keys.values()).index(request.headers['Auth'])]
        else:
            abort(400)
    else:
        abort(401)

    file = request.files['file']
    if file.filename == '':
        abort(403)
    
    filename = secure_filename(file.filename)
    
    if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], prefix)):
        path = os.path.join(app.config["UPLOAD_FOLDER"], prefix)
        file.save(os.path.join(path, filename))
    else:
        os.mkdir(os.path.join(app.config["UPLOAD_FOLDER"], prefix))
        path = os.path.join(app.config["UPLOAD_FOLDER"], prefix)
        file.save(os.path.join(path, filename))

    response = {
        "data": {
            "link": f"{server_url}{url_for('download_file', name=filename, prefix=prefix)}"
        }
    }

    r = json.dumps(response)
    return r

@app.route('/<prefix>/<name>')
def download_file(name, prefix):
    directory = os.path.join(app.config["UPLOAD_FOLDER"], prefix)
    return send_from_directory(directory, name)

if __name__ == "__main__":
    app.run()
