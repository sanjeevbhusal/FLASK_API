from flask import Flask, request
# from flask_sqlalchemy import SQLAlchemy
import psycopg2
from psycopg2.extras import RealDictCursor
from marshmallow import Schema, fields

app = Flask(__name__) 
# app.config["SQL_ALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost/flaskapi"


class UserSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
user_schema = UserSchema()

try :
    conn = psycopg2.connect(host = "localhost", database = "flask_api", 
    user = "postgres", password = "1234", cursor_factory = RealDictCursor) 
    cursor = conn.cursor()
    print("Connection was Succesfull.")
    
except Exception as e :
    print("Exception Occurred", e)
    
    
@app.route("/")
def home():
    cursor.execute(""" SELECT * FROM users """)
    users = cursor.fetchall()
    return users

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        request_data = request.get_json()
        
        deserialized_user = user_schema.load(request_data)
        cursor.execute("""INSERT INTO users (username, email, password) 
                       VALUES (%s, %s, %s) RETURNING *""", 
                       (deserialized_user["username"], deserialized_user["email"],
                        deserialized_user["password"]))
        
        new_user = cursor.fetchone()
        conn.commit()
        
        return new_user
        
     

# Authentication

if __name__ == "__main__":
    app.run(debug = True)
    

        
