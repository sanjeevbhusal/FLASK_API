from flask import Blueprint, request, url_for
from marshmallow import ValidationError
from marshmallow import ValidationError


from api import db
from api.models import Post, Vote, Comment
from api.schema import PostRegister, PostResponse, PostUpdate, VoteInput, PostReview, CommentRegister, CommentResponse, CommentUpdate
from api.utils import token_required, admin_token_required, get_post_by_id,send_post_accepted_email, send_post_rejected_email, save_file, allowed_image
from sqlalchemy import or_, desc


posts = Blueprint("posts", __name__)

@posts.route("/posts/new", methods=["POST"])
@token_required
def create_new_post(user):

    data = request.form
    image = request.files.get("image")
    print(image)

    try:
        # import pdb; pdb.set_trace()
        data = PostRegister().load(data)
        data["user_id"] = user.id
        data["file_name"] = None
        
        if image:
            if not allowed_image(image):
                return {"message":"Your extension was not supported. Only PNG, JPEG, JPG extensions are supported. "}
            filename = save_file(image)
            data["file_name"] = filename
        
        new_post = Post(**data)
        
        db.session.add(new_post)
        db.session.commit()     
    except ValidationError as err:
        return {"message" : err.messages}, 400
    except Exception as err:
        return {"message" : "The category you choosed isn't available."}, 400
    
    post = PostResponse(exclude=["comments"]).dump(new_post)
        
    return {"message" : 'Post has been Created', "post" : post}, 201
    
@posts.route("/posts", methods=["GET"])
def get_all_posts():
    
    page = request.args.get("page", 1, type=int) 
    per_page = request.args.get("perpage", 10, type=int)
    search =  request.args.get("search", "") 
    category =  request.args.get("category", "") 
    
    all_filters = [or_(Post.title.ilike(f'%{search}%'), Post.content.ilike(f'%{search}%'))]
    if category :
        all_filters.append(Post.category == category)
    
    # posts = Post.query.filter(*all_filters).paginate(page= page, per_page= per_page)
    posts = Post.query.filter(*all_filters).order_by(Post.created_at.desc())

    posts = PostResponse().dump(posts, many=True)
    
    for post in posts :
        if post["file_name"]:
            post["file_name"] = url_for("static", filename="blog_pictures/" + post["file_name"], _external=True)
         
    return {"posts" : posts}, 200

@posts.route("/posts/<int:post_id>", methods=["GET"])
def get_single_post(post_id):
    
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
    
    post = PostResponse().dump(post)
    
    if post["file_name"] :
        post["file_name"] = url_for("static", filename="blog_pictures/" + post["file_name"], _external=True)
          
    return {"post" : post}, 200

@posts.route("/posts/<int:post_id>", methods=["PUT"])
@token_required
def update_single_post(user, post_id):
     
    try:
        data= request.get_json()
        data = PostUpdate().load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 201
    
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    if user.is_admin == "False" and not post.author.id == user.id:
        return {"message" : "You are not authorized to perform this operation."}, 403
       
    post.title = data["title"]
    post.content = data["content"]
    post.category = data["category"]
    
    db.session.commit()
    
    updated_post = PostUpdate().dump(post)

    return {"message" : updated_post}, 200

@posts.route("/posts/<int:post_id>", methods=["DELETE"])
@token_required
def delete_single_post(user, post_id):
    
    post = get_post_by_id(post_id)
    
    if not post :
         return {"message" : "The Post doesnot exist"}, 404
     
    if user.is_admin == "False" and not post.author.id == user.id:
        return {"message" : "You are not authorized to perform this operation."}, 403
    
    db.session.delete(post)
    db.session.commit()

    return {"message" : f'The post created by user with email {post.author.email} has been deleted Succesfully.'}, 200
    
@posts.route("/vote/<int:post_id>", methods=["POST"])
@token_required
def create_vote(user, post_id):
    
    post = Post.query.filter_by(id = post_id).first()
    
    if not post :
        return {"message": f"The Post with id of {post_id} doesnot exist."}, 404
    
    all_votes = len(Vote.query.all())
    
    #if user has already voted on this post, remove the vote.
    vote = Vote.query.filter_by(post_id = post_id, user_id = user.id).first()
    if vote :
        db.session.delete(vote)
        db.session.commit()
        
        return {"votes": all_votes - 1, "hasvoted" : False}
    else:
        new_vote = Vote(user_id = user.id, post_id = post_id) 
        db.session.add(new_vote)
        db.session.commit()
        
        return {"votes": all_votes + 1, "hasvoted" : True}
        
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
    
    try:
        data = PostReview().load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 401
    except Exception :
        return {"message" : "Rejecetd Reason is also required if The Post has been Rejeted"}, 401

    post = get_post_by_id(post_id)
    
    if not post :
        return {"message": f"The Post with an id of {post_id} doesnot Exist."}, 404
    
    if data.get("is_accepted"):
        post.is_accepted = True
        send_post_accepted_email(post)
    else:
        post.rejected_reason = data["rejected_reason"]
        send_post_rejected_email(post)
    
    post.is_reviewed = True
    
    db.session.commit()   
    
    return {"message" : "Post has been Updated"}, 200
        
@posts.route("/comments/<int:post_id>", methods=["POST"])
@token_required
def add_comment(user, post_id):
    data = request.get_json()
    
    try:
        comment = CommentRegister().load(data)
    except ValidationError as err :
        return {"message": err.messages}, 400
    
    post = Post.query.get(post_id)
    
    if not post :
        return {"message": f"The Post with an id of {post_id} doesnot exist."}, 400
    
    comment = Comment(**comment, user_id = user.id, post_id = post_id)
    
    db.session.add(comment)
    db.session.commit()
    
    comment = CommentResponse(exclude=["author"]).dump(comment)
    
    return {"comment" : comment}, 201
    
           
@posts.route("/comments/<int:post_id>", methods=["GET"])
def get_comment(post_id):
    
    post = Post.query.get(post_id)
    
    if not post :
        return {"message": f"The Post with an id of {post_id} doesnot exist."}, 400
    
    comments = CommentResponse().dump(post.comments, many=True)
    
    return {"comments" : comments}, 200

@posts.route("/comments/<int:comment_id>", methods=["PUT"])
@token_required
def update_comment(user, comment_id):
    data = request.get_json()
    try:
        CommentUpdate().load(data)
    except ValidationError as err :
        return {"message" : err.messages}, 400
    
    comment = Comment.query.get(comment_id)
    
    if not comment :
        return {"message" : f"Comment with an id of {comment_id} doesnot exist"}, 404
    
    if user.is_admin == False and user.id != comment.author.id :
         return {"message" : "You can only update your own comment"}, 403
    
    comment.message = data["message"]
    db.session.commit()
    
    comment = CommentResponse(exclude=["author"]).dump(comment)
    
    return {"updated comment" : comment }, 200
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
    
    return {"message" : f"Comment with an id of {comment_id } has been Deleted Succesfully"}, 200
    
        
    
    

    
        
        
        