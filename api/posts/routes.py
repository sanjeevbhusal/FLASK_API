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
        unverified_user_input = request.form
        data = validate_create_new_post_route(unverified_user_input)
        
        status = data["status"]
        user_input = data.get("verified_user_input")
        
        if status == "failure" :
            return data, data["code"]
        
        user_input["user_id"] = user.id
        if user.is_admin == True :
            user_input["is_reviewed"] = True
            user_input["is_accepted"] = True 
            
        post = Post(**user_input)
        db.session.add(post)
        db.session.commit()     
        post = PostResponse(exclude=["comments"]).dump(post)
        
        return {"status": "success", "post_details": post, "code": 201, "message": "Post has been Created"}, 201


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
    def get(self, post_id) :
        post = Post.query.get(post_id)
        if not post :
            return {"status" : "failure", "code" : 404, "message" : "The Post doesnot exist."}, 404
        
        post = PostResponse().dump(post)

        return {"status" : "success", "code" : 200, "post" : post}, 200
    
    @token_required
    def put(user, self, post_id) :
        unverified_user_input = request.get_json()
        data = validate_update_single_post_route(unverified_user_input, post_id, user)
        
        status = data["status"]
        user_input = data.get("verified_user_input")
        post = data.get("post_object")
        
        if status == "failure":
            return data, data["code"]
        
        post.title = user_input["title"]
        post.content = user_input["content"]
        post.category = user_input["category"]
        db.session.commit()
        updated_post = PostUpdate().dump(post)
        
        return {"status" : "success", "code" : 200, "message" : "Updated Succesfully", "post" : updated_post}, 200
    
    @token_required
    def delete(user, self, post_id) :
        data = validate_delete_single_post_route(user, post_id)
        
        status = data["status"]
        post = data.get("post_object")
        
        if status == "failure" :
            return data, data["code"]
        
        db.session.delete(post)
        db.session.commit()
        
        return {"status" : "success", "message" : "The post has been deleted", "code" : 200}, 200
    
class Votes(Resource) :
    @token_required
    def post(user, self, post_id) :
        post = Post.query.get(post_id)
        if not post :
            return {"status": "failure", "code": 404, "message" : "The Post doesnot exist."}, 404
        post_votes = len((Vote.query.filter_by(post_id = post_id)).all())
        
        #if user has already voted on this post, remove the vote.
        vote = Vote.query.filter_by(post_id = post_id, user_id = user.id).first()
        if vote :
            db.session.delete(vote)
            db.session.commit()
            return {"status" : "success", "code" : 200, "votes": post_votes - 1, "message" : "Your Like has been removed succesfully.", "has_voted" : False}, 200
        else:
            new_vote = Vote(user_id = user.id, post_id = post_id) 
            db.session.add(new_vote)
            db.session.commit()
            return {"status" : "success", "code" : 200, "votes": post_votes + 1, "message" : "Your Like has been added succesfully.", "has_voted" : True}, 200
        
class UnverifiedPost(Resource) :
    @admin_token_required
    def get(user, self) :
        posts = Post.query.filter_by(is_reviewed= False)
        posts = PostResponse(exclude=["comments"]).dump(posts, many=True)
        return {"status" : "success", "code" : 200, "posts" : posts, "message": "Here are all the posts to review"}, 200
    
    @admin_token_required
    def put(user, self, post_id):
        unverified_user_input = request.get_json()
        data = validate_update_post_status_route(unverified_user_input, post_id)
        
        status = data["status"]
        verified_user_input = data.get("verified_user_input")
        post = data.get("post_object")
        
        if status == "failure" :
            return data, data["code"]
        
        is_accepted = False 
        if verified_user_input.get("is_accepted"):
            is_accepted = True
            post.is_reviewed = True
            post.is_accepted = True
            send_post_accepted_email(post)
        else:
            post.rejected_reason = verified_user_input["rejected_reason"]
            send_post_rejected_email(post)
            db.session.delete(post)

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
    def post(user, self, post_id):
        unvalidated_user_input = request.get_json()
        data = validate_add_comment_route(unvalidated_user_input, post_id)
        
        status = data["status"]
        comment = data.get("validated_user_input")
        
        if status == "failure" :
            return data, data["code"]
        
        comment = Comment(**comment, user_id = user.id, post_id = post_id)
        db.session.add(comment)
        db.session.commit()
        comment = CommentResponse().dump(comment)
        
        return {"status" : "success", "code" : 201, "comment" : comment, "message" : "Comment Added Succesfully."}, 201
    
    @token_required
    def put(user, self, post_id) :
        unvalidated_user_input = request.get_json()
        data = validate_update_comment_route(unvalidated_user_input, post_id, user)
        
        status = data["status"]
        validated_user_input = data.get("validated_user_input")
        comment = data.get("comment")
        
        if status == "failure" :
            return data, data["code"]
        
        comment.message = validated_user_input["message"]
        db.session.commit()
        comment = CommentResponse(exclude=["author", "created_at"]).dump(comment)
        
        return {"status" : "success", "updated_comment" : comment}, 200
    
    @token_required
    def delete(user, self, post_id) :
        data = validate_delete_comment_route(post_id, user)
        
        status = data["status"]
        comment = data.get("comment")
        
        if status == "failure" :
            return data, data["code"]
        
        db.session.delete(comment)
        db.session.commit()
        
        return {"status" : "success", "message" : "Comment has been deleted.", "code" : 200}, 200
        

        
        
        