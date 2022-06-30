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
from api.models import User, Post, Comment

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
            if user is None:
                return {"status" : "failure", "code" : 404, "message": "User trying to perform operation doesnot exist."}, 404
        except:
            return {"message" : 'Token is invalid.'}, 401
        
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
        except:
            return {"message" : 'Token is invalid'}, 401
        
        user = User.query.get(data["user_id"])
        if not user :
            return {"message" : "User with token doesnot exist."} 
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

We receive a lot of Article requests and we try our best to select those which provide a great value to our readers. Below is the reason, we decided not to accept your article. We also have delted the article

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
     
    random_name = secrets.token_hex(8)
    
    _, f_exe = os.path.splitext(file.filename)
    filename = random_name + f_exe
    
    image_path = os.path.join(current_app.root_path, "static/blog_pictures")
    
    with open(image_path + "/" + filename, "wb") as f:
        f.write(file.read())
    
    return filename


def allowed_image(image):
    
    #check if image has the valid extension.
    
    allowed_extensions = ["PNG", "JPEG", "JPG"]
    
    image_extension = image.filename.split(".")[1]
    
    if image_extension.upper() not in allowed_extensions  :
        return False
    
    return True
    
from api.schema import UserRegister, UserLogin, UserUpdate, ResetPassword
from marshmallow import ValidationError

def validate_register_route(data) :
    try:
        data = UserRegister().load(data)  
    except ValidationError as err:
        return {"status" : "failure", "code" : 400, "message" : err.messages}
    
    email = data["email"]    
    user = User.query.filter_by(email = email).first()   
    if user :
        return {"status": "failure", "code" : 409, "message" : "The Email isn't available. Please choose a different one."}
         
    return {"status" : "success", "code" : 201, "validated_user_input" : data}

def validate_login_route(data) :
    try:
        data = UserLogin().load(data)
    except ValidationError as err:
        return {"status": "failure", "code" : 400, "message" : err.messages}
    
    email = data["email"]
    user =  User.query.filter_by(email = email).first()
    
    if not user :
        return {"status": "failure", "code" : 404, "message" : "Couldn't find your Moru Account"}
        
    if not bcrypt.check_password_hash(user.password, data["password"]) :
         return {"status": "failure", "code" : 401, "message" : "Please Enter Correct Password"}
     
    # if user.is_verified == False :
    #     return {"status" : "failure", "code" : 403, "message" : "The account is unverified. Please check your email for verificaion"}
    
    return {"status" : "success", "user" : user, "validated_user_input" : data }

def validate_user_update_route(user, user_id, data) :
    try:
        data = UserUpdate().load(data)
    except ValidationError as err:
        return {"status": "failure" , "code" : 400, "message" : err.messages}
    
    if user.is_admin == False and user.id != user_id :
        return {"status": "failure", "code" : 403, "message" : "You are not authorized"}
    
    if user.is_admin == True:
        user = User.query.get(user_id)
        
    if not user :
        return {"status" : "failure", "code" : 404, "message" : "User doesnot exist"}

    return {"status" : "success", "validated_user_input" : data, "user_object" : user}

def validate_user_delete_route(user, user_id) :
    if user.is_admin == False and user.id != user_id :
        return {"status": "failure", "code" : 403, "message" : "You are not authorized"}
    
    user_to_be_deleted = User.query.get(user_id)
    if not user_to_be_deleted :
        return {"status": "failure", "code" : 404, "message" : "User doesnot exist"}
    
    redirect_required = True
    if user.is_admin == True and user.id != user_to_be_deleted.id :
        redirect_required = False
        
    return {"status": "success", "user_object" : user_to_be_deleted, "redirect_required" : redirect_required}

def verify_reset_token(token):
    try:
        token_info = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms="HS256")
    except Exception :
        return {"status": "failure", "code" : 400, "message" : "Token couldn't be validated. It might have expired or it might be invalid"}
    
    user_id = token_info["user_id"]
    user = User.query.get(user_id)
    
    if not user :
        return {"status": "failure", "code" : 404, "message" : "The user doesnot exist"}
    
    return {"status" : "success", "user_id" : user_id}

def validate_reset_password_route(data, token) :
    try:
        data = ResetPassword().load({**data})
    except ValidationError as err:
        return {"status": "failure", "code" : 400, "message" : err.messages}
    
    token_data = verify_reset_token(token)
    user_id = token_data.get("user_id")
    
    if token_data["status"] == "failure" :
        return token_data
    elif data["user_id"] != user_id :
        return {"status" : "failure", "code" : 400, "message" : "User in the token token and user sent in the request was not same"}
        
    return {"status" : "success" , "validated_user_input" : data, "user_id" : user_id}
 
from api.schema import PostRegister, CategoryMismatchException, PostUpdate, PostReview , CommentRegister, CommentUpdate
def validate_create_new_post_route(data) :
    try:
        data = PostRegister().load(data)
    except ValidationError as err :
        return {"status" : "failure", "code" : 400, "message" : err.messages, }
    except CategoryMismatchException as err :
        return {"status" : "failure", "code" : 400, "message" : "Please choose a Valid Category"}
        
    return {"status" : "success" , "verified_user_input" : data}

def validate_update_single_post_route(data, post_id, user):
    try:
        data= request.get_json()
        data = PostUpdate().load(data)
    except ValidationError as err :
        return {"status" : "failure", "code" : 400, "message" : err.messages}
    
    post = Post.query.get(post_id) 
    if not post :
       return {"status" : "failure", "code" : 404, "message" : "The Post doesnot exist."} 
   
    if user.is_admin == False and user.id != post.author.id :
        return {"status" : "failure" , "code" : 403, "message" : "You are not authorized."}
    
    return {"status" : "success", "verified_user_input" : data, "post_object" : post}
    
def validate_delete_single_post_route(user, post_id) :
    post = Post.query.get(post_id)
    if not post :
        return {"status" : "failure", "code" : 404, "message" : "The post doesnot exist"}
    if user.is_admin == False and user.id != post.author.id :
        return {"status" : "failure" , "code" : 403, "message" : "You are not authorized."}  
    return {"status" : "success", "post_object" : post}

def validate_update_post_status_route(data, post_id) :
    try:
        data = PostReview().load(data)
    except ValidationError as err :
        return {"status": "failure", "code" : 401, "message" : err.messages}
    except Exception :
        return {"status": "failure", "code" : 401, "message" : "Rejected Reason is also required if The Post has been Rejeted"}

    post = Post.query.get(post_id)
    if not post :
        return {"status" : "failure", "code" : 404, "message": "The Post doesnot Exist."}
    if post.is_reviewed == True :
        return {"status" : "failure", "code" : 400, "message": "The Post is already verified."}
    
    return {"status" : "success", "verified_user_input" : data, "post_object" : post}


def validate_add_comment_route(data, post_id) :
    try:
        data = CommentRegister().load(data)
    except ValidationError as err :
        return {"status": "failure", "code" : 400, "message" : err.messages}
    
    post = Post.query.get(post_id)
    if not post :
        return {"status": "failure", "code" : 404, "message" : "The Post doesnot exist"}
    
    return {"status" : "success", "validated_user_input": data}

def validate_update_comment_route(data, comment_id, user) :
    try:
        data = CommentUpdate().load(data)
    except ValidationError as err :
        return {"status": "failure", "code" : 400, "message" : err.messages}
    
    comment = Comment.query.get(comment_id)
    if not comment :
        return {"status" : "failure", "code" : 404, "message" : "Comment doesnot exist"}
    
    if user.is_admin == False and user.id != comment.author.id :
        return {"status" : "failure", "code" : 403,  "message" : "You are not authorized"}
     
    return {"status" : "success", "validated_user_input" : data, "comment" : comment}

def validate_delete_comment_route(comment_id, user) :
    comment = Comment.query.get(comment_id)
    if not comment :
        return {"status" : "failure", "code" : 404, "message" : "Comment doesnot exist"}
    
    if user.is_admin == False and user.id != comment.user_id :
         return {"status" : "failure", "code" : 403,  "message" : "You are not authorized"}
     
    return {"status" : "success", "comment" : comment}
        