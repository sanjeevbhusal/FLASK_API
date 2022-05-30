from turtle import pd
from flask import request, url_for
from api import bcrypt, mail
from flask import current_app
import jwt
from api.models import User
from functools import wraps
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message

def token_required(f):
    def wrapper(*args, **kwargs):
        token = None
        if "access_token" in request.headers:
            token = request.headers["access_token"]
        else:
            return {"message" : "No Token Received"}, 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
            user = User.query.get(data["id"])

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
            print(data["id"])
            user = User.query.get(data["id"])

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
    
def verify_reset_token(token, expires= 1800):
    s = Serializer(current_app.config["SECRET_KEY"])
    try :
        user_id = s.loads(token, expires)["user_id"]
        return User.query.get(user_id)
    except:
        return None
    
    
def send_email(user, token):
    msg = Message("Password Reset Form", sender="bhusalsanjeev@gmail.com", recipients= [user.email])
    msg.body = f"""Click this link to reset the password.
    {url_for("users.check_token", token=token, _external=True )}
    """
    try:
        mail.send(msg)
    except Exception:
        return None
    
    return "Message Sent"
    
    
    
        