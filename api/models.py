from api import db
from datetime import datetime
from sqlalchemy.sql import func


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False )   
    created_at = db.Column(db.DateTime, nullable=False, server_default = func.now())
    # posts = db.relationship("Post", backref="user")
    
class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default = func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, )
    user = db.relationship("User")
    
class Vote(db.Model):
    __tablename__ = "votes"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    