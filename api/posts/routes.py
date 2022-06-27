from flask import Blueprint, request
from sqlalchemy import or_

from api import db
from api.models import Post, Vote, Comment
from api.schema import  PostResponse, PostUpdate, CommentResponse
from api.utils import token_required, admin_token_required, send_post_accepted_email, send_post_rejected_email, validate_create_new_post_route, validate_update_single_post_route,validate_delete_single_post_route, validate_update_post_status_route, validate_add_comment_route, validate_update_comment_route, validate_delete_comment_route


posts = Blueprint("posts", __name__)

@posts.route("/posts/new", methods=["POST"])
@token_required
def create_new_post(user):
    data = request.form
    data = validate_create_new_post_route(data)
    if data["status"] == "failure" :
        return data, data["code"]
    
    post_details = data["post_details"]
    post_details["user_id"] = user.id
    if user.is_admin == True :
        post_details["is_reviewed"] = True
        post_details["is_accepted"] = True 
        
    new_post = Post(**post_details)
    db.session.add(new_post)
    db.session.commit()     
    post = PostResponse(exclude=["comments"]).dump(new_post)
    
    return {**data, "post_details" : post}, data["code"]

    
@posts.route("/posts", methods=["GET"])
def get_all_posts():
    page = request.args.get("page", 1, type=int) 
    per_page = request.args.get("perpage", 10, type=int)
    search =  request.args.get("search", "") 
    category =  request.args.get("category", "") 
    
    all_filters = [or_(Post.title.ilike(f'%{search}%'), Post.content.ilike(f'%{search}%')),Post.is_accepted == True]
    if category :
        all_filters.append(Post.category == category)
    
    # posts = Post.query.filter(*all_filters).paginate(page= page, per_page= per_page)
    posts = Post.query.filter(*all_filters).order_by(Post.created_at.desc())
    posts = PostResponse().dump(posts, many=True)
    
    # for post in posts :
    #     if post["image"]:
    #         post["image"] = url_for("static", filename="blog_pictures/" + post["image"], _external=True) 
    return {"status" : "success", "code" : 200, "posts" : posts}, 200

@posts.route("/posts/<int:post_id>", methods=["GET"])
def get_single_post(post_id):
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
    post = PostResponse().dump(post)
          
    return {"status" : "success", "code" : 200, "post" : post}, 200

@posts.route("/posts/<int:post_id>", methods=["PUT"])
@token_required
def update_single_post(user, post_id):
    data = request.get_json()
    data = validate_update_single_post_route(data, post_id, user)
    if data["status"] == "failure":
        return data, data["code"]
    
    post = data["post"]  
    credentials = data["credentials"]
    
    post.title = credentials["title"]
    post.content = credentials["content"]
    post.category = credentials["category"]
    db.session.commit()
    updated_post = PostUpdate().dump(post)
    
    return {**data, "post" : updated_post} ,data["code"]

@posts.route("/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_single_post(user, post_id):
    data = validate_delete_single_post_route(user, post_id)
    if data["status"] == "failure" :
        return data, data["code"]
    
    post = data["post"]
    db.session.delete(post)
    db.session.commit()
    
    data.pop("post")
    return data, data["code"]
    
@posts.route("/vote/<int:post_id>", methods=["POST"])
@token_required
def create_vote(user, post_id):
    post = Post.query.get(post_id)
    if not post :
        return {"status": "failure", "code": 404, "message" : "The Post doesnot exist."}, 404
    
    all_votes = len((Vote.query.filter_by(post_id = post_id)).all())
    
    #if user has already voted on this post, remove the vote.
    vote = Vote.query.filter_by(post_id = post_id, user_id = user.id).first()
    if vote :
        db.session.delete(vote)
        db.session.commit()
        return {"status" : "success", "code" : 200, "votes": all_votes - 1, "message" : "Your Like has been removed succesfully.", "has_voted" : False}
    else:
        new_vote = Vote(user_id = user.id, post_id = post_id) 
        db.session.add(new_vote)
        db.session.commit()
        return {"status" : "success", "code" : 200, "votes": all_votes + 1, "message" : "Your Like has been removed succesfully.", "has_voted" : True}
        
@posts.route("/review_posts", methods=["GET"])
@admin_token_required
def review_all_posts(user):
    posts = Post.query.filter_by(is_reviewed= False)
    posts = PostResponse(exclude=["comments"]).dump(posts, many=True)
    return {"status" : "success", "code" : 200, "posts" : posts, "message": "Here are all the posts to review"}, 200

@posts.route("/update_post_status/<int:post_id>", methods=["PUT"])
@admin_token_required
def update_post_status(user,post_id):
    data = request.get_json()
    data = validate_update_post_status_route(data, post_id)
    if data["status"] == "failure" :
        return data
    
    post = data["post"]
    credentials = data["credentials"]
    is_accepted = True
    if credentials.get("is_accepted"):
        post.is_accepted = True
        send_post_accepted_email(post)
        post.is_reviewed = True
    else:
        post.rejected_reason = credentials["rejected_reason"]
        send_post_rejected_email(post)
        db.session.delete(post)
        is_accepted = False
    
    db.session.commit()   
    
    return {"status" : "success", "code" : 200, "message" : "Post has been Accepted" if is_accepted else "Post has been rejected", "is_accepted" : is_accepted}, 200
        
@posts.route("/comments/<int:post_id>", methods=["POST"])
@token_required
def add_comment(user, post_id):
    data = request.get_json()
    data = validate_add_comment_route(data, post_id)
    if data["status"] == "failure" :
        return data, data["code"]
    
    comment = data["credentials"]
    comment = Comment(**comment, user_id = user.id, post_id = post_id)
    
    db.session.add(comment)
    db.session.commit()
    comment = CommentResponse(exclude=["author"]).dump(comment)
    
    return {"status" : "success", "code" : 201, "comment" : comment, "message" : "Comment Added Succesfully."}, 201
           
@posts.route("/comments/<int:post_id>", methods=["GET"])
def get_comment(post_id):
    post = Post.query.get(post_id)
    if not post :
        return {"status": "failure" , "code" : 404, "message" : "The Post doesnot exist."}
    
    comments = CommentResponse().dump(post.comments, many=True)
    return {"status" : "success", "code" : 200, "comments" : comments}, 200

@posts.route("/comments/<int:comment_id>", methods=["PUT"])
@token_required
def update_comment(user, comment_id):
    data = request.get_json()
    data = validate_update_comment_route(data, comment_id, user)
    if data["status"] == "failure" :
        return data, data["code"]
    
    credentials = data["credentials"]
    comment = data["comment"]
    
    comment.message = credentials["message"]
    db.session.commit()
    
    comment = CommentResponse(exclude=["author"]).dump(comment)
    data.pop("credentials")
    return {**data, "comment" : comment}, data["code"], data["code"]
    

@posts.route("/comments/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(user, comment_id):
    data = validate_delete_comment_route(comment_id, user)
    if data["status"] == "failure" :
        return data, data["code"]
    
    comment = data["credentials"]
    print(comment.message)
    db.session.delete(comment)
    db.session.commit()
    
    return {"status" : "success", "message" : "Comment has been deleted.", "code" : 200}, 200
    
        
    
    

    
        
        
        