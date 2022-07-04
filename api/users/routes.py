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
        unvalidated_user_input = request.get_json()
        data = validate_register_route(unvalidated_user_input)
        
        status = data["status"]
        validated_user_input = data.get("validated_user_input")
        
        if status == "failure" :
            return data, data["code"]
   
        validated_user_input["password"] = generate_hash_password(validated_user_input["password"])
        
        new_user = User(**validated_user_input)
        db.session.add(new_user)
        db.session.commit()
        
        token = get_verification_token(new_user.id)
        send_verify_email(new_user.email, token)
        
        return {"status" : "success", "message" : f"Please Verify your account. The link is sent to {validated_user_input['email']}.", "code" : 201, "is_admin" : new_user.is_admin } , 201
    
class Login(Resource) :
    def post(self) :
        unvalidated_user_input = request.get_json()
        data = validate_login_route(unvalidated_user_input)
        
        status = data["status"]
        user = data.get("user")
        
        if status == "failure" :
            return data, data["code"]
        
        token = jwt.encode({"user_id": user.id, "exp": datetime.utcnow() + timedelta(days= 365 )}, current_app.config["SECRET_KEY"])
        user = UserResponse(exclude=["posts", "comments", "created_at"]).dump(user)
    
        return {"user" : user, "token" : token, "message" : f"Welcome Back {user['email']}", "code" : 200 }, 200    

class UsersList(Resource) :
    def get(self) :
        max = request.args.get("max")
        user = User.query.limit(max)
        user = UserResponse(exclude=[]).dump(user, many=True)
        return {"code" : 200, "status" : "success" , "users" : user,}, 200
    
class UserById(Resource) :
    def get(self, user_id) :
        user = User.query.get(user_id)
        if not user :
            return {"status" : "failure", "message" : "User doesnot exist.", "code" : 404,}, 404
        user = UserResponse().dump(user)
    
        return {"status": "success", "user" : user, "code" : 200}, 200
    
    @token_required
    def delete(user, self, user_id) :
        data = validate_user_delete_route(user, user_id)
        
        status = data["status"]
        user = data.get("user_object")
        redirect_required = data.get("redirect_required")
        
        if status == "failure" :
            return data, data["code"]
    
        db.session.delete(user)
        db.session.commit()
        
        return  {"status" : "success", "code" : 200, "message" : "User has been deleted Succesfully", "redirect_required" : redirect_required}, 200
    
    @token_required
    def put(user, self, user_id) :
        unvalidated_user_input = request.get_json()
        data = validate_user_update_route(user, user_id, unvalidated_user_input)
        
        status = data["status"]
        user = data.get("user_object")
        validated_user_input = data.get("validated_user_input")
        
        if status == "failure":
            return data, data["code"]
        
        updated_username = validated_user_input["username"]
        user.username = updated_username
        db.session.commit()
      
        return {"status" : "success", "code" : 200, "message" : f"Username has been Updated to {updated_username}", "credintials" : user}, 200
            
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
        
        status = data["status"]
        user_id = data.get("user_id")
        
        if status == "failure":
            return data, data["code"]
        
        return {"status" : "success", "code" : 200, "user_id" : user_id}, 200
    
class ResetPassword(Resource) :
    def put(self, token):
        unvalidated_user_input = request.get_json()
        data = validate_reset_password_route(unvalidated_user_input, token)
        
        status = data["status"]
        validated_user_input = data.get("validated_user_input")
        user_id = data.get("user_id")
        
        if status == "failure":
            return data, data["code"]

        user = User.query.get(user_id)
        user.password = generate_hash_password(validated_user_input["password"])
        db.session.commit()

        return {"status" : "success", "code" : 200, "message" : "Password Succesfully Changed"}, 200
            
    
