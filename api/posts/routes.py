from flask import Blueprint, request, url_for, current_app
from marshmallow import ValidationError


from api import db
from api.models import Post, Vote, Comment
from api.schema import PostRegister, PostResponse, PostUpdate, VoteInput, PostReview, CommentRegister, CommentResponse, CommentUpdate, CategoryMismatchException
from api.utils import token_required, admin_token_required, get_post_by_id,send_post_accepted_email, send_post_rejected_email, save_file, allowed_image, verify_create_new_post, verify_update_single_post,verify_delete_single_post, verify_update_post_status, verify_add_comment, verify_update_comment, verify_delete_comment
from sqlalchemy import or_, desc


posts = Blueprint("posts", __name__)

@posts.route("/posts/new", methods=["POST"])
@token_required
def create_new_post(user):
    data = request.form
    data = verify_create_new_post(data)
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
    
    return {**data,  "post_details" : post}, data["code"]

    
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
    return {"posts" : posts}, 200

@posts.route("/posts/<int:post_id>", methods=["GET"])
def get_single_post(post_id):
    post = Post.query.get(post_id)
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
    post = PostResponse().dump(post)
    # if post["image"] :
    #     post["image"] = url_for("static", filename="blog_pictures/" + post["image"], _external=True)       
    return {"post" : post}, 200

@posts.route("/posts/<int:post_id>", methods=["PUT"])
@token_required
def update_single_post(user, post_id):
    data = request.get_json()
    data = verify_update_single_post(data, post_id, user)
    if data["has_error"] :
        return data["error"]
    
    post = data["post"]  
    post.title = data["title"]
    post.content = data["content"]
    post.category = data["category"]
    db.session.commit()
    updated_post = PostUpdate().dump(post)
    return {"message" : updated_post}, 200

@posts.route("/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_single_post(user, post_id):
    data = verify_delete_single_post(user, post_id)
    if data["has_error"] :
        return data["error"]
    
    post = data["post"]
    db.session.delete(post)
    db.session.commit()
    return {"message" : f'The post created by user with email {post.author.email} has been deleted Succesfully.'}, 200
    
@posts.route("/vote/<int:post_id>", methods=["POST"])
@token_required
def create_vote(user, post_id):
    post = Post.query.get(post_id)
    if not post :
        return {"error": {"code": 404, "message" : f"The Post with id of {post_id} doesnot exist."}}, 404
    
    all_votes = len((Vote.query.filter_by(post_id = post_id)).all())
    
    #if user has already voted on this post, remove the vote.
    vote = Vote.query.filter_by(post_id = post_id, user_id = user.id).first()
    if vote :
        db.session.delete(vote)
        db.session.commit()
        return {"message" : {"votes": all_votes - 1, "has_voted" : False}}
    else:
        new_vote = Vote(user_id = user.id, post_id = post_id) 
        db.session.add(new_vote)
        db.session.commit()
        return {"message" : {"votes": all_votes + 1, "has_voted" : True}}
        
@posts.route("/review_posts", methods=["GET"])
@admin_token_required
def review_all_posts(user):
    posts = Post.query.filter_by(is_reviewed= False)
    posts = PostResponse(exclude=["comments"]).dump(posts, many=True)
    return {"posts" : posts}, 200

@posts.route("/update_post_status/<int:post_id>", methods=["PUT"])
@admin_token_required
def update_post_status(user,post_id):
    data = request.get_json()
    data = verify_update_post_status(data, post_id)
    if data["has_error"] :
        return data["error"]
    
    post = data["post"]
    data = data["data"]
    if data.get("is_accepted"):
        post.is_accepted = True
        send_post_accepted_email(post)
        post.is_reviewed = True
    else:
        post.rejected_reason = data["rejected_reason"]
        send_post_rejected_email(post)
        db.session.delete(post)
    
    db.session.commit()   
    return {"message" : "Post has been Updated"}, 200
        
@posts.route("/comments/<int:post_id>", methods=["POST"])
@token_required
def add_comment(user, post_id):
    data = request.get_json()
    data = verify_add_comment(data, post_id)
    if data["has_error"] :
        return data["error"]
    
    comment = data["data"]
    comment = Comment(**comment, user_id = user.id, post_id = post_id)
    db.session.add(comment)
    db.session.commit()
    comment = CommentResponse(exclude=["author"]).dump(comment)
    return {"comment" : comment}, 201
           
@posts.route("/comments/<int:post_id>", methods=["GET"])
def get_comment(post_id):
    post = Post.query.get(post_id)
    if not post :
        return {"error": {"code" : 404, "message" : "The Post doesnot exist."}}
    
    comments = CommentResponse().dump(post.comments, many=True)
    return {"comments" : comments}, 200

@posts.route("/comments/<int:comment_id>", methods=["PUT"])
@token_required
def update_comment(user, comment_id):
    data = request.get_json()
    data = verify_update_comment(data, comment_id, user)
    if data["has_error"] :
        return data["error"]
    
    comment = data["comment"]
    data = data["data"]
    comment.message = data["message"]
    db.session.commit()
    comment = CommentResponse(exclude=["author"]).dump(comment)
    return {"updated comment" : comment }, 200
    

@posts.route("/comments/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(user, comment_id):
    data = verify_delete_comment(comment_id, user)
    if data["has_error"] :
        return data["error"]
    
    comment = data["data"]
    db.session.delete(comment)
    db.session.commit()
    return {"message" : f"Comment with an id of {comment_id } has been Deleted Succesfully"}, 200
    
        
    
    

    
        
        
        