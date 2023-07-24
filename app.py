import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import flickrapi

app = Flask(__name__)
app.secret_key = '1234'  # Replace 'your_secret_key' with a real secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables a warning message
from werkzeug.security import check_password_hash, generate_password_hash

# This is your hardcoded user data
users = {
    "davis": generate_password_hash("test"),
    "davisdeaton": generate_password_hash("1234"),
    
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username], password):
            login_user(User(id=username, username=username, password_hash=users[username]))
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')


flickr = flickrapi.FlickrAPI('1abc2735254269820d503c03d527e4c9', '8ee50ae57a05f23c', cache=True)

@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        else:
            user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/set_privacy_metadata', methods=['POST'])
@login_required
def set_privacy_metadata():
    min_date = request.form.get('min_date')
    max_date = request.form.get('max_date')
    is_public = request.form.get('is_public')
    try:
        photos = flickr.photos.search(user_id=current_user.id, min_taken_date=min_date, max_taken_date=max_date)
        for photo in photos['photos']['photo']:
            flickr.photos.setPerms(photo_id=photo['id'], is_public=is_public, is_friend=0, is_family=0, perm_comment=0, perm_addmeta=0)
        flash("Privacy settings updated successfully", "success")
    except flickrapi.exceptions.FlickrError as e:
        flash('Flickr API error: {}'.format(e), 'error')
    return redirect(url_for('index'))

@app.route('/set_album_privacy', methods=['POST'])
@login_required
def set_album_privacy():
    album_id = request.form.get('album_id')
    is_public = request.form.get('is_public')
    try:
        photos = flickr.photosets.getPhotos(user_id=current_user.id, photoset_id=album_id)
        for photo in photos['photoset']['photo']:
            flickr.photos.setPerms(photo_id=photo['id'], is_public=is_public, is_friend=0, is_family=0, perm_comment=0, perm_addmeta=0)
        flash("Privacy settings updated successfully", "success")
    except Exception as e:
        logging.error(str(e))
        flash("Error updating privacy settings", "error")
    return redirect(url_for('index'))

@app.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    if request.method == 'POST':
        num_photos = request.form.get('num_photos')
        try:
            photos = flickr.people.getPhotos(user_id=current_user.id, per_page=num_photos)
            return render_template('photos.html', photos=photos['photos']['photo'])
        except Exception as e:
            logging.error(str(e))
            flash("Error fetching photos", "error")
    return render_template('photos.html')

@app.route('/set_privacy_date_range', methods=['POST'])
@login_required
def set_privacy_date_range():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    is_public = request.form.get('is_public')
    try:
        photos = flickr.photos.search(user_id=current_user.id, min_upload_date=start_date, max_upload_date=end_date)
        for photo in photos['photos']['photo']:
            flickr.photos.setPerms(photo_id=photo['id'], is_public=is_public, is_friend=0, is_family=0, perm_comment=0, perm_addmeta=0)
        flash("Privacy settings updated successfully", "success")
    except Exception as e:
        logging.error(str(e))
        flash("Error updating privacy settings", "error")
    return redirect(url_for('index'))

@app.route('/albums', methods=['GET', 'POST'])
@login_required
def albums():
    if request.method == 'POST':
        album_id = request.form.get('album_id')
        try:
            photos = flickr.photosets.getPhotos(user_id=current_user.id, photoset_id=album_id)
            return render_template('photos.html', photos=photos['photoset']['photo'])
        except Exception as e:
            logging.error(str(e))
            flash("Error fetching album photos", "error")
    else:
        try:
            albums = flickr.photosets.getList(user_id=current_user.id)
            return render_template('albums.html', albums=albums['photosets']['photoset'])
        except Exception as e:
            logging.error(str(e))
            flash("Error fetching albums", "error")
    return render_template('albums.html')

@app.route('/date', methods=['GET', 'POST'])
@login_required
def date():
    if request.method == 'POST':
        min_date = request.form.get('min_date')
        max_date = request.form.get('max_date')
        try:
            photos = flickr.people.getPhotos(user_id=current_user.id, min_upload_date=min_date, max_upload_date=max_date)
            return render_template('photos.html', photos=photos['photos']['photo'])
        except Exception as e:
            logging.error(str(e))
            flash("Error fetching photos by date", "error")
    return render_template('date.html')

@app.route('/error')
def error():
    with open('error.log', 'r') as file:
        contents = file.read()
    return render_template('error_log.html', contents=contents)

if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    app.run(debug=True)