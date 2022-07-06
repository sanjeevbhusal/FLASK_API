from flask import request
from flask_restful import Resource
from werkzeug.exceptions import BadRequest
from smtplib import SMTPException
from marshmallow import ValidationError
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from api.models import User
from api.schema import UserResponse
from api.utils import  validate_routes, authenticate, email_gateway, token, user_database, DuplicateEmailException, UserNotFoundException, IncorrectPasswordException, UnautorizedAccessException

class Register( Resource):
    def post(self):
        try:
            request_data = request.get_json()
            result = validate_routes.register(request_data)
            user = User(**result)
            user_database.save(user)
            email_gateway.send_welcome_message(result["email"])
            return {"status" : "success", "message" : "User registered successfully"}, 201
        except BadRequest as err :
            return {"status" : "failure", "message" : err.description}, 400
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except DuplicateEmailException as err :
            return {"status" : "failure", "error" : err.args[0]}, 409
        except SMTPException as err :
            return {"status" : "failure", "error" : "Invalid Email address"}, 400
class Login(Resource) :
    def post(self):
        try: 
            request_data = request.get_json()
            user = validate_routes.login(request_data)
            jwt = token.create_login_token(user["id"])
            return { "status" : "success", "user" : user, "token" : jwt }, 200 
        except BadRequest as err :
            return {"status" : "failure", "message" : err.description}, 400
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except UserNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404
        except IncorrectPasswordException as err :
            return {"status" : "failure", "error" : err.args[0]}, 401
    
class UsersList(Resource) :
    def get(self):
        schema = UserResponse(exclude=[])
        limit = request.args.get("max")
        user = User.query.limit(limit)
        user = schema.dump(user, many=True)
        return {"status" : "success" , "users" : user,}, 200
    
class UserById(Resource) :
    def get(self, user_id) :
        schema = UserResponse()
        user = user_database.get_by_id(user_id)
        if not user :
            return {"status" : "failure", "message" : "User doesnot exist."}, 404
        user = schema.dump(user)
        return {"status": "success", "user" : user}, 200
    
    @authenticate.token_required
    def delete(user, self, user_id) :
        try:
            user, should_redirect = validate_routes.delete_user(user, user_id).values()
            user_database.delete_user(user)
        except UnautorizedAccessException as err :
            return {"status" : "failure", "error" : err.args[0]}, 403
        except UserNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404
        return  {"status" : "success", "should_redirect" : should_redirect},200
    
    @authenticate.token_required
    def put(user, self, user_id) :
        try:
            request_data = request.get_json()
            user, result = validate_routes.update_user(user, user_id, request_data).values()
            user.username = result["username"]
            user_database.update_user()
            return {"status" : "success","message" : "Username Updated" ,"credintials" : {"username" : user.username}}, 200
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except UnautorizedAccessException as err :
            return {"status" : "failure", "error" : err.args[0]}, 403
        except UserNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404
        
class GenerateToken(Resource) :
    def get(self, email) :
        try:
            user = user_database.get_by_email(email)
            if not user :
                return {"status": "failure", "message" : "Couldn't find the User"}, 404
            jwt = token.get_password_reset_token(user.id)
            email_gateway. send_reset_password_email(user.email, jwt)
            return {"status" : "success", "message" : "Password reset link sent to your email"}, 200
        except SMTPException as err :
            return {"status" : "failure", "error" : "Invalid Email address"}, 400

class VerifyToken(Resource) :
    def get(self, user_token):
        try:
            user_id = token.verify_reset_token(user_token)
            return {"status" : "success", "user_id" : user_id}, 200
        except ExpiredSignatureError as err :
            return {"status": "failure", "error": "Token has been expired."}, 400
        except InvalidTokenError as err :
            return {"status": "failure", "error": "Token is invalid"}, 400
        except UserNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404 
   
class ResetPassword(Resource) :
    def put(self, user_token):
        try:
            request_data = request.get_json()
            result, user_id = validate_routes.reset_password(request_data, user_token).values()
            user = user_database.get_by_id(user_id)
            user_database.update_password(user, result["password"])
            return {"status" : "success", "message" : "Password Succesfully Updated"}, 200
        except BadRequest as err :
            return {"status" : "failure", "message" : err.description}, 400 
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except ExpiredSignatureError as err :
            return {"status": "failure", "error": "Token has been expired."}, 400
        except InvalidTokenError as err :
            return {"status": "failure", "error": "Token is invalid"}, 400
        except UserNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404
        
            
            
    
