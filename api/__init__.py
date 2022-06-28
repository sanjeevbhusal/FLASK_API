from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail
from api.config import Config
from flask_restful import Api

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()


def create_app(config=Config):
    app = Flask(__name__) 
    app.config.from_object(config)
    api = Api(app)
    
    api.init_app(app)
    db.init_app(app)    
    mail.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=["*"])
    
    from api.main.routes import Main
    from api.users.routes import Register
    from api.users.routes import Login
    from api.users.routes import UsersList
    from api.users.routes import UserById
    from api.users.routes import GenerateToken
    from api.users.routes import VerifyToken
    from api.users.routes import ResetPassword
    from api.posts.routes import CreatePost
    from api.posts.routes import PostsList
    from api.posts.routes import PostsById
    from api.posts.routes import UnverifiedPost
    from api.posts.routes import Comments
    
    api.add_resource(Main, "/")
    api.add_resource(Register, "/register")
    api.add_resource(Login, "/login")
    api.add_resource(UsersList, "/users")
    api.add_resource(UserById, "/users/<int:id>")
    api.add_resource(GenerateToken, "/generate_token/<string:email>")
    api.add_resource(VerifyToken, "/verify_token/<token>")
    api.add_resource(CreatePost, "/posts/new")
    api.add_resource(PostsList, "/posts")
    api.add_resource(PostsById, "/posts/<int:id>")
    api.add_resource(UnverifiedPost, "/posts/review_posts", "/posts/update_post_status")
    api.add_resource(Comments, "/comments/<int:id>")
    return app
