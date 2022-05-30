from turtle import pd
from flask import request, url_for
from api import bcrypt, mail
from flask import current_app
import jwt
from api.models import User
from functools import wraps
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message
from api.models import User, Post
from api.schema import user_response

def get_user_by_email(email):
    return User.query.filter_by(email = email).first()
    

def token_required(f):
    def wrapper(*args, **kwargs):
        token = None
        if "access_token" in request.headers:
            token = request.headers["access_token"]
        else:
            return {"message" : "No Token Received"}, 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            user = User.query.get(data["user_id"])

        except:
            return {"message" : 'Token is invalid'}, 401
        
        return f(user, *args, **kwargs)
    # Renaming the function name:
    wrapper.__name__ = f.__name__
    return wrapper


def admin_token_required(f):
    def wrapper(*args, **kwargs):
        token = None
        if "access_token" in request.headers:
            token = request.headers["access_token"]
        else:
            return {"message" : "No Token Received"}, 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            user = User.query.get(data["user_id"])

        except:
            return {"message" : 'Token is invalid'}, 401
        
        if user.is_admin == False :
             return {"message" : "You are not authorized"}, 401
        
        return f(user, *args, **kwargs)
    # Renaming the function name:
    wrapper.__name__ = f.__name__
    return wrapper

def generate_hash_password(password):
    return bcrypt.generate_password_hash(password).decode("utf-8")


def get_reset_token(user_id):
    s = Serializer(current_app.config["SECRET_KEY"])
    return s.dumps({"user_id": user_id})
    
def verify_reset_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
    except Exception :
        return None
    
def send_email(user, token):
    msg = Message("Password Reset Form", sender="bhusalsanjeev@gmail.com", recipients= [user.email])
    msg.body = f"""Click this link to reset the password.
    """
    try:
        mail.send(msg)
    except Exception:
        return None
    
    return "Message Sent"
    
def get_user_by_id(user_id):
    return User.query.get(user_id)

def serialize_user(user):
    return user_response.dump(user)

def get_serialized_user_by_id(user_id):
    user = get_user_by_id(user_id)
    return user_response.dump(user)

def get_post_by_id(post_id):
    return Post.query.get(post_id)

def is_user_author(user_id, post_user_id):
    return user_id == post_user_id

def is_user_admin(user):
    return user.is_admin
    
    
    
        