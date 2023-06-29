import os
import sys
import json
import random
import string
import requests

from flask import Flask, request, redirect, url_for, render_template, send_from_directory, abort
from werkzeug.utils import secure_filename
from db import Database
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["UPLOAD_FOLDER"] = './uploads'
server_url = "https://hrfarmer.live"

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

try:
    print(sys.argv)
    _x = sys.argv[1]
    if _x == "test":
        print("Testing mode on")
        server_url = "http://localhost:5000"
except IndexError:
    pass

json_exists = os.path.exists("keys.json")
if json_exists == False:
    default_key = {"default": "key"}
    key_dict = json.dumps(default_key)

    with open("keys.json", "w") as f:
        f.write(key_dict)

f = open('keys.json')
keys = json.load(f)
key_list = list(keys.values())


# For shortlink generation
def generate_shortlink():
    database = Database()
    while True:
        characters = string.ascii_letters + string.digits
        final_string = ''.join(random.choice(characters) for i in range(10))
        d = database.return_path(final_string)
        if d is not None:
            continue
        else:
            return final_string


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(400)
def no_permission(error):
    return {"error": "No permission!!!! (maybe key invalid or something broke)"}, 400


@app.errorhandler(401)
def no_key(error):
    return {"error": "No key provided"}, 401


@app.errorhandler(403)
def file_error(error):
    return {"error": "There is an issue with the file provided, please try again or try a differnt file."}, 403


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
            "link": f"{server_url}/a/{shortlink}"
        }
    }

    r = json.dumps(response)
    return r


@app.route('/a/<shortlink>')
def open_album(shortlink):
    # database = Database()

    # path = database.return_path(shortlink)
    # if path is None:
    #     abort(404)

    # filepath = f"{server_url}/upload/{shortlink}"

    # data = {'link': filepath, 'shortlink': shortlink, 'server_path': path[1]}
    # return render_template('filepage.html', data=data)
    database = Database()

    path = database.return_path(shortlink)
    if path == None:
        abort(404)

    split_path = os.path.split(path[0])
    return send_from_directory(split_path[0], split_path[1])


@app.route('/upload/<shortlink>')
def open_file(shortlink):
    database = Database()

    path = database.return_path(shortlink)
    if path == None:
        abort(404)

    split_path = os.path.split(path[0])
    return send_from_directory(split_path[0], split_path[1])


@app.route('/auth')
def twitch_auth():
    print(request.url)
    if request.url == f"{server_url}/auth":
        return redirect(
            f"https://id.twitch.tv/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={server_url}/auth&scope=user%3Aread%3Afollows+user%3Aread%3Aemail")

    db = Database()
    code = request.args['code']

    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"{server_url}/auth"
    }
    response = requests.post("https://id.twitch.tv/oauth2/token", params=params)
    response_json = json.loads(response.content.decode('utf8'))
    access_token = response_json['access_token']
    refresh_token = response_json['refresh_token']

    r = requests.get("https://api.twitch.tv/helix/users",
                     headers={"Authorization": f"Bearer {access_token}", "Client-Id": client_id})
    r_json = json.loads(r.content.decode('utf8'))

    username = r_json['data'][0]['login']
    email = r_json['data'][0]['email']
    db.new_user(username, email, access_token, refresh_token, 'user')

    return redirect(url_for('file_page', key=access_token))


@app.route('/files')
def file_page():
    return render_template('files.html')


if __name__ == "__main__":
    app.run()
