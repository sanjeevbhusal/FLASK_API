from flask import Blueprint, request
from marshmallow import ValidationError
from marshmallow import ValidationError

from api import db
from api.models import Post, Vote, Comment
from api.schema import post_response, vote_input, post_review, post_register, post_update, comment_register, comment_response, comment_update
from api.utils import token_required, admin_token_required, get_post_by_id,send_post_accepted_email, send_post_rejected_email
from sqlalchemy import or_


posts = Blueprint("posts", __name__)

@posts.route("/posts/new", methods=["POST"])
@token_required
def create_new_post(user):

    data = request.get_json()
    
    try:
        data = post_register.load(data)
        data["user_id"] = user.id
        post = Post(**data)
        
        db.session.add(post)
        db.session.commit()     
    except ValidationError as err:
        return {"message" : err.messages}, 400
    except Exception as err:
        return {"message" : "The category you choosed isn't available."}, 400
        
    return {"message" : 'Post has been Created'}, 201
    
@posts.route("/posts", methods=["GET"])
def get_all_posts():
    
    page = request.args.get("page", 1, type=int) 
    per_page = request.args.get("perpage", 10, type=int)
    search =  request.args.get("search", "") 
    category =  request.args.get("category", "") 
    
    all_filters = [or_(Post.title.ilike(f'%{search}%'), Post.content.ilike(f'%{search}%'))]
    if category :
        all_filters.append(Post.category == category)
    
    posts = Post.query.filter(*all_filters).paginate(page= page, per_page= per_page)

    posts = post_response.dump(posts.items, many=True)
         
    return {"posts" : posts}, 200

@posts.route("/posts/<int:post_id>", methods=["GET"])
def get_single_post(post_id):
    
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
    
    post = post_response.dump(post)
    return {"post" : post}, 200

@posts.route("/posts/<int:post_id>", methods=["PUT"])
@token_required
def update_single_post(user, post_id):
     
    try:
        data= request.get_json()
        data = post_update.load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 201
    
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    if user.is_admin != "False" and not post.author.id == user.id:
        return {"message" : "You are not authorized to perform this operation."}, 403
       
    post.title = data["title"]
    post.content = data["content"]
    post.category = data["category"]
    
    db.session.commit()

    return {"message" : "The Post has been Updated."}, 200

@posts.route("/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_single_post(user, post_id):
    
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    if user.is_admin != "False" and not post.author.id == user.id:
        return {"message" : "You are not authorized to perform this operation."}, 403
    
    db.session.delete(post)
    db.session.commit()

    return {"message" : 'Deleted Succesfully.'}, 200
    
@posts.route("/vote", methods=["POST"])
@token_required
def vote(user):
    
    data = request.get_json()
    
    try:
        data = vote_input.load(data)
    except ValidationError as err :
        return {"message", err.messages}, 400
    
    post = Post.query.filter_by(id = data["post_id"]).first()
    
    if not post :
        return {"message": "The Post doesnot exist."}, 404
    
    #if user has already voted on this post, remove the vote.
    vote = Vote.query.filter_by(post_id = data["post_id"], user_id = user.id).first()
    if vote :
        db.session.delete(vote)
        db.session.commit()
        
        return {"message": "The Vote has been deleted."}
    else:
        new_vote = Vote(user_id = user.id, post_id = data["post_id"]) 
        db.session.add(new_vote)
        db.session.commit()
        
        return {"message": "The Vote has been created."}
        
@posts.route("/review_posts", methods=["GET"])
@admin_token_required
def review_all_posts(user):
    
    posts = Post.query.filter_by(is_reviewed= False)
    posts = post_response.dump(posts, many=True)
    
    return {"posts" : posts}, 200

@posts.route("/update_post_status/<int:post_id>", methods=["PUT"])
@admin_token_required
def update_post_status(user,post_id):
    
    data = request.get_json()
    
    try:
        data = post_review.load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 401
    # except Exception :
    #     return {"message" : "Rejecetd Reason is also required if The Post has been Rejeted"}, 401

    post = get_post_by_id(post_id)
    
    if not post :
        return {"message": "The Post doesnot Exist."}, 404
    
    if data.get("is_accepted"):
        post.is_accepted = True
        send_post_accepted_email(post.author.email)
    else:
        post.rejected_reason = data["rejected_reason"]
        send_post_rejected_email(post.author.email, data["rejected_reason"])
    
    post.is_reviewed = True
    
    db.session.commit()   
    
    return {"message" : "Post has been Updated"}, 200
        
@posts.route("/comments", methods=["POST"])
@token_required
def add_comment(user):
    try:
        comment = comment_register.load(data)
    except ValidationError as err :
        return {"message": err.messages}, 400
    
    data = request.get_json()
    
    post = Post.query.get(data["post_id"])
    
    if not post :
        return {"message": "The Post doesnot exist."}, 400
    
    comment = Comment(**data, user_id = user.id)
    
    db.session.add(comment)
    db.session.commit()
    
    return {"message" : "Success"}, 201
    
           
@posts.route("/comments/<int:post_id>", methods=["GET"])
def get_comment(post_id):
    
    post = Post.query.get(post_id)
    
    if not post :
        return {"message": "The Post doesnot exist."}, 400
    
    comments = comment_response.dump(post.comments, many=True)
    
    return {"comments" : comments}, 200

@posts.route("/comments/<int:comment_id>", methods=["PUT"])
@token_required
def update_comment(user, comment_id):
    try:
        comment_update.load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 400
    
    data = request.get_json()
    
    comment = Comment.query.get(comment_id)
    
    if not comment :
        return {"message" : "Comment doesnot exist"}, 404
    
    if user.is_admin == False and user.id != comment.author.id :
         return {"message" : "You can only update your own comment"}, 403
    
    comment.message = data["message"]
    db.session.commit()
    
    return {"message" : "Updated Succesfully."}, 200
    P

@posts.route("/comments/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(user, comment_id):
    
    comment = Comment.query.get(comment_id)
    
    if not comment :
        return {"message" : "Comment doesnot exist"}, 404
    
    if user.is_admin == False and user.id != comment.user_id :
         return {"message" : "You can only delete your own comment"}, 403
        
    db.session.delete(comment)
    db.session.commit()
    
    return {"message" : "Deleted Succesfully"}, 200
    
        
    
    

    
        
        
        