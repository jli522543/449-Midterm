import functools
from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response, jsonify, current_app, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
import jwt
import datetime
from functools import wraps
from bson import ObjectId
from werkzeug.utils import secure_filename
import os

bp = Blueprint('auth', __name__, url_prefix='/auth')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Check if the username already exists
def is_username_unique(username):
    db = get_db()
    return db.users.count_documents({"username": username}) == 0

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return jsonify({'message':'Token is missing!'}), 403
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message':'Token is expired'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message':'Invalid token'}), 403

        return f(*args, **kwargs)

    return decorated

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().users.find_one({"_id": ObjectId(user_id)})
        print(g.user)
        print('hi')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        ##error handling - checks if username or password is empty
        if not username and not password:
            error = 'Username and password are required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        if error:
            response = make_response(render_template('auth/register.html', error=error))
            response.status_code = 400
            return response
        document = {
            "username": username,
            "password": generate_password_hash(password)
        }
        if is_username_unique(document["username"]):
            db.users.insert_one(document)
            return redirect(url_for("auth.login"))
        else:
            error = f"User {username} is already registered."
            response = make_response(render_template('auth/register.html', error=error))
            response.status_code = 409
            return response
            
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        ##error handling - checks if username or password is empty
        if not username and not password:
            error = 'Username and password are required.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        if error:
            response = make_response(render_template('auth/login.html', error=error))
            response.status_code = 400
            return response
        
        user = db.users.find_one({"username": username})

        if user is None:
            error = 'Incorrect username.'
            
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is not None:
            response = make_response(render_template('auth/login.html', error=error))
            response.status_code = 401
            return response

        session.clear()
        session['user_id'] = str(user['_id'])
        token = jwt.encode({'user': username, 'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=30)}, current_app.config['SECRET_KEY'])
        session['token'] = token
        return redirect(url_for('index'))

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    ##delete the cookies as well
    redirect_to_login = redirect(url_for('auth.login'))
    redirect_to_login.set_cookie("profileName", "", expires=0)
    return redirect_to_login

@bp.route('/delete', methods=['GET', 'POST'])
@token_required
def delete():
    user_id = session.get('user_id')
    db = get_db()
    if(db.users.delete_one({"_id": ObjectId(user_id)})):
        return redirect(url_for('auth.logout'))
    return jsonify({'message':'Something went wrong on our end'}), 500
    

@bp.route('/changeUserInfo', methods=('GET', 'POST'))
@token_required
def changeUserInfo():
    if request.method == 'POST':
        user_id = session.get('user_id')
        newUsername = request.form['changeUsername']
        newPassword = request.form['changePassword']
        error = None
        ##error handling - checks if username or password is empty
        if not newUsername and not newPassword:
            error = 'Username and password are required.'
        elif not newUsername:
            error = 'Username is required.'
        elif not newPassword:
            error = 'Password is required.'
        if error:
            response = make_response(render_template('auth/changeUserInfo.html', error=error))
            response.status_code = 400
            return response
        
        db = get_db()
        if(db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"username": newUsername, "password": generate_password_hash(newPassword)}})):
            return redirect(url_for('home.index'))
        return jsonify({'message':'Something went wrong on our end'}), 500

    return render_template('auth/changeUserInfo.html')

@bp.route('/setProfileName', methods=('GET', 'POST'))
@token_required
def setProfileName():
    if request.method == 'POST':
        error = None
        newProfile = request.form['profileName']
        if newProfile:
            redirect_to_index = redirect(url_for('home.index'))
            redirect_to_index.set_cookie("profileName", newProfile)
            return redirect_to_index
        else:
            error = "Profile name not provided."
            response = make_response(render_template('auth/setProfileName.html', error=error))
            response.status_code = 400
            return response
        
    return render_template('auth/setProfileName.html')

@bp.route('/uploadFile', methods=('GET', 'POST'))
@token_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('home.index', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>'''