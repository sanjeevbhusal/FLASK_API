from marshmallow import Schema, fields

class UserInput(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
class UserResponse(Schema):
    id = fields.Integer(required=True)
    username = fields.String(required=True)
    email = fields.Email(required=True)
    
class PostInput(Schema):
    title = fields.String(required=True)
    content = fields.String(required=True)
    
class PostResponse(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    content = fields.String(required=True)
    votes = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)
    user = fields.Nested(UserResponse)
    
class VoteInput(Schema):
    post_id = fields.Integer(required=True)
    
    
user_input = UserInput()
user_response = UserResponse()
post_input = PostInput()
post_response = PostResponse()
vote_input = VoteInput()
    