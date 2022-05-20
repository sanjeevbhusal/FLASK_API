from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from api.config import Config

app = Flask(__name__) 
db = SQLAlchemy(app)
bcrypt = Bcrypt()
app.config.from_object(Config)
    
from api.main.routes import main
from api.users.routes import users
from api.posts.routes import posts


app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(posts)