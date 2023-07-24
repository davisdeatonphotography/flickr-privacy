import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import flickrapi
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = '1234'
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

users = {
    "davis": User("davis", "davis", generate_password_hash("test")),
    "davisdeaton": User("davisdeaton", "davisdeaton", generate_password_hash("1234")),
}
flickr = flickrapi.FlickrAPI(os.environ['FLICKR_API_KEY'], os.environ['FLICKR_API_SECRET'], cache=True)

@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    user = users.get(user_id)
    if user:
        return user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
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
            flickr.photos.setPerms(photo_id=photo['id'], is_public=is_public, 
                                   is_friend=0, is_family=0, perm_comment=0, perm_addmeta=0)
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
            flickr.photos.setPerms(photo_id=photo['id'], is_public=is_public, 
                                   is_friend=0, is_family=0, perm_comment=0, perm_addmeta=0)
        flash("Privacy settings updated successfully", "success")
    except Exception as e:
        logging.error(e, exc_info=True)
        flash("Error updating privacy settings: {}".format(e), "error")
    return redirect(url_for('index'))

@app.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    try:
        if request.method == 'POST':
            num_photos = request.form.get('num_photos')
        else:
            num_photos = 10  # Default number of photos for GET request
        photos = flickr.people.getPhotos(user_id=current_user.id, per_page=num_photos)
        return render_template('photos.html', photos=photos['photos']['photo'])
    except Exception as e:
        logging.error(e, exc_info=True)
        flash("Error fetching photos: {}".format(e), "error")
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
            flickr.photos.setPerms(photo_id=photo['id'], is_public=is_public, 
                                   is_friend=0, is_family=0, perm_comment=0, perm_addmeta=0)
        flash("Privacy settings updated successfully", "success")
    except Exception as e:
        logging.error(e, exc_info=True)
        flash("Error updating privacy settings: {}".format(e), "error")
    return redirect(url_for('index'))

@app.route('/albums', methods=['GET', 'POST'])
@login_required
def albums():
    try:
        if request.method == 'POST':
            album_id = request.form.get('album_id')
            photos = flickr.photosets.getPhotos(user_id=current_user.id, photoset_id=album_id)
            return render_template('photos.html', photos=photos['photoset']['photo'])
        else:
            albums = flickr.photosets.getList(user_id=current_user.id)
            return render_template('albums.html', albums=albums['photosets']['photoset'])
    except Exception as e:
        logging.error(e, exc_info=True)
        flash("Error: {}".format(e), "error")
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
            logging.error(e, exc_info=True)
            flash("Error fetching photos by date: {}".format(e), "error")
    return render_template('date.html')

@app.route('/error')
def error():
    with open('error.log', 'r') as file:
        contents = file.read()
    return render_template('error_log.html', contents=contents)

if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    app.run(debug=True)
