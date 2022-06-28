from marshmallow import Schema, fields, validates_schema, ValidationError

class User(Schema):
    id = fields.Integer(required=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    is_admin = fields.Boolean(required=True)
    created_at = fields.DateTime(required=True)
    
class Post(Schema):
    id  = fields.Integer(required=True)
    title = fields.String(required=True)
    content = fields.String(required=True)
    category = fields.String(required=True)
    created_at = fields.DateTime(required=True) 
    
class Comment(Schema):
    id = fields.Integer(required=True)
    message = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    author = fields.Nested(User, required=False)
    
#***********************************************************************************    

class UserRegister(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    is_admin = fields.Boolean(default=False)
    
    
class UserLogin(Schema):
    username = fields.Email(required=True)
    password = fields.String(required=True)
       
class UserUpdate(Schema):
    username = fields.String(required=True)
    
class UserResponse(User):
    posts = fields.List(fields.Nested(Post))
    comments = fields.List(fields.Nested(Comment))
    
class ResetPassword(Schema):
    password = fields.String(required=True)
    confirm_password = fields.String(required=True)
    
    @validates_schema
    def compare_passwords(self, data, **kwargs):
        if data["password"] != data["confirm_password"] :
            raise ValidationError("Password and Confirm Password should be same")
    
#*********************************************************************************** 
    
class VoteInput(Schema):
    post_id = fields.Integer(required=True)
    
class VoteResponse(VoteInput):
    user_id = fields.Integer(required=True)
    
    
class BytesField(fields.Field) :
    def _validate(self, data):
        if data is None :
            return
        if not isinstance(data, bytes) :
            raise ValidationError("Not a Valid Image")
        
class CategoryMismatchException(Exception):
    pass
    
class PostRegister(Schema):
    title = fields.String(required=True)
    content = fields.String(required=True)
    category = fields.String(required=True)
    image = fields.String()
    
    @validates_schema
    def validate_category(self, data, **kwargs):
        available_categories = ["LatestOffer", "NewEvent", "Careers", "Stories", "Trending"]
  
        if data["category"] not in available_categories :
            raise CategoryMismatchException()
    
class PostUpdate(PostRegister):
    author = fields.Nested(User)
     
class PostResponse(Post):
    author = fields.Nested(User)
    comments = fields.List(fields.Nested(Comment))
    votes = fields.List(fields.Nested(VoteResponse))
    image= fields.String()
     
class PostReview(Schema):
    is_accepted = fields.Boolean(required=True)
    rejected_reason = fields.String()
    
    @validates_schema
    def validate_rejected_reason(self, data, **kwargs):
        if data["is_accepted"] == False and "rejected_reason" not in data:
            raise Exception()
    

#*********************************************************************************** 

class CommentRegister(Schema):
    message = fields.String(required=True)

class CommentResponse(Comment):
    author = fields.Nested(User)
    # post  = fields.Nested(Post)
   
class CommentUpdate(Schema):
    message = fields.String(required=True)
    
                
user_register = UserRegister()
user_login = UserLogin()
user_update = UserUpdate()
reset_password = ResetPassword()
user_response = UserResponse()

post_register = PostRegister()
post_review = PostReview()
post_response = PostResponse()
post_update = PostRegister()


vote_input = VoteInput()

comment = Comment()
comment_register = CommentRegister()
comment_update = CommentUpdate()
comment_response = CommentResponse()
