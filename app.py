import os
import sys
import json
import random
import string

from flask import Flask, request, redirect, url_for, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from db import Database

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["UPLOAD_FOLDER"] = './uploads'
server_url = "http://hrfarmer.live"

try:
    _x = sys.argv[1]
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

#For shortlink generation
def generate_shortlink():
    database = Database()
    while True:
        characters = string.ascii_letters + string.digits
        final_string = ''.join(random.choice(characters) for i in range(10))
        d = database.return_path(final_string)
        if d != None:
            continue
        else:
            return final_string


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(400)
def no_permission(error):
    return {"error": "The key provided is invalid"}, 400

@app.errorhandler(401)
def no_key(error):
    return {"error": "No key provided"}, 401

@app.errorhandler(403)
def file_error(error):
    return {"erorr": "There is an issue with the file provided, please try again or try a differnt file."}, 403

@app.errorhandler(404)
def invalid_link(error):
    return {"error": "This link is invalid"}

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    database = Database()

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
    
    shortlink = generate_shortlink()
    database.add_link(os.path.join(path, filename), shortlink)

    response = {
        "data": {
            "link": f"{server_url}/{shortlink}"
        }
    }

    r = json.dumps(response)
    return r

@app.route('/<prefix>/<name>')
def download_file(name, prefix):
    directory = os.path.join(app.config["UPLOAD_FOLDER"], prefix)
    return send_from_directory(directory, name)

@app.route('/<shortlink>')
def open_shortlink(shortlink):
    database = Database()

    path = database.return_path(shortlink)
    if path == None:
        abort(404)

    split_path = os.path.split(path[0])
    return send_from_directory(split_path[0], split_path[1])
    
if __name__ == "__main__":
    app.run()
