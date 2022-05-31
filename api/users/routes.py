from flask import Blueprint, request, current_app
from marshmallow import ValidationError
from datetime import datetime, timedelta
import jwt

from api import db, bcrypt
from api.models import User, Post
from api.schema import user_input, user_response, PostResponse, user_login_input, user_update_input, reset_user_password
from api.utils import generate_hash_password, token_required, get_reset_token, verify_reset_token, send_email , get_user_by_email, get_user_by_id, serialize_user, get_serialized_user_by_id

users = Blueprint("users", __name__,)
       
@users.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    
    try:
        data = user_input.load(data)  
        user = get_user_by_email(data["email"]) 
        
        if user :
            return {"message": "The User with this Email already exist."}, 409
            
        data["password"] = generate_hash_password(data["password"])
        user = User(**data)
        
        db.session.add(user)
        db.session.commit()
        
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    
    # token = jwt.encode({"id": user.id, "exp": datetime.utcnow() + timedelta(minutes= 30 )}, current_app.config["SECRET_KEY"])
    # email_sent = send_email(user, token)
    # if not email_sent:
    #     return {"message" : "Due to some reason your email couldnot be valiated right now. Please Validate your email after some time."}, 401
    # return {"message": "The validation link is sent to your email. Please go and confirm it."}, 201
    return {"message": "User has been Created"}, 201
        
    
@users.route("/login", methods = ["POST"])
def login():
    auth = request.authorization
 
    try:
        data = user_login_input.load(auth)
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    user = get_user_by_email(data["username"])
    
    if not user :
        return {"message": "Couldn't find your Moru Account"}, 404
        
    if not bcrypt.check_password_hash(user.password, data["password"]) :
        return {"message": "Please Enter Correct Password"}, 401
    
    token = jwt.encode({"user_id": user.id, "exp": datetime.utcnow() + timedelta(days= 365 )}, current_app.config["SECRET_KEY"])
    
    return {"token" : token}


@users.route("/account/<int:user_id>", methods=["GET"])
def user_account(user_id):
    user = User.query.get(user_id)
    if not user :
        return {"message": "User doesnot exist in the database"}, 404
    
    user = user_response.dump(user)
    posts = Post.query.filter_by(user_id = user["id"]).all()
    user["posts"]= PostResponse(exclude=["user"]).dump(posts, many=True)
   
    return {"user": user}, 200

@users.route("/update_user", methods=["PUT"])
@token_required
def update_user(user):
    data = request.get_json()
    try:
        data = user_update_input.load(data)
        user_exist = get_user_by_email(data["email"])
        
        if user_exist :
            return {"message": "The Email already exist."}, 400
        
    except ValidationError as err:
        return {"message" : err.messages}, 400

    user.email = data["email"]
    user.username = data["username"]
    user.password=  generate_hash_password(data["password"])
    
    user = serialize_user(user)
    db.session.commit()
    
    return {"user" : user}, 200


@users.route("/delete_user", methods=["DELETE"])
@token_required
def delete_user(user):
    db.session.delete(user)
    db.session.commit()
    return {"message" : "The user has been deleted"}, 200
    

@users.route("/generate_token")
def generate_token():    
    email = request.args.get("email")
    if email is None :
        return {"message": "Username field is Missing."}, 400
    
    user = get_user_by_email(email)
    
    if not user :
        return {"message" : "User doesnot exist."}, 400
    
    token = get_reset_token(user.id)
    send_email(user, token)
    return {"message" : "Token Sent"}
    
@users.route("/verify_token/<token>", methods=["GET"])
def verify_token(token):
    token_data = verify_reset_token(token)
    if not token_data :
        return {"message" : "The Token is Invalid or Expired"}, 401
    
    user = get_serialized_user_by_id(token_data["user_id"])
    return {"user": user}, 200
    
@users.route("/reset_password/", methods=["POST"])
def reset_passsword():
    data = request.get_json()
    try:    
        user_credentials = reset_user_password.load(data)
    except ValidationError as err:
        return {"message" : err.messages}, 401
    
    user = get_user_by_id(user_credentials["user_id"])
    user.password = generate_hash_password( user_credentials["password"])
    db.session.commit()
    
    return {"message" : "The password has been updated."}, 200
    
    
    
    
    
    

    