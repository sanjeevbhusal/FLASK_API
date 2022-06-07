from flask import Blueprint, request, current_app
from marshmallow import ValidationError
from datetime import datetime, timedelta
import jwt

from api import db, bcrypt
from api.models import User
from api.schema import user_login, UserRegister, UserResponse, UserUpdate, ResetPassword
from api.utils import generate_hash_password, token_required, admin_token_required,get_password_reset_token, verify_reset_token, send_reset_password_email , get_user_by_email, get_user_by_id,  get_serialized_user_by_id, get_verification_token, send_verify_email

users = Blueprint("users", __name__,)
       
@users.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    
    try:
        data = UserRegister().load(data)  
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    user = get_user_by_email(data["email"]) 
        
    if user :
        return {"message": "The User with this Email already exist."}, 409
            
    data["password"] = generate_hash_password(data["password"])
    new_user = User(**data)
    
    db.session.add(new_user)
    db.session.commit()
    
    token = get_verification_token(new_user.id)
    send_verify_email(new_user.email, token)
    
    user = UserResponse(exclude=["posts", "comments"]).dump(new_user)

    return {"message": "User has been Created", "user" : user }, 201
        
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
    
    user = UserResponse(exclude=["posts", "comments", "created_at"]).dump(user)
    
    return {"token" : token, "user" : user}

@users.route("/account", methods=["GET"])
def get_all_users():
    max = request.args.get("max")
    
    user = User.query.limit(max)
    
    user = UserResponse(exclude=[]).dump(user, many=True)
    
    return {"users": user}, 200

@users.route("/account/<int:user_id>", methods=["GET"])
def get_user_account(user_id):
    
    user = User.query.get(user_id)
    
    if not user :
        return {"message": "User doesnot exist."}, 404
    
    user = UserResponse().dump(user)
    
    return {"user": user}, 200

@users.route("/update_user/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user, user_id):
    
    if user.is_admin == False and user.id != user_id :
        return {"message" : "You cannot update other's account."}, 403
    
    data = request.get_json()
    
    try:
        data = UserUpdate().load(data)
    except ValidationError as err:
        return {"message" : err.messages}, 400
    
    user.username = data["username"]

    db.session.commit()
    
    return {"user" : "User has been Updated"}, 200

@users.route("/delete_user/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(user, user_id):
    
    user = get_user_by_id(user_id)
    
    if not user :
        return {"message" : f"User with email {user_id} doesnot exist."}, 404
    
    
    if user.is_admin == False and user.id != user_id :
        return {"message" : "You cannot delete other's account."}, 403
 
    user = User.query.get(user_id)  
    if not user :
        return {"message": f"The user with id {user_id} doesnot exist."}, 404
    
    db.session.delete(user)
    db.session.commit()
    
    return {"message" : "The user has been deleted"}, 200
    
@users.route("/generate_token/<string:email>")
def generate_reset_password_token(email):    
    
    user = get_user_by_email(email)
    
    if not user :
        return {"message" : f"User with email {email} doesnot exist."}, 404
    
    token = get_password_reset_token(user.id)
    send_reset_password_email(user.email, token)
    
    return {"message" : f"Token has been sent to {user.email}"}, 200
    
@users.route("/verify_token/<token>", methods=["GET"])
def verify_token(token):
    
    token_data = verify_reset_token(token)
    if not token_data:
        return {"message": "Token couldn't be validated. It might have expired or it might be invalid"}, 400
    
    user = get_user_by_id(token_data["user_id"])
    
    if not user :
        return {"message" : "The Token is Invalid or Expired"}, 400
    
    user = UserResponse(only=["id"]).dump(user)
    
    return {"message": "The token has been verified", "token": token}, 200
    
@users.route("/reset_password/", methods=["POST"])
def reset_passsword():
    
    data = request.get_json()
    
    try:    
        user_credentials = ResetPassword().load(data)
    except ValidationError as err:
        return {"message" : err.messages}, 401
    
    token_data = verify_reset_token(user_credentials["token"])
    if not token_data:
        return {"message": "Token couldn't be validated. It might have expired or it might be invalid"}, 400
    
    user = get_user_by_id(token_data["user_id"])
    if not user:
        return {"message": "The user doesnot exist"}, 404
    
    user.password = generate_hash_password(user_credentials["password"])
    
    db.session.commit()
    
    return {"message" : "The password has been updated."}, 200
    
    
    
    
    
    

    
