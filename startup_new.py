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
from pprint import pprint



app = Flask(__name__)
# with open('/home/nikhilmanvesh/GlobalLinkLLC_app_credentials.json', mode='r') as f:
#     global_link_creds = json.load(f)

cors = CORS(app, resources={r'/*': {'origins': '*'}})
app.config['CORS_HEADERS'] = 'Content-Type'
# session = SessionGenerator().get_session()

# with open(glob('/home/ni**ma**/aw**_k**.json')[0]) as f:
#     aws_creds = json.load(f)
# os.environ['AWS_access_key_id'] = aws_creds['AWS_access_key_id']
# os.environ['AWS_secret_access_key'] = aws_creds['AWS_secret_access_key']

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
    # session_obj = session()
    # with open(glob('/home/ni**/a**_k**.json')[0]) as f:
        # aws_creds = json.load(f)
    # db_client = boto3.resource('dynamodb', 
    #                          aws_access_key_id=aws_creds['AWS_access_key_id'], 
    #                          aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
    #                          region_name='eu-north-1')
    db_client = boto3.resource('dynamodb', 
                             aws_access_key_id=os.environ['AWS_access_key_id'], 
                             aws_secret_access_key=os.environ['AWS_secret_access_key'], 
                             region_name='eu-north-1')
    if request.method == 'POST':
        _username = request.form['username']
        _password = generate_password_hash(request.form['password'])
        _email = request.form['email']
        # session_obj.add(
        #     User(username=_username, 
        #          password=_password, 
        #          email=_email)
        # )
        # session_obj.commit()
        # session_obj.close()
        table = db_client.Table('UsersDB')
        print('table ---> ', table)
        res = table.get_item(Key={'username': _username})
        # print(res['Item'])
        res_one = table.scan(FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(_email))
        # print(res_one['Items'])
        if res.get('Item'):
            return {'message': 'username is not available'}
        elif res_one.get('Items'):
            return {'message': 'Please enter correct email'}

        try:
            _table = db_client.create_table(TableName='UsersDB', 
                                            KeySchema=[
                                                {'AttributeName': 'username', 'KeyType': 'HASH'}
                                            ], 
                                            AttributeDefinitions=[
                                                {'AttributeName': 'username', 'AttributeType': 'S'}
                                            ], 
                                            ProvisionedThroughput={
                                                'ReadCapacityUnits': 5, 
                                                'WriteCapacityUnits': 5
                                            })
        except Exception as ex:
            # return {'Message': str(ex)}
            _table = db_client.Table('UsersDB')
            _table.put_item(Item={'username': _username, 'password': _password, 'email': _email})
            return 'Hi, ' + _username
        else:
            _table.put_item(Item={'username': _username, 'password': _password, 'email': _email})
            return 'Hi, ' + _username

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
    # with open(glob('/home/ni**/a**_k**.json')[0]) as f:
    #     aws_creds = json.load(f)
    # db_client = boto3.resource('dynamodb', 
    #                          aws_access_key_id=aws_creds['AWS_access_key_id'], 
    #                          aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
    #                          region_name='eu-north-1')
    db_client = boto3.client('dynamodb', 
                             aws_access_key_id=os.environ['AWS_access_key_id'], 
                             aws_secret_access_key=os.environ['AWS_secret_access_key'], 
                             region_name='eu-north-1')
    # session_obj = session()
    if request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        # user_records = session_obj.query(User).all()
        # actual_user_records = [(user_record.username, user_record.password) for user_record in user_records]
        # if actual_user_records:
        #     for actual_user in actual_user_records:
        #         if actual_user[0] == _username and check_password_hash(actual_user[-1], _password):
        #             return 'Welcome ' + _username.capitalize()
        #     else:
        #         return 'Invalid Credentials'
        
        table = db_client.Table('UsersDB')
        print('table ---> ', table)
        res = table.get_item(Key={'username': _username})
        # print(res['Item'])
        if res.get('Item') and check_password_hash(res.get('Item').get('password'), _password):
            return 'Welcome ' + _username.capitalize()
        else:
            return 'Please Signup'

    return \
    """
    <form method="POST">
        Username: <input name="username" required><br>
        Password: <input name="password" required><br>
        <button>Login</button>
    </form>
    """

@app.route('/test-dynamodb', methods=['GET', 'POST'])
def dynamoDB_database():
    # with open(glob('/home/ni**/a**_k**.json')[0]) as f:
    #     aws_creds = json.load(f)
    # print(aws_creds)
    # # db_client = boto3.client('dynamodb', 
    # #                          aws_access_key_id=aws_creds['AWS_access_key_id'], 
    # #                          aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
    # #                          region_name='eu-north-1')
    # db_client = boto3.resource('dynamodb', 
    #                          aws_access_key_id=aws_creds['AWS_access_key_id'], 
    #                          aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
    #                          region_name='eu-north-1')
    # print('dynamoDB_client ---> ', db_client)
    db_client = boto3.client('dynamodb', 
                             aws_access_key_id=os.environ['AWS_access_key_id'], 
                             aws_secret_access_key=os.environ['AWS_secret_access_key'], 
                             region_name='eu-north-1')
    if request.method == 'GET':
        try:
            # test_data = {'user_name': 'Mike', 'password': 'mike123@', 'email': 'mike@gmail.com'}
            test_data = {"username": "Mike", 
                         "password": "mike123@", 
                         "email": "mike@gmail.com"}
            print('test_data ---> ', test_data)
            # _table = db_client.Table('users_table')
            # _table = db_client.create_table(TableName='UsersData', 
            #                                 KeySchema=[
            #                                     {'AttributeName': 'username', 'KeyType': 'HASH'}
            #                                 ], 
            #                                 AttributeDefinitions=[
            #                                     {'AttributeName': 'username', 'AttributeType': 'S'}
            #                                 ], 
            #                                 ProvisionedThroughput={
            #                                     'ReadCapacityUnits': 5, 
            #                                     'WriteCapacityUnits': 5
            #                                 })
            _table = db_client.Table('UsersData')
            print('=== About to create a table ===')
            # _table.wait_until_exists()
            print('table ---> ', _table)
            # _table.put_item(Item=json.dumps(test_data))
            _table.put_item(Item=test_data)
        except Exception as ex:
            return {'Error Message': type(ex)}
        else:
            return {'Message': 'Data inserted successfully'}


@app.route('/upload-to-S3', methods=['POST', 'GET'])
def upload_data_to_AmazonS3():
    # with open(glob('/home/ni**/a**_k**.json')[0]) as f:
    #     aws_creds = json.load(f)
    # print(aws_creds)
    # s3_client = boto3.client('s3', 
    #                          aws_access_key_id=aws_creds['AWS_access_key_id'], 
    #                          aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
    #                          region_name='eu-north-1')
    s3_client = boto3.client('s3', 
                             aws_access_key_id=os.environ['AWS_access_key_id'], 
                             aws_secret_access_key=os.environ['AWS_secret_access_key'], 
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
    # print('category ---> ', category)
    images_list = os.listdir('static/Products/%s' % category.capitalize())
    # with open(glob('/home/ni**ma**/aw**_k**.json')[0]) as f:
    #     aws_creds = json.load(f)
    # s3_client = boto3.client('s3', 
    #                          aws_access_key_id=aws_creds['AWS_access_key_id'], 
    #                          aws_secret_access_key=aws_creds['AWS_secret_access_key'], 
    #                          region_name='eu-north-1')
    s3_client = boto3.client('s3', 
                             aws_access_key_id=os.environ['AWS_access_key_id'], 
                             aws_secret_access_key=os.environ['AWS_secret_access_key'], 
                             region_name='eu-north-1')
    # _buckets = s3_client.list_buckets()
    _category = category.capitalize()
    res = s3_client.list_objects_v2(Bucket='global-link-llc-bucket', 
                                    Prefix=_category + '/')
    # print('res ---> ', res)
    # pprint(res['Contents'][0]['Key'])
    category_contents = [_content['Key'] for _content in res['Contents']]
    # print('category_contents ---> ', category_contents)
    urls_list = []
    for category_content in category_contents:
        # object_data = s3_client.get_object(Bucket='global-link-llc-bucket', 
                                            # Key=category_content)
        # print('object_data ---> ', object_data, end='\n\n')
        # pprint(object_data)
        # res = object_data['Body'].read().decode('utf-8')
        # res = object_data['Body'].read()
        # print(res)
        _url = s3_client.generate_presigned_url(
            'get_object', 
            Params={'Bucket': 'global-link-llc-bucket', 'Key': category_content}, 
            ExpiresIn=3600
        )
        urls_list.append(_url)
    # print('urls_list ---> ', urls_list)

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
    html_template_new = \
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
            {% for __url in urls_list %}
            <img src="{{ __url }}" alt="{{ image }}">
            {% endfor %}
        </div>
    </body>
    </html>
    """
    # return jsonify(images_list)
    return render_template_string(html_template_new, urls_list=urls_list, _category=_category)

def payment_gateway_integration():
    ...

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
