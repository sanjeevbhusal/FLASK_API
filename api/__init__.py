from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from api.config import Config

app = Flask(__name__) 
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt()
CORS(app, origins=["*"])
    
from api.main.routes import main
from api.users.routes import users
from api.posts.routes import posts


app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(posts)