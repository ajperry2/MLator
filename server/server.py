from flask import (Flask, redirect, render_template, request, url_for, jsonify,
                   session, flash, send_file, send_from_directory)
from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user, UserMixin)
import wtforms
from wtforms.validators import DataRequired, Email
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.fields.html5 import EmailField
from wtforms import SubmitField, StringField, PasswordField
from werkzeug import secure_filename
import time
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_uploads import (UploadSet, IMAGES, configure_uploads,
                           patch_request_class)
import boto3
import os

os.environ[
           "GOOGLE_APPLICATION_CREDENTIALS"] = ("product-analytics-group7/"
                                                "server/nmt-API-07b7802bb743.json")
import main_func
from glob import glob
import zipfile
from io import BytesIO

db_name = 'mlator'
model, model2 = main_func.model_load(
                                     'product-analytics-group7/server/checkpoint')
model._make_predict_function()
model2._make_predict_function()
# load models once the server set up
# model, model2 = main_func.model_load(
# 'product-analytics-group7/server/checkpoint')

# Create and configure an app.
app = Flask(__name__)

app.config.from_object('static.config.flask_config.Config')
db = SQLAlchemy(app)
migration = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'home'


# order_data = pd.read_csv('order_data.csv')


# configure_uploads(app, photos) # no photos var?


class User(UserMixin, db.Model):
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_authenticated = False
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
    
    def is_authenticated():
        return self.is_authenticated
    
    def set_authenticated(authenticated):
        self.is_authenticated = authenticated
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_user_name(self):
        return self.username


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    projectname = db.Column(db.String(80), unique=True, nullable=False)
    numimages = db.Column(db.Integer, unique=False, nullable=False)
    cost = db.Column(db.Float, unique=False, nullable=False)
    
    def __init__(self, username, projectname, numimages, cost):
        self.username = username
        self.email = email
        self.set_password(password)


class UploadFileForm(FlaskForm):
    """Class for uploading file when submitted"""
    file_selector = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Submit')


# return Book pictures
@app.route('/pages/<book>/<size>/<page>', methods=['GET', 'POST'])
def images(book, size, page):
    if size == 'regular':
        return redirect(url_for('static', filename='images/' + book + '/' + page + '.jpg'))
    elif size == 'large':
        return redirect(url_for('static',filename='images/' + book + '/' + page + '-large.jpg'))
    elif size == 'thumb':
        return redirect(url_for('static',filename='images/' + book + '/' + page + '-thumb.jpg'))
    elif size == 'regions':
        return redirect(url_for('static',filename='images/' + book + '/' + page + '-regions.json'))


@app.route('/', methods=['GET', 'POST'])
def foo():
    return redirect(url_for('home'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    filename = ''
    if 'file_urls' in session: filename = session['file_urls'][0]
    filename = ''
    login_form = LoginForm()
    register_form = RegisterForm()
    login = render_template('login.html', form=login_form)
    register = render_template('signup.html', form=register_form)
    return render_template('home.html',
                           loginForm=login_form,
                           registerForm=register_form,
                           login=login,
                           register=register,
                           filename=filename)


@app.route('/translated/<translation>', methods=['GET', 'POST'])
def translated(translation):
    print(translation)
    return send_from_directory('static/translated/', translation)


# FORMS
class RegisterForm(FlaskForm):
    useremail = EmailField('User Email',
                           [DataRequired(), Email()],
                           id='emailRegister')
    username = StringField('User Name', [DataRequired()], id='userRegister')
    password = StringField('Password', [DataRequired()], id='passwordRegister')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('User Name', [DataRequired()], id='userLogin')
    userpassword = PasswordField('Password', [DataRequired()],
                                 id='passwordLogin')
    submit = SubmitField('Log In')


# Validate Forms Without refreshing (handle AJAX requests)
@app.route('/checkRegister', methods=['POST'])
def checkRegister():
    form = RegisterForm(request.form)
    messages = []
    
    user = User.query.filter_by(username=form.username.data).first()
    user_name_count = User.query.filter_by(username=form.username.data).count()
    user_email_count = User.query.filter_by(email=form.useremail.data).count()
    message = []
    
    # Add validation messages
    if form.validate():
        if (user_name_count > 0):
            message.append('This User Name is taken')
        if (user_email_count > 0):
            message.append('This Email is in use')
        # Register User
        if (user_name_count == 0) and (user_email_count == 0):
            current_user = User(form.username.data, form.useremail.data,
                                form.password.data)
            current_user.authenticated = True
            db.session.add(current_user)
            db.session.commit()
            login_user(current_user, remember=True)

        if len(message) > 0:
            # "not valid"
            return jsonify(data={'messages': message})
        else:
    # "valid"
                return jsonify(data={'messages': False})
    else:
        return jsonify(data={'messages': message})


@app.route('/checkPassword', methods=['POST'])
def checkPassword():
    form = LoginForm(request.form)
    messages = []
    user = User.query.filter_by(username=form.username.data).first()
    if form.validate():
        if user is None or not user.check_password(form.userpassword.data):
            messages.append('Username or Passord is not correct')
        if len(messages) > 0:
            return jsonify(data={'messages': messages})
        else:
            user = User.query.filter_by(username=form.username.data).first()
            
            login_user(user)
            return jsonify(data={'messages': False})  # form.data
    else:
        return jsonify(data={'messages': message})


# User Mangement
@login_manager.user_loader
def load_user(id):  # id is the ID in User.
    return User.query.get(int(id))


# User Account Page
@app.route('/user/<username>')
@login_required
def user(username):
    form = UploadFileForm()
    return render_template('user.html', uploaded=False)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/form', methods=['POST'])
def handle_form():
    title = request.form.get('title')
    description = request.form.get('description')
    return 'file uploaded and form submit<br>title: %s<br> description: %s' % (
                                                                               title, description)


@app.route('/upload_form', methods=['POST'])
def handle_upload():
    for key, f in request.files.items():
        if key.startswith('file'):
            f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return '', 204


@app.route('/upload_demo', methods=['GET', 'POST'])
def upload_demo():
    """upload a file from a client machine.
        returns: a translated picture with demo written on it"""
    # Check if it is a POST request and if it is valid.
    if "file_urls" not in session:
        session['file_urls'] = []
    file_urls = session['file_urls']
    uploaded = False
    fn = ''
    if request.method == 'POST':
        print('inupload')
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            filename = photos.save(file, name='demo_' + secure_filename(
                                                                        file.filename))
            print('saving:', 'demo_' + secure_filename(file.filename))
            file_urls.append('demo_' + secure_filename(file.filename))
            tmp_path = "product-analytics-group7/server/static/stored"
            tmp2 = "product-analytics-group7/server/static/translated"
            main_func.main(os.path.join(tmp_path, filename),
                           os.path.join(tmp2, 'demo_' + secure_filename(
                                                                        file.filename)), model, model2, True)
            fn = secure_filename(file.filename.split('/')[-1])
            print('returning:',
                  url_for('translated', translation='demo_' + fn))
            return url_for('translated', translation='demo_' + fn)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """upload a file from a client machine."""
    # Check if it is a POST request and if it is valid.
    print('in upload!')
    if "file_urls" not in session:
        session['file_urls'] = []
    file_urls = session['file_urls']
    uploaded = False
    if request.method == 'POST':
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            filename = photos.save(file, name=secure_filename(file.filename))
            file_urls.append(secure_filename(file.filename))
            
            tmp_path = "product-analytics-group7/server/static/stored"
            tmp2 = "product-analytics-group7/server/static/translated"
            print(os.path.join(tmp2, "trn_" + filename))
            main_func.main(os.path.join(tmp_path, filename),
                           os.path.join(tmp2, 'trn_' + secure_filename(
                                                                       file.filename)), model, model2, False)
        
        session['file_urls'] = file_urls
        print(session['file_urls'])
        return 'uploading...'

    return render_template('user.html', file_urls=file_urls, uploaded=False)



@app.route('/download', methods=['GET', 'POST'])
@login_required
def download():
    zip_buffer = BytesIO()
    uploads = "product-analytics-group7/server/static/translated/*"
    
    def f(x):
        return secure_filename(x.split('/')[-1])
    
    curr_files = [f(file) for file in session['file_urls']]
    print("curr_files:", curr_files)
    available_files = [file.split('/')[-1] for file in glob(uploads)]
    print("secure_filename:", [secure_filename(x) for x in available_files])
    
    to_download = []
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for curr_file in curr_files:
            if 'trn_' + curr_file in [secure_filename(x) for x in
                                      available_files]:
                to_download.append('trn_' + curr_file)
                print('trn_' + curr_file)
                
                zip_file.write(os.path.join(
                                "product-analytics-group7/server/static/translated",
                                'trn_' + curr_file),
                                curr_file)

    zip_buffer.seek(0)
    return send_file(zip_buffer,
                     mimetype='zip',
                     attachment_filename='Translated.zip',
                     as_attachment=True)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/account')
def account():
    return render_template('account.html')


@app.after_request
def add_header(request):
    """Controls for the caching of our site
        """
    request.headers["Cache-Control"] = "must-revalidate"
    request.headers["Pragma"] = "no-cache"
    request.headers["Expires"] = "0"
    request.headers['Cache-Control'] = 'public, max-age=0'
    return request


@app.errorhandler(CSRFError)
def csrf_error(e):
    return e.description, 400


if __name__ == '__main__':
    # s3 info
    #    s3 = boto3.client('s3')
    #    result = s3.get_bucket_policy(Bucket='mlator-photos')
    #    print(result['Policy'])
    #
    # login_manager needs to be initiated before running the app
    login_manager.init_app(app)
    login_manager.login_message = u""
    # flask-login uses sessions which require a secret Key
    app.secret_key = os.urandom(24)
    
    dropzone = Dropzone(app)
    csrf = CSRFProtect(app)
    
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)
    patch_request_class(app)
    
    # Create tables.
    db.create_all()
    db.session.commit()
    
    bootstrap = Bootstrap(app)
app.run(host='0.0.0.0', port=5000, debug=True)
