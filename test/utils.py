from flask import current_app
from config import app
import jwt
from datetime import datetime, timedelta
def get_jwt(user_id) :
    with app.app_context():
        token = jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(days= 365 )}, current_app.config["SECRET_KEY"])
        return token
    