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
    "davisdeatonphotography": User("davisdeatonphotography", "davisdeatonphotography", generate_password_hash("1234")),
}


flickr = flickrapi.FlickrAPI(os.environ['FLICKR_API_KEY'], os.environ['FLICKR_API_SECRET'], cache=True)

@app.route('/')
def index():
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Login, logout routes 

@app.route('/photos', methods=['GET'])
@login_required
def photos():
    try:
        photos = flickr.people.getPhotos(user_id=current_user.id, per_page=10)
        return render_template('photos.html', photos=photos['photos']['photo'])
    except flickrapi.exceptions.FlickrError as e:
        logging.error(str(e))
        flash("Error fetching photos", "error")
    return render_template('photos.html')

@app.route('/albums', methods=['GET'])
@login_required
def albums():
    try:
        albums = flickr.photosets.getList(user_id=current_user.id)
        return render_template('albums.html', albums=albums['photosets']['photoset'])
    except flickrapi.exceptions.FlickrError as e:
        logging.error(str(e))
        flash("Error fetching albums", "error")
    return render_template('albums.html')

# Other routes 

if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    app.run(debug=True)