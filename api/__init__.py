from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from api.config import Config
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()

def create_app(config=Config):
    app = Flask(__name__) 
    app.config.from_object(config)
    app.config['MAIL_SERVER']='smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = '7333153070b432'
    app.config['MAIL_PASSWORD'] = 'ce7347484a0'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
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
