from flask import request, current_app
from functools import wraps
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message
from datetime import datetime, timedelta
import jwt

from api import bcrypt, mail
from api.schema import user_response
from api.models import User, Post

def get_user_by_email(email):
    return User.query.filter_by(email = email).first()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def serialize_user(user):
    return user_response.dump(user)

def get_serialized_user_by_id(user_id):
    user = get_user_by_id(user_id)
    return serialize_user(user)

def get_post_by_id(post_id):
    return Post.query.get(post_id)

def is_user_author(user_id, post_user_id):
    return user_id == post_user_id

def is_user_admin(user):
    return user.is_admin
    
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
    return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes= 30 )}, current_app.config["SECRET_KEY"])
   
def get_verification_token(user_id):
    return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=30 )}, current_app.config["SECRET_KEY"])
     
def verify_reset_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
    except Exception :
        return None
    
def send_reset_password_email(email, token):
    msg = Message("Password Reset Form", sender="sanjeev2111071@iimscollege.edu.np", recipients= [email])
    msg.body = f"""Click this link to reset the password.
    {token}
    """
    mail.send(msg)
 
def send_post_accepted_email(email_id):
    msg = Message("Password Reset Form", sender="sanjeev2111071@iimscollege.edu.np", recipients= [email_id])
    msg.body = f"""Congratulations! Your Post has been accepted succesfully
    """
    mail.send(msg)

def send_post_rejected_email(email_id, rejected_reason):
    msg = Message("Password Reset Form", sender="sanjeev2111071@iimscollege.edu.np", recipients= [email_id])
    msg.body = f"""We are Sorry to inform you that your post has been rejected.! 
Below is the rejected reason :
{rejected_reason}
    """
    mail.send(msg)

def send_verify_email(email_id, link):
    msg = Message("Thank You for creating your account. In order to get the most out of your account, please confirm your gmail account.", sender="sanjeev2111071@iimscollege.edu.np", recipients= [email_id])
    msg.body = f"""Click this link to verify your email id.
    {link}
    """
    mail.send(msg)

    # return "Message Sent"
    # # msg = Message('Hello from the other side!', sender =   'peter@mailtrap.io', recipients = ['paul@mailtrap.io'])
    # # msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
    # # mail.send(msg)
    # # return "Message sent!"
    
    
    

    
    
    
        