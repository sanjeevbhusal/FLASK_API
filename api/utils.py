import jwt
from flask import request, current_app
from flask_mail import Message
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta

from api import bcrypt, mail, db
from api.models import User, Post, Comment
from api.schema import PostRegister, PostUpdate, PostReview , CommentRegister, CommentUpdate, UserRegister, UserLogin, UserUpdate, ResetPassword, UserResponse

class Authenticate() :
    def __init__(self) :
        pass
    def token_required(self, f):
        def wrapper(*args, **kwargs):
            user_token = None
            if "access_token" in request.headers:
                user_token = request.headers["access_token"]
            else:
                return {"message" : "No Token Received"}, 401
            try:
                user_id = token.decode_token(user_token)["user_id"]
                user = user_database.get_by_id(user_id)
                if user is None:
                    return {"status" : "failure", "error": "User with the current token doesnot exist."}, 404
            except ExpiredSignatureError as err :
                return {"status": "failure", "error": "Token has been expired."}, 400
            except InvalidTokenError as err :
                return {"status": "failure", "error": "Token is invalid"}, 400
            return f(user, *args, **kwargs)
        # Renaming the function name:
        wrapper.__name__ = f.__name__
        return wrapper
    def admin_token_required(self, f):
        def wrapper(*args, **kwargs):
            user_token = None
            if "access_token" in request.headers:
                user_token = request.headers["access_token"]
            else:
                return {"message" : "No Token Received"}, 401
            try:
                user_id = token.decode_token(user_token)["user_id"]
                user = user_database.get_by_id(user_id)
                if user is None:
                    return {"status" : "failure", "error": "User with the current token doesnot exist."}, 404
                if user.is_admin == False :
                    return {"message" : "You are not authorized"}, 401
            except ExpiredSignatureError as err :
                return {"status": "failure", "error": "Token has been expired."}, 400
            except InvalidTokenError as err :
                return {"status": "failure", "error": "Token is invalid"}, 400        
            return f(user, *args, **kwargs)
        # Renaming the function name:
        wrapper.__name__ = f.__name__
        return wrapper

class Hashing :
    def __init__(self) :
        pass
    def hash_password(self, password):
        return bcrypt.generate_password_hash(password).decode("utf-8")
    def compare_password(self, hashed_pw, password):
        return bcrypt.check_password_hash(hashed_pw, password)

class UserDatabase :
    def __init__(self) :
        pass
    def get_by_email(self, email) :
        return User.query.filter_by(email = email).first()
    def get_by_id(self, id) :
        return User.query.get(id)
    def delete_by_email(self, email) :
        user = self.get_by_email(email)
        db.session.delete(user) 
    def delete_user(self, user) :
        db.session.delete(user)
        db.session.commit()
    def update_password(self, user, password) :
        user.password =  self.hash_password(password)
        db.session.commit()
    def create_user(self, username, email, password) :
        return User(username = username, email = email, password = hashing.hash_password(password))
    def check_password(self, db_password, password,) :
        return bcrypt.check_password_hash(db_password, password)
    def hash_password(self, password) :
        return bcrypt.generate_password_hash(password).decode("utf-8")
    def update_user(self) :
        db.session.commit()
    def save(self, user) :
        db.session.add(user)
        db.session.commit()
        
class PostDatabase :
    def __init__(self) :
        pass
    def verify_post(self, post) :
        post.is_reviewed = True
        post.is_accepted = True
        db.session.commit()
    def create_post(self, user_id, title, content, category, image) :
        return Post(user_id = user_id, title = title, content = content, category = category, image = image)
    def save(self, post) :
        db.session.add(post)
        db.session.commit()
    def get_by_id(self, post_id):
        return Post.query.get(post_id)
    def update_post(self, post, title, content, category):
        post.title = title
        post.content = content
        post.category = category
        db.session.commit()
    def delete_post(self, post) :
        db.session.delete(post)
        db.session.commit()
                
class Token :
    def __init__(self) :
        pass
    def create_token(self, user_id):
        return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes=30)}, current_app.config["SECRET_KEY"])
    def decode_token(self, user_token) :
        return jwt.decode(user_token, current_app.config['SECRET_KEY'], algorithms="HS256")
    def create_login_token(self, user_id):
        return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(hours=24)}, current_app.config["SECRET_KEY"])
    def get_password_reset_token(self, user_id):
        return jwt.encode({"user_id": user_id, "exp": datetime.utcnow() + timedelta(minutes= 30)}, current_app.config["SECRET_KEY"])
    def verify_reset_token(self, user_token):
        token_info = jwt.decode(user_token, current_app.config['SECRET_KEY'], algorithms="HS256")
        user = user_database.get_by_id(token_info["user_id"])
        if not user :
            raise  UserNotFoundException("Couldn't find the user")
        return token_info["user_id"]
    
class EmailGateway :
    def __init__(self) :
        pass
    
    def send_welcome_message(self, email):
        msg = Message("Welcome to Moru Digital Wallet", sender="noreply@gmail.com", recipients= [email])
        msg.body = """Welcome to Moru Digital Wallet. We are glad to have you on board. In order to get the most out of Moru, please confirm your account and fill the KYC(Know Your Customer) form. This will unlock all the features available in Moru Digital Wallet.
    
        Please, click on the link below to verify your account. 
        The link expires in 30 minutes.
        
        https://moru-blog.herokuapp.com/verify_email/verify_email?token="sssssssssssssssssss
        
        This is a automated generated email. Please donot reply this email.
        """
        mail.send(msg)
        
    def send_reset_password_email(self, email, token):
        msg = Message("Reset Your Password", sender="noreply@gmail.com", recipients= [email])
        msg.body = f"""

        Click on the link below to reset your password.

        The link expires in 30 minutes.

        https://moru-blog.herokuapp.com/reset_password/password_change?token={token}

        If you didn't requested to reset your password, kindly ignore this email.
        This is a automated generated email. Please donot reply this email.
        """
    
        mail.send(msg)
       
    def send_post_accepted_email(self, post):
        msg = Message("Congratulations for getting your Post accepted!", sender="moru@gmail.com", recipients= [post.author.email])
        msg.body = f"""
        Congratulations {post.author.username}, 
        Recently, you wrote a Article titled {post.title}. Our review team has carefully reviewed the Article and we are more than happy to let you know that your Article has been accepted. 
    
        Thank You for sharing your knowledge with the world.
        Keep Writing!!!

        Best Wishes from MORU Digital Wallet.
        """
        mail.send(msg)

    def send_post_rejected_email(self, post):
        msg = Message("Regarding the recent article you wrote on blog.moru.com.", sender="noreply@gmail.com", recipients= [post.author.email])
        msg.body = f"""
        Dear {post.author.username}, 
        Recently, you wrote a Article titled {post.title}. Our team has carefully reviewed the Article and we feel very sorry to inform you that we have decided not to go forward with your Article. 

        We receive a lot of Article requests and we try our best to select those which provide a great value to our readers. Below is the reason, we decided not to accept your article. We also have delted the article

        {post.rejected_reason}
    
        Don't let this rejection stop you from writing articles. 
        Keep Writing!!!

        Best Wishes from MORU Digital Wallet.
        """
        mail.send(msg)

class DuplicateEmailException(Exception) :
    pass
class UserNotFoundException(Exception) :
    pass
class IncorrectPasswordException(Exception) :
    pass
class UnautorizedAccessException(Exception) :
    pass  
class PostNotFoundException(Exception) :
    pass
class PostAlreadyVerifiedException(Exception) :
    pass
class CommentNotFoundException(Exception) :
    pass
class ValidateRoutes :
    def __init__(self):
        pass
    
    def register(self, data) :
        schema = UserRegister()
        result = schema.load(data)
        existing_user = user_database.get_by_email(result["email"])   
        if existing_user :
            raise DuplicateEmailException("User with such email address already exists.")
        result["password"] = user_database.hash_password(result["password"])
        return result
    
    def login(self, data) :
        schema = UserLogin()
        response_schema = UserResponse(exclude=["posts", "comments", "created_at"])
        result = schema.load(data)
        
        existing_user = user_database.get_by_email(result["email"]) 
        if not existing_user :
            raise UserNotFoundException("Couldn't find the User") 
        
        correct_password = user_database.check_password(existing_user.password, result["password"])
        if not correct_password :
            raise IncorrectPasswordException("Please Enter Correct Password")
        return response_schema.dump(existing_user)
    
    def update_user(self, user, user_id, data) :
        schema = UserUpdate()
        result = schema.load(data)

        if user.is_admin == False and user.id != user_id :
            raise UnautorizedAccessException("You are not authorized")
        
        existing_user = user_database.get_by_id(user_id)
        if not existing_user :
            raise UserNotFoundException("Couldn't find the User") 
        
        return {"user" : existing_user, "result" : result}
    
    def delete_user(self, user, user_id):
        if user.is_admin == False and user.id != user_id :
            raise UnautorizedAccessException("You are not authorized")
        
        existing_user = user_database.get_by_id(user_id)
        if not existing_user :
            raise UserNotFoundException("Couldn't find the User") 
        
        should_redirect = user.is_admin != True or user.id == existing_user.id
            
        return {"user" : existing_user, "should_redirect" : should_redirect}

    def reset_password(self, data, user_token) :
        schema = ResetPassword()
        result = schema.load(data)
        user_id = token.verify_reset_token(user_token)    
        return {"result" : result, "user_id" : user_id}
    
    def create_post(self, data) :
        schema = PostRegister()
        result = schema.load(data)
        return {"title" : result["title"], "content" : result["content"], "category" : result["category"], "image" : result["image"]}
    
    def update_post(self, data, post_id, user):
        schema = PostUpdate()
        result = schema.load(data)
        post = post_database.get_by_id(post_id)  
        if not post :
            raise PostNotFoundException("Couldn't find the Post")
        if user.is_admin == False and user.id != post.author.id :
            raise UnautorizedAccessException("You are not authorized")
        
        return {"result" : result, "post" : post}
    
    def delete_post(self, user, post_id) :
        post = post_database.get_by_id(post_id)
        if not post :
            raise PostNotFoundException("Couldn't find the Post'")
        if user.is_admin == False and user.id != post.author.id :
            raise UnautorizedAccessException("You are not authorized")
        return post
    
    def update_post_status(self, data, post_id) :
        schema = PostReview()
        result = schema.load(data)
        post = post_database.get_by_id(post_id)
        if not post :
            raise PostNotFoundException("Couldn't find the Post")
        if post.is_reviewed == True :
            raise PostAlreadyVerifiedException("Post is already verified")
        return {"result" : result, "post_object" : post}

    def add_comment(self, data, post_id) :
        schema = CommentRegister()
        result = schema.load(data)
        post = post_database.get_by_id(post_id)
        if not post :
            raise PostNotFoundException("The Post doesnot exist")
        return result
    
    def update_comment(self, data, comment_id, user) :
        schema = CommentUpdate()
        result = schema.load(data)
        comment = Comment.query.get(comment_id)
        if not comment :
            raise CommentNotFoundException("Comment doesnot exist")
        if user.is_admin == False and user.id != comment.author.id :
            raise UnautorizedAccessException("You are not authorized")
        return result, comment
    
    def delete_comment(self, comment_id, user) :
        comment = Comment.query.get(comment_id)
        if not comment :
            raise CommentNotFoundException("Comment doesnot exist")
        if user.is_admin == False and user.id != comment.user_id :
            raise UnautorizedAccessException("You are not authorized")
        
        return comment
  
validate_routes = ValidateRoutes()
email_gateway = EmailGateway()
authenticate = Authenticate() 
hashing = Hashing()       
user_database = UserDatabase()     
post_database = PostDatabase()
token = Token()



    







        