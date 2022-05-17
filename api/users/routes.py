from flask import Blueprint, request, abort, make_response
from api import db, bcrypt
from api.schema import user_input, user_response
from api.models import User
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError


users = Blueprint("users", __name__)

@users.route("/register", methods = ["POST"])
def register():
    user_credintials = request.get_json()
    try:
        desirialized_user = user_input.load(user_credintials)
        hashed_pw = bcrypt.generate_password_hash(desirialized_user["password"]).decode("utf-8")
        desirialized_user["password"] = hashed_pw
        new_user = User(**desirialized_user)
        db.session.add(new_user)
        db.session.commit()
    except ValidationError as err:
        abort(404, description = err.messages)
    except IntegrityError as err :
        abort(409, description = "The email already exists.")
         
    serialized_user = user_input.dump(new_user)
    response = make_response(serialized_user, 201)
    
    return response
    
    
@users.route("/login", methods = ["POST"])
def login():
    user_credintials = request.get_json()
    user = User.query.filter_by(email=user_credintials["email"]).first()
    
    if not user :
        abort(404, description = "Couldn't find your Moru Aaccount")
    serialized_user = user_response.dump(user)
    if not bcrypt.check_password_hash(serialized_user["password"], user_credintials["password"]) :
        abort(404, description = "Please Enter Correct Password.")
    
    return serialized_user
    