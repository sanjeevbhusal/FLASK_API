from ssl import VERIFY_X509_STRICT
from turtle import pd
from flask import Blueprint, request, abort,jsonify
from api import db, bcrypt
from api.schema import user_input, user_response, PostResponse, post_response
from api.models import User, Post
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta
from flask import current_app
from api.utils import generate_hash_password
from ..utils import token_required, get_reset_token, verify_reset_token, send_email

users = Blueprint("users", __name__,)
       
@users.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    
    try:
        data = user_input.load(data)  
        hashed_pw = generate_hash_password(data["password"])
        data["password"] = hashed_pw
        user = User(**data)
        db.session.add(user)
        db.session.commit()
    except ValidationError as err:
        return {"message" : err.messages}, 400
    except IntegrityError as err :
        return {"message" : "The Email is already Registered"}, 409
    
    
    # token = jwt.encode({"id": user.id, "exp": datetime.utcnow() + timedelta(minutes= 30 )}, current_app.config["SECRET_KEY"])
    # email_sent = send_email(user, token)
    # if not email_sent:
    #     return {"message" : "Due to some reason your email couldnot be valiated right now. Please Validate your email after some time."}, 401
    # return {"message": "The validation link is sent to your email. Please go and confirm it."}, 201
    return {"message": "User has been Created"}, 201
        
    
    
@users.route("/login", methods = ["POST"])
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return jsonify({"message" : "Please Enter both email and Password "}), 400
    
    user = User.query.filter_by(email=auth.username).first()
    
    if not user :
        return {"message": "Couldn't find your Moru Account"}, 404
        
    if not bcrypt.check_password_hash(user.password, auth.password) :
        return {"message": "Please Enter Correct Password"}, 401
    
    token = jwt.encode({"id": user.id, "exp": datetime.utcnow() + timedelta(minutes= 30 )}, current_app.config["SECRET_KEY"])
    
    return {"token" : token}


@users.route("/account/<int:user_id>", methods=["GET"])
def user_account(user_id):
    user = User.query.get(user_id)
    if not user :
        return {"message": "User doesnot exist in the database"}, 401
    
    user = user_response.dump(user)
    posts = Post.query.filter_by(user_id = user["id"]).all()
    user["posts"]= PostResponse(exclude=["user"]).dump(posts, many=True)

    return {"user": user}, 200

@users.route("/update_user", methods=["PUT"])
@token_required
def update_user(user):
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password") or not data.get("username"):
        return {"message" : "Fields are missing"}, 401

    user.email = data["email"]
    user.username = data["username"]
    user.password=  generate_hash_password(data["password"])
    
    db.session.commit()
    return {"message" : "The user has been updated"}


@users.route("/delete_user", methods=["DELETE"])
@token_required
def delete_user(user):
    db.session.delete(user)
    db.session.commit()
    return {"message" : "The user has been deleted"}
    

@users.route("/generate_token")
def generate_token():    
    email = request.args.get("email")
    if email is None :
        return {"message": "Username field is Missing."}, 400
    
    user = User.query.filter_by(email= email).first()
    if user is None :
        return {"message" : "User doesnot exist."}, 401
    
    token = get_reset_token(user.id)
    send_email(user, token)
    
@users.route("/reset_password", methods=["POST"])
def reset_passsword():
    data = request.get_json()
    if data or data.get("password") or data.get("confirm_password") or data.get("user_id"):
        return {"message" : "Fields are missing"}, 401
    
    user = User.query.get(id)
    user.password = data["password"]
    db.session.commit()
    
    return {"message" : "The password has been updated."}
    
    
@users.route("/check_token/<string:token>", methods=["POST"])
def check_token(token):
    user = verify_reset_token(token)
    if user is None :
        return {"message" : "The Token is Invalid or Expired"}, 401
    user = user_response.dump(user)
    
    return {"user": user}, 200
    
    
    
    
    

    