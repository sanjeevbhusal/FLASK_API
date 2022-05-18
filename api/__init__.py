from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_bcrypt import Bcrypt

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:1234@localhost/flask_api"
app.config["SECRET_KEY"] = 'iamasecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt()

try :
    conn = psycopg2.connect(host = "localhost", database = "flask_api", 
    user = "postgres", password = "1234", cursor_factory = RealDictCursor) 
    cursor = conn.cursor()
    print("Connection was Succesfull.")
    
except Exception as e :
    print("Exception Occurred", e)
    
from api.main.routes import main
from api.users.routes import users
from api.posts.routes import posts


app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(posts)