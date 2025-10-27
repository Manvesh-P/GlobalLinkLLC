from flask import Flask, jsonify, render_template_string, request
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# from realesrgan import RealESRGAN
from PIL import Image
from mysql.connector import connect
from flask_cors import CORS, cross_origin
import json
from werkzeug.security import (generate_password_hash, 
                               check_password_hash)
from session_maker import SessionGenerator
from models import User
import boto3
from glob import glob


app = Flask(__name__)
# with open('/home/nikhilmanvesh/GlobalLinkLLC_app_credentials.json', mode='r') as f:
#     global_link_creds = json.load(f)

cors = CORS(app, resources={r'/*': {'origins': '*'}})
app.config['CORS_HEADERS'] = 'Content-Type'
session = SessionGenerator().get_session()


cross_origin(
origins = '*', 
methods = ['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT'], 
headers = None, 
supports_credentials = False, 
max_age = None, 
send_wildcard = True, 
always_send = True, 
automatic_options = False
)

def database_connectivity():
    _connection = connect(user='nikhilmanvesh', 
                          password='Nikhil123', 
                          database='GlobalLink', 
                          host='localhost')
    return _connection


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # session = SessionGenerator().get_session()
    session_obj = session()
    if request.method == 'POST':
        _username = request.form['username']
        _password = generate_password_hash(request.form['password'])
        _email = request.form['email']
        session_obj.add(
            User(username=_username, 
                 password=_password, 
                 email=_email)
        )
        session_obj.commit()
        session_obj.close()
    return \
    """
    <form method="POST">
        User Name: <input name="username" required><br>
        Password: <input name="password" required><br>
        Email: <input name="email"><br>
        <button>Sign Up</button>
    </form>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    session_obj = session()
    if request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        user_records = session_obj.query(User).all()
        actual_user_records = [(user_record.username, user_record.password) for user_record in user_records]
        if actual_user_records:
            for actual_user in actual_user_records:
                if actual_user[0] == _username and check_password_hash(actual_user[-1], _password):
                    return 'Welcome ' + _username.capitalize()
            else:
                return 'Invalid Credentials'
    return \
    """
    <form method="POST">
        Username: <input name="username" required><br>
        Password: <input name="password" required><br>
        <button>Login</button>
    </form>
    """

@app.route('/upload-to-S3', methods=['POST', 'GET'])
def upload_data_to_AmazonS3():
    with open(glob('/home/ni**/a**_k**.json')[0]) as f:
        aws_creds = json.load(f)
    print(aws_creds)
    s3_client = boto3.client('s3', 
                             aws_access_key_id=aws_creds['AWS_access_key_id'], 
                             aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
                             region_name='eu-north-1')
    # bucket_name = 'global-link-llc-bucket'
    pay_load = request.json
    print('payload ---> ', pay_load)
    bucket_name = pay_load['bucket_name']
    # folder_path = glob('/home/ni**/Gl**L**/Ba**/st**/Pr**/')[0]
    local_folder_path = pay_load['local_folder_path']

    try:
        for inner_folder_path, _, _images in list(os.walk(local_folder_path))[1: ]:
            for _image in _images:
                s3_folder_name = inner_folder_path.split('/')[-1]
                s3_client.upload_file(f'{inner_folder_path}/{_image}', bucket_name, f'{s3_folder_name}/{_image}')
    except Exception as ex:
        return {'error': str(ex)}
    else:
        return {'message': 'sucess'}

@app.route('/scrape_wix_data/', methods=['GET'])
@cross_origin
def scrape_wix_data():
    categories = ['dental', 'janitorial', 'medical', 'bandages', 'medical-blanket-emergency', 
                  'catheters', 'custom-kits', 'surgical-gowns', 'medical-bleach-and-alcohol', 
                  'medical-facemask', 'medical-gloves', 'medical-hand-sanitizer', 
                  'medical-hygiene-kits', 'medical-oximeters', 'medical-syringes', 
                  'medical-wipes', 'janitorial-kleenex', 'respiratory', 'soap']
    # categories = ['dental']
    # _model = RealESRGAN(device='cpu')
    # _model.load_weights('RealESRGAN_x4.pth')

    for _category in categories:
        BASE_URL = f'https://www.myglobal-link.net/category/{_category}'
        DIR_NAME = 'static/Products/' + _category.capitalize()
        try:
            os.mkdir(DIR_NAME)
        except Exception as e:
            ...
        _res = requests.get(url=BASE_URL)
        _soup = BeautifulSoup(_res.text, 'lxml')
        _images = _soup.find_all('img')
        for _image in _images:
            _image_url = _image.get('src') or _image.get('data-src')
            if not _image_url or 'GLOBAL' in _image_url:
                continue
            
            full_url = urljoin(BASE_URL, _image_url)
            print('full_url ---> ', full_url)
            file_name = os.path.basename(full_url.split('?')[0])
            file_path = os.path.join(DIR_NAME, file_name)

            image_desc = _image.get('alt')
            print('image_desc ---> ', image_desc)

            try:
                # _data = requests.get(full_url).content
                # with open(file_path, mode='wb') as f:
                #     f.write(_data)
               _data = requests.get(full_url.split('/v1')[0], stream=True)
               with open(file_path, mode='wb') as f:
                   for _chunk in _data.iter_content(chunk_size=1024):
                       f.write(_chunk)

            except Exception as ex:
                ...
            # _img = Image.open(file_path).convert('RGB')
            # _result = _model.predict(_img)
            # _result.save(DIR_NAME + '_HD/' + file_name)

            # _img = Image.open(file_path)
            # _img.save(file_path.replace('.JPEG', '.png').replace('.jpg', '.png').replace('.jpeg', '.png'))
    return jsonify({"message": "Scrapping Done Successfully"})

@app.route('/render_products/<category>', methods=['GET'])
def render_products(category):
    print('category ---> ', category)
    images_list = os.listdir('static/Products/%s' % category.capitalize())
    _category = category.capitalize()
    html_template = \
    """
    <!DOCTYPE html>
    <html>
    <head>
        <title>|| Global Link ||</title>
        <style>
            body {
                background: #f9f9f9;
                font-family: Arial, sans-serif;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-top: 30px;
            }
            .grid {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                margin: 20px;
            }
            .grid img {
                width: 200px;
                margin: 10px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                transition: transform 0.2s;
            }
            .grid img:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <h1>Product Gallery</h1>
        <div class="grid">
            {% for image in images_list %}
            <img src="{{ url_for('static', filename='Products/' ~ _category  ~ '/' + image) }}" alt="{{ image }}">
            {% endfor %}
        </div>
    </body>
    </html>
    """
    # return jsonify(images_list)
    return render_template_string(html_template, images_list=images_list, _category=_category)

def payment_gateway_integration():
    ...

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
