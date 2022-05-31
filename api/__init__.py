from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from api.config import Config


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config=Config):
    app = Flask(__name__) 
    app.config.from_object(config)
    
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=["*"])
    
    from api.main.routes import main
    from api.users.routes import users
    from api.posts.routes import posts

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    
    
    return app
