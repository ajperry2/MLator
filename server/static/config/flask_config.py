import os

# get database info from file (dont hardcode!)
db_name = 'mlator'


def getDBConString(db_name):
    db = {}
    with open('product-analytics-group7/server/databases.csv', 'r') as db_file:
        for line in db_file.readlines():
            db_info = line.split(',')
            if db_info[3] == db_name:
                db['username'] = db_info[0]
                db['password'] = db_info[1]
                db['endpoint'] = db_info[2]
                db['instance'] = db_info[3]
                break

    return 'postgresql+psycopg2://{}:{}@{}/{}' \
        .format(db['username'], db['password'], db['endpoint'], db['instance'])


class Config(object):
    FLASK_APP = 'MLATOR'
    SECRET_KEY = 'supes secret'
    # Database Options
    DATABASE_URL = getDBConString(db_name)
    SQLALCHEMY_DATABASE_URI = getDBConString(db_name)
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    # Options related to file upload
    DROPZONE_ENABLE_CSRF = True
    DROPZONE_UPLOAD_ACTION = 'upload'  # URL or endpoint
    DROPZONE_ALLOWED_FILE_TYPE = 'image'
    DROPZONE_MAX_FILE_SIZE = 3
    DROPZONE_MAX_FILES = 20
    DROPZONE_UPLOAD_MULTIPLE = True
    DROPZONE_PARALLEL_UPLOADS=3 # set parallel amount

    PATH = 'product-analytics-group7/server/static/stored/'
    UPLOADED_PATH = os.path.join(os.getcwd(), PATH)
    UPLOADED_PHOTOS_DEST = os.path.join(os.getcwd(), PATH)
    # Options Related to Flask Bootstrap
    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_SERVE_LOCAL = False
    BOOTSTRAP_LOCAL_SUBDOMAIN = 'product-analytics-group7/server/static/'
    BOOTSTRAP_QUERYSTRING_REVVING = False
