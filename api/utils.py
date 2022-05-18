from flask import request
from api import app, bcrypt
import jwt
from api.models import User
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(*args, *kwargs)
        token = None
        
        if "access_token" in request.headers:
            token = request.headers["access_token"]
        else:
            return {"message" : "No Token Received"}, 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            user = User.query.get(data["id"])
        except:
            return {"message" : 'Token is invalid'}, 401
        
        return f(user, *args, **kwargs)
    
    return decorated

def generate_hash_password(password):
    return bcrypt.generate_password_hash(password).decode("utf-8")