from flask import Blueprint, request,jsonify
from api import db
from api.schema import post_input, post_response, vote_input
from api.models import Post, Vote, User
from api.utils import token_required
from marshmallow import ValidationError
from sqlalchemy import select, func, text
import copy
from sqlalchemy.orm import load_only

posts = Blueprint("posts", __name__)

@posts.route("/posts/new", methods=["POST"])
@token_required
def new_post(user):
    data = request.get_json()
    try:
        data = post_input.load(data)
        data["user_id"] = user.id
        post = Post(**data)
        db.session.add(post)
        db.session.commit()     
    except ValidationError as err:
        return {"message" : err.messages}
        
    return {"message" : 'Post has been Created.'}

@posts.route("/posts", methods=["GET"])
def get_posts():
    limit = 8
    skip = 0
    search = ""
    
    if request.args.get("limit"):
        limit = request.args.get("limit")
    if request.args.get("skip"):
        skip = request.args.get("skip")
    if request.args.get("search"):
        search = request.args.get("search")
  
    query = db.session.query(Post).join(Vote, Post.id == Vote.post_id, isouter=True).group_by(Post.id).filter(Post.title.contains(search)).limit(limit).offset(skip). with_entities(Post, func.count(Vote.post_id)).all()
    
    posts = []
    for collection in query :
        post, votes = collection
        post.votes = votes
        post.user = User.query.get(post.user_id)
        posts.append(post)

    posts = post_response.dump(posts, many=True)
         
    return {"posts" : posts}

@posts.route("/posts/<int:post_id>", methods=["GET"])
def post(post_id):
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist."}
     
    query = db.session.query(Post).join(Vote, Post.id == Vote.post_id, isouter=True).group_by(Post.id).filter(Post.id == post_id).with_entities(Post, func.count(Vote.post_id)).first()
    
    post, votes = query
    post.votes = votes
    post.user = User.query.get(post.user_id)
    post = post_response.dump(post)
    return {"message" : post}

@posts.route("/posts/<int:post_id>/update", methods=["PUT"])
@token_required
def update_post(user, post_id):
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist."}
     
    if user.email != "bhusalsanjeev23@gmail.com" and post.user_id != user.id:
        return {"message" : "You are not authorized to perform this operation."}
    
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
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist."}
    
    if user.email != "bhusalsanjeev23@gmail.com" and post.user_id != user.id:
        return {"message" : "You are not authorized to perform this operation."}
    
    db.session.delete(post)
    db.session.commit()

    return {"message" : 'Deleted Succesfully.'}
    
@posts.route("/vote", methods=["POST"])
@token_required
def vote(user):
    data = request.get_json()
    data = vote_input.load(data)
    post = Post.query.filter_by(id = data["post_id"]).first()
    
    if not post :
        return {"message": "The Post doesnot exist."}
    
    already_voted = Vote.query.filter_by(post_id = data["post_id"], user_id = user.id).first()
    
    if already_voted :
        db.session.delete(already_voted)
        db.session.commit()
        return {"message": "The Vote has been deleted."}
    else:
        new_vote = Vote(user_id = user.id, post_id = data["post_id"]) 
        db.session.add(new_vote)
        db.session.commit()
        return {"message": "The Vote has been created."}
        
        
        
        
    
    

    
        
        
        