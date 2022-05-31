from marshmallow import Schema, fields, validates_schema, ValidationError

class UserSchema(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)

class UserInput(UserSchema):
    password = fields.String(required=True)
    is_admin = fields.Boolean(required=True)
    
class UserLoginInput(Schema):
    username = fields.Email(required=True)
    password = fields.String(required=True)
    
class UserUpdateInput(UserSchema):
    password = fields.String(required=True)
    
class UserResponse(UserSchema):
    id = fields.Integer(required=True)
    is_admin = fields.Boolean(required=True)
    created_at = fields.DateTime(required=True)
    
class PostSchema(Schema):
    title = fields.String(required=True)
    content = fields.String(required=True)
    category = fields.String(required=True)

class PostInput(PostSchema):
    
    @validates_schema
    def validate_category(self, data, **kwargs):
        category = ["LatestOffer", "NewEvent", "Careers", "Stories", "Trending"]
        if data["category"] not in category :
            raise Exception()
            
            
class PostResponse(PostSchema):
    id = fields.Integer(required=True)
    votes = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)
    user = fields.Nested(UserResponse)
    
class PostReviewInput(Schema):
    is_accepted = fields.Boolean(required=True)
    rejected_reason = fields.String()
    
    @validates_schema
    def validate_rejected_reason(self, data, **kwargs):
        if data["is_accepted"] == False and "rejected_reason" not in data:
            raise Exception()
        
class ResetUserPassword(Schema):
    user_id = fields.Integer(required=True)
    password = fields.String(required=True)
    confirm_password = fields.String(required=True)
    
    @validates_schema
    def compare_passwords(self, data, **kwargs):
        if data["password"] != data["confirm_password"] :
            raise ValidationError("Password and Confirm Password should be same")
    
class VoteInput(Schema):
    post_id = fields.Integer(required=True)

    
user_input = UserInput()
user_response = UserResponse()
post_input = PostInput()
post_response = PostResponse()
vote_input = VoteInput()
post_review_input = PostReviewInput()
user_login_input = UserLoginInput()
user_update_input = UserUpdateInput()
reset_user_password = ResetUserPassword()
    