from flask import Blueprint, request, abort,jsonify
from api import db, bcrypt
from api.schema import user_input
from api.models import User
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
import jwt
from datetime import datetime, timedelta
from api import app
from api.utils import generate_hash_password

users = Blueprint("users", __name__)
       
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
        return {"message" : err.messages}
    except IntegrityError as err :
        return {"message" : "The Email is already Registered."}
         
    return {"message" : "You are registered Succesfully."}
    
    
@users.route("/login", methods = ["POST"])
def login():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return jsonify({"message" : "Please Enter both email and Password "})
    
    user = User.query.filter_by(email=auth.username).first()
    
    if not user :
        return {"message": "Couldn't find your Moru Account"}, 404
        
    if not bcrypt.check_password_hash(user.password, auth.password) :
        return {"message": "Please Enter Correct Password"}, 404
    
    token = jwt.encode({"id": user.id, "exp": datetime.utcnow() + timedelta(minutes= 30 )}, app.config["SECRET_KEY"])
    
    return {"token" : token}
    