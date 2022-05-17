from flask import Blueprint, request, abort, make_response, jsonify
from api import db
from api.schema import post_input, post_response
from api.models import Post
from marshmallow import ValidationError

posts = Blueprint("posts", __name__)

@posts.route("/post/new", methods=["POST"])
def new_post():
    post_info = request.get_json()
    desirialized_post = post_input.load(post_info)
    
    new_post = Post(**desirialized_post)
    db.session.add(new_post)
    db.session.commit()     
        
    serialized_post = post_input.dump(new_post)
    response = make_response(serialized_post, 201)
        
    return response

@posts.route("/posts", methods=["GET"])
def get_posts():
    posts = Post.query.all()
    serialized_posts = post_response.dump(posts, many=True)
    print(serialized_posts)
    response = make_response(jsonify(serialized_posts), 200)
    
    return response

@posts.route("/post/<int:post_id>", methods=["POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    serialized_post = post_response.dump(post)
    response = make_response(serialized_post, 200)
    
    return response

@posts.route("/post/<int:post_id>/update", methods=["PUT"])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    post_info = request.get_json()
    deserialized_post = post_input.load(post_info)
    
    post.title = deserialized_post["title"]
    post.content = deserialized_post["content"]
    
    db.session.commit()
    response = make_response("Success", 201)
    
    return response

@posts.route("/post/<int:post_id>/delete", methods=["DELETE"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    response = make_response("Success", 200)
    return response
    
    
        
        
        