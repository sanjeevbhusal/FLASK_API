from flask import request
from sqlalchemy import or_
from flask_restful import Resource

from api import db
from api.models import Post, Vote, Comment 
from api.schema import  PostResponse, PostUpdate, CommentResponse
from api.utils import token_required, admin_token_required, send_post_accepted_email, send_post_rejected_email, validate_create_new_post_route, validate_update_single_post_route,validate_delete_single_post_route, validate_update_post_status_route, validate_add_comment_route, validate_update_comment_route, validate_delete_comment_route


class CreatePost(Resource) :
    @token_required
    def post(user, self) :
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

class PostsList(Resource) :
    def get(self) :
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
        
        return {"status" : "success", "code" : 200, "posts" : posts}, 200
    
class PostsById(Resource) :
    def get(self, id) :
        post = Post.query.get(id)
        if not post :
            return {"message" : "The Post doesnot exist"}, 404
        post = PostResponse().dump(post)
            
        return {"status" : "success", "code" : 200, "post" : post}, 200
    
    @token_required
    def put(user, self, id) :
        data = request.get_json()
        data = validate_update_single_post_route(data, id, user)
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
    
    @token_required
    def delete(user, self, id) :
        data = validate_delete_single_post_route(user, id)
        if data["status"] == "failure" :
            return data, data["code"]
        
        post = data["post"]
        db.session.delete(post)
        db.session.commit()
        
        data.pop("post")
        return data, data["code"]
    
class CreateVote(Resource) :
    @token_required
    def post(user, self, id) :
        post = Post.query.get(id)
        if not post :
            return {"status": "failure", "code": 404, "message" : "The Post doesnot exist."}, 404
        
        post_votes = len((Vote.query.filter_by(post_id = id)).all())
        
        #if user has already voted on this post, remove the vote.
        vote = Vote.query.filter_by(post_id = id, user_id = user.id).first()
        if vote :
            db.session.delete(vote)
            db.session.commit()
            return {"status" : "success", "code" : 200, "votes": post_votes - 1, "message" : "Your Like has been removed succesfully.", "has_voted" : False}
        else:
            new_vote = Vote(user_id = user.id, post_id = id) 
            db.session.add(new_vote)
            db.session.commit()
            return {"status" : "success", "code" : 200, "votes": post_votes + 1, "message" : "Your Like has been removed succesfully.", "has_voted" : True}
        
class UnverifiedPost(Resource) :
    @admin_token_required
    def get(user, self) :
        posts = Post.query.filter_by(is_reviewed= False)
        posts = PostResponse(exclude=["comments"]).dump(posts, many=True)
        return {"status" : "success", "code" : 200, "posts" : posts, "message": "Here are all the posts to review"}, 200
    
    @admin_token_required
    def put(user, self, id):
        data = request.get_json()
        data = validate_update_post_status_route(data, id)
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
    
class Comments(Resource) :
    def get(self, id) :
        post = Post.query.get(id)
        if not post :
            return {"status": "failure" , "code" : 404, "message" : "The Post doesnot exist."}
        
        comments = CommentResponse().dump(post.comments, many=True)
        return {"status" : "success", "code" : 200, "comments" : comments}, 200
    
    @token_required
    def post(user, self, id):
        data = request.get_json()
        data = validate_add_comment_route(data, id)
        if data["status"] == "failure" :
            return data, data["code"]
        
        comment = data["credentials"]
        comment = Comment(**comment, user_id = user.id, post_id = id)
        
        db.session.add(comment)
        db.session.commit()
        comment = CommentResponse(exclude=["author"]).dump(comment)
        
        return {"status" : "success", "code" : 201, "comment" : comment, "message" : "Comment Added Succesfully."}, 201
    
    
    @token_required
    def put(user, self, id) :
        data = request.get_json()
        data = validate_update_comment_route(data, id, user)
        if data["status"] == "failure" :
            return data, data["code"]
        
        credentials = data["credentials"]
        comment = data["comment"]
        
        comment.message = credentials["message"]
        db.session.commit()
        
        comment = CommentResponse(exclude=["author"]).dump(comment)
        data.pop("credentials")
        return {**data, "comment" : comment}, data["code"]
    
    @token_required
    def delete(user, self, id) :
        data = validate_delete_comment_route(id, user)
        if data["status"] == "failure" :
            return data, data["code"]
        
        comment = data["credentials"]
        print(comment.message)
        db.session.delete(comment)
        db.session.commit()
        
        return {"status" : "success", "message" : "Comment has been deleted.", "code" : 200}, 200
        

        
        
        