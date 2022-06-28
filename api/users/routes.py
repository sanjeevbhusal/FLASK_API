from flask import Blueprint, request, current_app
from datetime import datetime, timedelta
import jwt
from flask_restful import Resource

from api import db
from api.models import User
from api.schema import UserResponse
from api.utils import generate_hash_password,  verify_reset_token, send_reset_password_email, get_verification_token, send_verify_email, validate_register_route, validate_login_route, validate_user_update_route, validate_user_delete_route, validate_reset_password_route, token_required, get_password_reset_token

# users = Blueprint("users", __name__,)

class Register(Resource) :
    def post(self) :
        data = request.get_json()
        data = validate_register_route(data)
        
        if data["status"] == "failure" :
            return data, data["code"]
        
        credential = data["credential"]    
        credential["password"] = generate_hash_password(credential["password"])
        
        new_user = User(**credential)
        db.session.add(new_user)
        db.session.commit()
        
        token = get_verification_token(new_user.id)
        send_verify_email(new_user.email, token)
        user = UserResponse(exclude=["posts", "comments"]).dump(new_user)
        
        return {**data}, data["code"]
    
class Login(Resource) :
    def post(self) :
        data = request.authorization
        data = validate_login_route(data)
        if data["status"] == "failure" :
            return data, data["code"]
        
        user = data["user"]
        token = jwt.encode({"user_id": user.id, "exp": datetime.utcnow() + timedelta(days= 365 )}, current_app.config["SECRET_KEY"])
        user = UserResponse(exclude=["posts", "comments", "created_at"]).dump(user)
    
        return {**data, "user" : user, "token" : token}, data["code"]      

class UsersList(Resource) :
    def get(self) :
        max = request.args.get("max")
        user = User.query.limit(max)
        user = UserResponse(exclude=[]).dump(user, many=True)
        return {"code" : 200, "status" : "success" , "users" : user,}, 200
    
class UserById(Resource) :
    def get(self, id) :
        print(self, id)
        user = User.query.get(id)
        if not user :
            return {"status" : "failure", "message" : "User doesnot exist.", "code" : 404,}, 404
        user = UserResponse().dump(user)
    
        return {"status": "success", "user" : user, "code" : 200}, 200
    
    @token_required
    def delete(user, self, id) :
        data = validate_user_delete_route(user, id)
        if data["status"] == "failure" :
            return data
    
        user = data["user_to_delete"]
        db.session.delete(user)
        db.session.commit()
        data.pop("user_to_delete")
        
        return  data, data["code"]
    
    @token_required
    def put(user, self, id) :
        data = request.get_json()
        data = validate_user_update_route(user, id, data)
        if data["status"] == "failure":
            return data, data["code"]
        
        user = data["user"]
        updated_username = data["credentials"]["username"]
        user.username = updated_username
        db.session.commit()
        
        data.pop("user")
        return data, data["code"]
            
class GenerateToken(Resource) :
    def get(self, email) :
        user = User.query.filter_by(email = email).first()
        if not user :
            return {"status": "failure", "code" : 404, "message" : "User doesnot exist"}, 404
        
        token = get_password_reset_token(user.id)
        send_reset_password_email(user.email, token)
        
        return {"status" : "success", "code" : 200, "message" : f"Reset link has been sent to {user.email}"}, 200
    
class VerifyToken(Resource) :
    def get(self, token) :
        data = verify_reset_token(token)
        if data["status"] == "failure":
            return data, data["code"]
        
        return data, data["code"]
    
class ResetPassword(Resource) :
    def put(token):
        data = request.get_json()
        data = validate_reset_password_route(data, token)
        if data["status"] == "failure":
            return data, data["code"]

        user = User.query.get(data["user_id"])
        credentials = data["credentials"]

        user.password = generate_hash_password(credentials["password"])
        db.session.commit()

        return data, data["code"]
            
    
