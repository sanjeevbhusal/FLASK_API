from api import db
from sqlalchemy.sql import func



class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False )  
    
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False) 
    # is_active=  db.Column(db.Boolean, nullable=True, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default = func.now())

class Post(db.Model):
    __tablename__ = "posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    is_reviewed = db.Column(db.Boolean, nullable=False, default=False)
    is_accepted = db.Column(db.Boolean, nullable=False, default=False)
    rejected_reason = db.Column(db.Text, nullable=False, default="Not Rejected")
    category = db.Column(db.String, nullable=False, default="General")
    created_at = db.Column(db.DateTime, nullable=False, server_default = func.now())
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, )
    user = db.relationship("User")
    
class Vote(db.Model):
    __tablename__ = "votes"
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)

    
    