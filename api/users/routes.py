from flask import Blueprint, request, current_app
from datetime import datetime, timedelta
import jwt

from api import d
from api.models import User
from api.schema import UserResponse
from api.utils import generate_hash_password,  verify_reset_token, send_reset_password_email, get_verification_token, send_verify_email, validate_register, validate_login, validate_user_update, validate_user_delete, verify_reset_password

users = Blueprint("users", __name__,)
       
@users.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    data = validate_register(data)
    if data["has_error"] :
        return data["error"]
            
    data["password"] = generate_hash_password(data["password"])
    data.pop("has_error")
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    
    token = get_verification_token(new_user.id)
    send_verify_email(new_user.email, token)
    user = UserResponse(exclude=["posts", "comments"]).dump(new_user)
    return {"message": "User has been Created", "user" : user }, 201
        
@users.route("/login", methods = ["POST"])
def login():
    data = request.authorization
    data = validate_login(data)
    if data["has_error"]:
        return data["error"]
    user = data["cred"]
    
    token = jwt.encode({"user_id": user.id, "exp": datetime.utcnow() + timedelta(days= 365 )}, current_app.config["SECRET_KEY"])
    user = UserResponse(exclude=["posts", "comments", "created_at"]).dump(user)
    return {"token" : token, "user" : user}

@users.route("/users", methods=["GET"])
def get_all_users():
    max = request.args.get("max")
    user = User.query.limit(max)
    user = UserResponse(exclude=[]).dump(user, many=True)
    return {"users": user}, 200

@users.route("/users/<int:user_id>", methods=["GET"])
def get_user_account(user_id):
    user = User.query.get(user_id)
    if not user :
        return {"message": "User doesnot exist."}, 404
    user = UserResponse().dump(user)
    return {"user": user}, 200

@users.route("/user/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user, user_id):
    data = request.get_json()
    data = validate_user_update(user, user_id, data)
    if data["has_error"]:
        return data["error"]
    
    user.username = data["username"]
    db.session.commit()
    
    return {"user" : "User has been Updated"}, 200

@users.route("/user/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(user, user_id):
    data = validate_user_delete(user, user_id)
    if data["has_error"] :
        return data["error"]
    
    db.session.delete(data["user"])
    db.session.commit()
    return {"message" : "The user has been deleted"}, 200
    
@users.route("/generate_token/<string:email>", methods=["GET"])
def generate_reset_password_token(email):    
    user = User.query.filter_by(email = email).first()
    if not user :
        return {"error": {"code" : 404, "message" : "User doesnot exist"}}
    
    token = get_password_reset_token(user.id)
    send_reset_password_email(user.email, token)
    return {"message" : f"Token has been sent to {user.email}"}, 200
    
@users.route("/verify_token/<token>", methods=["GET"])
def verify_token(token):
    data = verify_reset_token(token)
    if data["has_error"] :
        return data["error"]
    
    return {"message": "The token has been verified", "token": data["token"]}, 200
    
@users.route("/reset_password", methods=["POST"])
def reset_passsword():
    data = request.get_json()
    data = verify_reset_password(data)
    if data["has_error"] :
        return data["error"]
    
    user = data["user"]
    user.password = generate_hash_password(data["password"])
    db.session.commit()
    return {"message" : "The password has been updated."}, 200
    
    
    
    
    
    

    
