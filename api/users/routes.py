from flask import Blueprint, request, current_app
from marshmallow import ValidationError
from datetime import datetime, timedelta
import jwt

from api import db, bcrypt
from api.models import User
from api.schema import user_register, user_response, user_login, user_update, reset_password
from api.utils import generate_hash_password, token_required, admin_token_required,get_reset_token, verify_reset_token, send_reset_password_email , get_user_by_email, get_user_by_id,  get_serialized_user_by_id, get_verification_token, send_verify_email

users = Blueprint("users", __name__,)
       
@users.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    
    try:
        data = user_register.load(data)  
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    user = get_user_by_email(data["email"]) 
        
    if user :
        return {"message": "The User with this Email already exist."}, 409
            
    data["password"] = generate_hash_password(data["password"])
    user = User(**data)
    
    db.session.add(user)
    db.session.commit()
    
    token = get_verification_token(user.id)
    send_verify_email(user.email, token)

    return {"message": "User has been Created"}, 201
        
@users.route("/login", methods = ["POST"])
def login():
    auth = request.authorization
 
    try:
        data = user_login.load(auth)
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    user = get_user_by_email(data["username"])
    
    if not user :
        return {"message": "Couldn't find your Moru Account"}, 404
        
    if not bcrypt.check_password_hash(user.password, data["password"]) :
        return {"message": "Please Enter Correct Password"}, 401
    
    token = jwt.encode({"user_id": user.id, "exp": datetime.utcnow() + timedelta(days= 365 )}, current_app.config["SECRET_KEY"])
    
    return {"token" : token}

@users.route("/account", methods=["GET"])
def get_all_users():
    max = request.get_args("max")
    
    user = User.query.limit(max)
    
    user = user_response.dump(user, many=True)
    
    return {"users": user}, 200


@users.route("/account/<int:user_id>", methods=["GET"])
def get_user_account(user_id):
    
    user = User.query.get(user_id)
    
    if not user :
        return {"message": "User doesnot exist."}, 404
    
    user = user_response.dump(user)
    
    return {"user": user}, 200

@users.route("/update_user", methods=["PUT"])
@token_required
def update_user(user):
    
    data = request.get_json()
    
    try:
        data = user_update.load(data)
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    user.username = data["username"]

    db.session.commit()
    
    return {"user" : "User has been Updated"}, 200

@users.route("/delete_user/<int:user_id>", methods=["DELETE"])
@admin_token_required
def delete_user(user, user_id):
     
    user = User.query.get(user_id)  
    if not user :
        return {"message": "The User doesnot Exist."}, 404
    
    db.session.delete(user)
    db.session.commit()
    
    return {"message" : "The user has been deleted"}, 200
    
@users.route("/generate_token")
def generate_reset_password_token():    
    
    email = request.args.get("email")
    
    if email is None :
        return {"message": "Email field is Missing."}, 400
    
    user = get_user_by_email(email)
    
    if not user :
        return {"message" : "User doesnot exist."}, 400
    
    token = get_reset_token(user.id)
    send_reset_password_email(user.email, token)
    
    return {"message" : "Token Sent"}, 200
    
@users.route("/verify_token/<token>", methods=["GET"])
def verify_token(token):
    
    user = verify_reset_token(token)
    
    if not user :
        return {"message" : "The Token is Invalid or Expired"}, 401
    
    user = get_serialized_user_by_id(user["user_id"])
    
    return {"user": user}, 200
    
@users.route("/reset_password/", methods=["POST"])
def reset_passsword():
    
    data = request.get_json()
    
    try:    
        user_credentials = reset_password.load(data)
    except ValidationError as err:
        return {"message" : err.messages}, 401
    
    user = get_user_by_id(user_credentials["user_id"])
    if not user:
        return {"message": "The user doesnot exist"}, 404
    
    user.password = generate_hash_password( user_credentials["password"])
    
    db.session.commit()
    
    return {"message" : "The password has been updated."}, 200
    
    
    
    
    
    

    