from flask import request, current_app
from functools import wraps
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message
from datetime import datetime, timedelta
import jwt
import os
import secrets

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
            return {"message" : 'Token is invalid or the user doesnot exist.'}, 401
        
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

def get_password_reset_token(user_id):
    return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes= 30 )}, current_app.config["SECRET_KEY"])
   
def get_verification_token(user_id):
    return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=30 )}, current_app.config["SECRET_KEY"])
     
def verify_reset_token(token):
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
    except Exception :
        return None
    
def send_reset_password_email(email, token):
    msg = Message("Password Reset Form", sender="noreply@gmail.com", recipients= [email])
    msg.body = f"""

Click on the link below to verify your account

The link expires in 30 minutes.

{token}

If you didn't requested to reset your password, kindly ignore this email.
"""
    mail.send(msg)
 
def send_post_accepted_email(post):
    msg = Message("Regarding the recent article you wrote on blog.moru.com.", sender="noreply@gmail.com", recipients= [post.author.email])
    msg.body = f"""
Congratulations {post.author.username}, 
Recently, you wrote a Article titled {post.title}. Our team has carefully reviewed the Article and we are more than happy to let you know that your Article has been accepted. 
 
Thank You for sharing your knowledge with the world.
Keep Writing!!!

Best Wishes from MORU Digital Wallet.
"""
    mail.send(msg)

def send_post_rejected_email(post):
    msg = Message("Regarding the recent article you wrote on blog.moru.com.", sender="noreply@gmail.com", recipients= [post.author.email])
    msg.body = f"""
Dear {post.author.username}, 
Recently, you wrote a Article titled {post.title}. Our team has carefully reviewed the Article and we feel very sorry to inform you that we have decided not to go forward with your Article. 

We receive a lot of Article requests and we try our best to select those which provide a great value to our readers. Below is the reason, we decided not to accept your article.

{post.rejected_reason}
 
Don't let this rejection stop you from writing articles. 
Keep Writing!!!

Best Wishes from MORU Digital Wallet.
    """
    mail.send(msg)

def send_verify_email(email_id, link):
    msg = Message("Verify your email Account", sender="noreply@gmail.com", recipients= [email_id])
    msg.body = f"""Thank You for creating your account. In order to get the most out of your account, please confirm your account
    
Click on the link below to verify your account

The link expires in 30 minutes.

{link}
    
This is a automated generated email. Please donot reply this email.
    """
    mail.send(msg)

    # return "Message Sent"
    # # msg = Message('Hello from the other side!', sender =   'peter@mailtrap.io', recipients = ['paul@mailtrap.io'])
    # # msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
    # # mail.send(msg)
    # # return "Message sent!"
    
def save_file(file):
    if not file :
        return None
     
    random_name = secrets.token_hex(8)
    
    _, f_exe = os.path.splitext(file.filename)
    filename = random_name + f_exe
    
    image_path = os.path.join(current_app.root_path, "static/blog_pictures")
    
    with open(image_path + "/" + filename, "wb") as f:
        f.write(file.read())
    
    return filename


def allowed_image(image):
    allowed_extensions = ["PNG", "JPEG", "JPG"]
    
    f_exe = image.filename.split(".")[1].upper()
    
    if f_exe in allowed_extensions:
        return True
    return False
    