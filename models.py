from app import db
from flask_login import UserMixin
from datetime import datetime


user_user = db.Table('user_user',
    db.Column('user_id1', db.Integer, db.ForeignKey('user.id')),
    db.Column('user_id2', db.Integer, db.ForeignKey('user.id'))
)




#model for user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_img = db.Column(db.String, nullable = True)
    posts = db.relationship('Post', backref = 'user', passive_deletes = True )
    following = db.relationship('User', secondary = user_user, backref='followers',passive_deletes = True,
    primaryjoin = user_user.c.user_id2==id,secondaryjoin=user_user.c.user_id1==id)
    comments = db.relationship('Comment', backref = 'user', passive_deletes = True)
    likes = db.relationship('Like', backref = 'user', passive_deletes = True)



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    title = db.Column(db.String(140), nullable=False)
    caption = db.Column(db.String(140), nullable=False)
    img = db.Column(db.String, nullable = True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = "CASCADE"), nullable = False)
    comments = db.relationship('Comment', backref = 'post', passive_deletes = True)
    likes = db.relationship('Like', backref = 'post', passive_deletes = True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    comment = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = 'CASCADE'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id',ondelete = 'CASCADE'), nullable = False)



class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.Integer, db.ForeignKey('user.id',ondelete = 'CASCADE'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id',ondelete = 'CASCADE'), nullable = False)



