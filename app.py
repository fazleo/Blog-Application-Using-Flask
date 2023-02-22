from flask import Flask,flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager








bas_dir = os.path.dirname(os.path.abspath(__name__))

#name of database
db_name = "database.sqlite3"
upload_folder = 'static/uploads'

#initialize app
app  = Flask(__name__)

app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = upload_folder


#connecting database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(bas_dir,db_name)
db = SQLAlchemy()
from models import *
db.init_app(app)






#login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



def del_img(img):
    img_path = os.path.join(app.config['UPLOAD_FOLDER'],img)
    if os.path.exists(img_path):
        os.remove(img_path)
    







