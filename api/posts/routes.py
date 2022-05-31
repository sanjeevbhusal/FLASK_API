from flask import Blueprint, request,jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func, text
from sqlalchemy.orm import load_only
from marshmallow import ValidationError

from api import db
from api.models import Post, Vote, User
from api.schema import post_input, post_response, vote_input, post_review_input 
from api.utils import token_required, admin_token_required, get_post_by_id, is_user_author, is_user_admin


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
        return {"message" : err.messages}, 400
    except Exception as err:
        return {"message" : "The category you choosed isn't available."}, 400
        
    return {"message" : 'Post has been Created'}
    
@posts.route("/posts", methods=["GET"])
def get_posts():
    page = int(request.args.get("page")) if request.args.get("page") else 1
    per_page = int(request.args.get("perpage")) if request.args.get("perpage") else 10
    search =  request.args.get("search") if request.args.get("search") else ""
    category =  request.args.get("category") if request.args.get("category") else ""
    
    # query = db.session.query(Post).join(Vote, Post.id == Vote.post_id, isouter=True).group_by(Post.id).filter(Post.title.contains(search)).limit(limit).offset(skip). with_entities(Post, func.count(Vote.post_id)).all()
      
    if category :
        posts = db.session.query(Post).\
        join(Vote, Post.id == Vote.post_id, isouter=True).\
        group_by(Post.id).\
        filter(Post.category == category).\
        order_by(Post.created_at).\
        offset((page * per_page) - per_page).\
        limit(per_page).\
        with_entities(Post, func.count(Vote.post_id)).all()
    else:
         posts = db.session.query(Post).\
        join(Vote, Post.id == Vote.post_id, isouter=True).\
        group_by(Post.id).\
        order_by(Post.created_at).\
        offset((page * per_page) - per_page).\
        limit(per_page).\
        with_entities(Post, func.count(Vote.post_id)).all()
        
    
    posts_with_user = []
    for collection in posts :
        post, votes = collection
        post.votes = votes
        post.user = User.query.get(post.user_id)
        posts_with_user.append(post)

    posts = post_response.dump(posts_with_user, many=True)
         
    return {"posts" : posts}

@posts.route("/posts/<int:post_id>", methods=["GET"])
def post(post_id):
    post = get_post_by_id(post_id)
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    post_with_votes = db.session.query(Post).\
            join(Vote, Post.id == Vote.post_id, isouter=True).\
            group_by(Post.id).\
            filter(Post.id == post_id).\
            with_entities(Post, func.count(Vote.post_id)).\
            first()
    
    post, votes = post_with_votes
    post.votes = votes
    post.user = User.query.get(post.user_id)
    
    post = post_response.dump(post)
    return {"post" : post}, 200

@posts.route("/posts/<int:post_id>/update", methods=["PUT"])
@token_required
def update_post(user, post_id):
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    post_author = is_user_author(user.id, post.user_id)
    admin = is_user_admin(user)
     
    if admin != "False" and not post_author:
        return {"message" : "You are not authorized to perform this operation."}, 403
    
    try:
        data= request.get_json()
        data = post_input.load(data)
    
        post.title = data["title"]
        post.content = data["content"]
        db.session.commit()
    except ValidationError as err :
        return {"message" : err.messages}, 201
    return {"message" : "The Post has been Updated."}


@posts.route("/posts/<int:post_id>/delete", methods=["DELETE"])
@token_required
def delete_post(user, post_id):
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    post_author = is_user_author(user.id, post.user_id)
    admin = is_user_admin(user)
     
    if admin != "False" and not post_author:
        return {"message" : "You are not authorized to perform this operation."}, 403
    
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
        
@posts.route("/review_posts", methods=["GET"])
@admin_token_required
def review_posts(user):
    posts = Post.query.filter_by(is_reviewed= False)
    posts = post_response.dump(posts, many=True)
    return {"posts" : posts}


@posts.route("/update_post_reviewed/<int:post_id>", methods=["POST"])
@admin_token_required
def update_post_reviewed(user,post_id):
    
    post = get_post_by_id(post_id)
    if not post :
        return {"message": "The Post doesnot Exist."}, 400

    data = request.get_json()
    
    try:
        data = post_review_input.load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 401
    except Exception :
        return {"message" : "Rejecetd Reason is also required if Rejected is True"}, 401

    if data.get("is_accepted"):
        post.is_accepted = True
        #send accepted reason email to the user.
    else:
        post.rejected_reason = data["rejected_reason"]
        #send rejected reason email to the user.
    post.is_reviewed = True
        
    db.session.commit()   
    return {"message" : "Post has been Updated"}, 200
        
        
    
    

    
        
        
        