from api import db
from sqlalchemy.sql import func
from flask import current_app

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False )  

    created_at = db.Column(db.DateTime, nullable=False, server_default = func.now())
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) 
    is_active=  db.Column(db.Boolean, nullable=True, default=True)
    
    posts = db.relationship("Post", backref="author")
    comments = db.relationship("Comment", backref="author")

class Post(db.Model):
    __tablename__ = "posts"
  
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String, nullable=False)
    
    is_reviewed = db.Column(db.Boolean, nullable=False, default=False)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)
    rejected_reason = db.Column(db.Text, nullable=False, default="Not Rejected")
    created_at = db.Column(db.DateTime, nullable=False, server_default = func.now())
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, )
    comments = db.relationship("Comment", backref="post")
    votes = db.relationship("Vote")
    
class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default= func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),)
    post_id = db.Column(db.ForeignKey("posts.id", ondelete="CASCADE"),)
    
class Vote(db.Model):
    __tablename__ = "votes"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
