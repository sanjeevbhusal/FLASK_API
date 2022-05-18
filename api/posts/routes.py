from flask import Blueprint, request,jsonify
from api import db
from api.schema import post_input, post_response
from api.models import Post
from api.utils import token_required
from marshmallow import ValidationError

posts = Blueprint("posts", __name__)

@posts.route("/posts/new", methods=["POST"])
@token_required
def new_post(user):
    data = request.get_json()
    
    if user.email != "bhusalsanjeev23@gmail.com":
        return {"message" : "You are not Authorized to Create a Post"}
    
    try:
        data = post_input.load(data)
        post = Post(**data)
        db.session.add(post)
        db.session.commit()     
    except ValidationError as err:
        return {"message" : err.messages}
        
    return {"message" : 'Post has been Created.'}

@posts.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    posts = post_response.dump(posts, many=True)
    
    return {"message" : posts}

@posts.route("/posts/<int:post_id>", methods=["GET"])
def post(post_id):
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist."}
     
    post = post_response.dump(post)
    return {"message" : post}

@posts.route("/posts/<int:post_id>/update", methods=["PUT"])
@token_required
def update_post(user, post_id):
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist."}
    
    try:
        data= request.get_json()
        data = post_input.load(data)
    
        post.title = data["title"]
        post.content = data["content"]
        db.session.commit()
    except ValidationError as err :
        return {"message" : err.messages}
    return {"message" : "The Post has been Updated."}


@posts.route("/posts/<int:post_id>/delete", methods=["DELETE"])
@token_required
def delete_post(user, post_id):
    if user.email != "bhusalsanjeev23@gmail.com":
        return {"message" : "You are not Authorized to Create a Post"}

    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist."}
    
    db.session.delete(post)
    db.session.commit()

    return {"message" : 'Deleted Succesfully.'}
    
    
        
        
        