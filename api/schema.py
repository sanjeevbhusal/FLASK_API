from marshmallow import Schema, fields

class UserInput(Schema):
    username = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
class UserResponse(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)
    
class PostInput(Schema):
    title = fields.String(required=True)
    content = fields.String(required=True)
    
class PostResponse(Schema):
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    content = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    
    
user_input = UserInput()
user_response = UserResponse()
post_input = PostInput()
post_response = PostResponse()
    