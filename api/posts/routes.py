from flask import request
from sqlalchemy import or_
from flask_restful import Resource
from api import db
from werkzeug.exceptions import BadRequest
from marshmallow import ValidationError

from api.models import Post, Vote, Comment 
from api.schema import  PostResponse, PostUpdate, CommentResponse, RejectedReasonNotPresent, CategoryMismatchException
from api.utils import authenticate, email_gateway, post_database, PostNotFoundException, UnautorizedAccessException, PostAlreadyVerifiedException, CommentNotFoundException, validate_routes

class CreatePost(Resource) :
    @authenticate.token_required
    def post(user, self) :
        schema = PostResponse(exclude=["comments"])
        try:
            request_data = request.form
            title, content, category, image = validate_routes.create_post(request_data).values()
            post = post_database.create_post(user.id, title, content, category, image)
            if user.is_admin == True :
                post.is_reviewed = True
                post.is_accepted = True
            post_database.save(post)
        except BadRequest as err :
            return {"status" : "failure", "message" : err.description}, 400
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except CategoryMismatchException as err :
            return {"status" : "failure", "message" : "Category Unavailable"}, 400

        post = schema.dump(post)
        return {"status": "success", "post_details": post, "message": "Post has been Created"}, 201

class PostsList(Resource) :
    def get(self) :
        schema = PostResponse()
        page = request.args.get("page", 1, type=int) 
        per_page = request.args.get("perpage", 10, type=int)
        search =  request.args.get("search", "") 
        category =  request.args.get("category", "") 
        
        all_filters = [or_(Post.title.ilike(f'%{search}%'), Post.content.ilike(f'%{search}%')),Post.is_accepted == True]
        if category :
            all_filters.append(Post.category == category)
        
        # posts = Post.query.filter(*all_filters).paginate(page= page, per_page= per_page)
        posts = Post.query.filter(*all_filters).order_by(Post.created_at.desc())
        posts = schema.dump(posts, many=True)
        
        return {"status" : "success", "posts" : posts}, 200
   
class PostsById(Resource) :
    def get(self, post_id) :
        schema = PostResponse()
        post = Post.query.get(post_id)
        if not post :
            return {"status" : "failure", "message" : "The Post doesnot exist."}, 404
        post = schema.dump(post)
        return {"status" : "success", "post" : post}, 200
    
    @authenticate.token_required
    def put(user, self, post_id) :
        schema = PostUpdate()
        try:
            request_data = request.get_json()
            post_data, post = validate_routes.update_post(request_data, post_id, user).values()
            post_database.update_post(post, post_data["title"], post_data["content"], post_data["category"])
            return {"status" : "success", "message" : "Post Updated Succesfully", "post" : schema.dump(post)}, 200
        except BadRequest as err :
            return {"status" : "failure", "message" : err.description}, 400
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except PostNotFoundException as err :
            return {"status" : "failure" , "error" : err.args[0]}, 404
        except UnautorizedAccessException as err :
            return {"status" : "failure", "error" : err.args[0]}, 403
        
    @authenticate.token_required
    def delete(user, self, post_id) :
        try:
            post = validate_routes.delete_post(user, post_id)
            post_database.delete_post(post)
            return {"status" : "success", "message" : "The post has been deleted"}, 200
        except PostNotFoundException as err :
            return {"status" : "failure", "message" : err.args[0]}, 404
        except UnautorizedAccessException as err :
            return {"status" : "failure" , "message" : err.args[0]}, 403

class Votes(Resource) :
    @authenticate.token_required
    def post(user, self, post_id) :
        post = post_database.get_by_id(post_id)
        if not post :
            return {"status": "failure", "error" : "The Post doesnot exist."}, 404
        post_votes = len((Vote.query.filter_by(post_id = post_id)).all())
        #if user has already voted on this post, remove the vote.
        vote = Vote.query.filter_by(post_id = post_id, user_id = user.id).first()
        if vote :
            db.session.delete(vote)
            db.session.commit()
            return {"status" : "success", "votes": post_votes - 1, "message" : "Your Like has been removed succesfully.", "has_voted" : False}, 200
        else:
            new_vote = Vote(user_id = user.id, post_id = post_id) 
            db.session.add(new_vote)
            db.session.commit()
            return {"status" : "success", "votes": post_votes + 1, "message" : "Your Like has been added succesfully.", "has_voted" : True}, 200
        
class UnverifiedPost(Resource) :
    @authenticate.admin_token_required
    def get(user, self) :
        schema = PostResponse(exclude=["comments"])
        posts = Post.query.filter_by(is_reviewed= False)
        posts = schema.dump(posts, many=True)
        return {"status" : "success", "posts" : posts}, 200
    
    @authenticate.admin_token_required
    def put(user, self, post_id):
        try:
            request_data = request.get_json()
            input_data, post = validate_routes.update_post_status(request_data, post_id).values()
            if input_data["is_accepted"] :
                post_database.verify_post(post)
                email_gateway.send_post_accepted_email(post)
            else :
                post_database.delete_post(post)
                email_gateway.send_post_rejected_email(post)    
            return {"status" : "success", "message" : "Your post is accepted" if input_data["is_accepted"] else "Your post is rejected"}, 400
                
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except RejectedReasonNotPresent as err :
            return {"status" : "failure", "error" : err.args[0]}, 400
        except PostNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404
        except PostAlreadyVerifiedException as err :
            return {"status" : 'failure', "error" : err.args[0]}, 400 
    
class Comments(Resource) :
    def get(self, post_id) :
        schema = CommentResponse()
        post = post_database.get_by_id(post_id)
        if not post :
            return {"status": "failure" ,"message" : "The Post doesnot exist."}, 404
        comments = schema.dump(post.comments, many=True)
        return {"status" : "success", "comments" : comments}, 200
    
    @authenticate.token_required
    def post(user, self, post_id):
        schema = CommentResponse()
        try:
            request_data = request.get_json()
            comment_data = validate_routes.add_comment(request_data, post_id)
            comment = Comment(**comment_data, user_id = user.id, post_id = post_id)
            db.session.add(comment)
            db.session.commit()
            return {"status" : "success", "comment" : schema.dump(comment)}, 200
        except ValidationError as err :
            return {"status" : "failure", "error" : err.messages}, 400
        except PostNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404
    
    @authenticate.token_required
    def put(user, self, post_id) :
        try:
            request_data = request.get_json()
            comment_data, comment = validate_routes.update_comment(request_data, post_id, user)
            comment.message = comment_data["message"]
            db.session.commit()
            return {"status" : "success", "message" : "Comment Updated Succesfully", "comment" : comment.message}, 200
        except ValidationError as err :
            return {"status" : "failure", "error" : err.message}, 400
        except CommentNotFoundException as err :
            return {"status": "failure", "error": err.args[0]}, 404
        except UnautorizedAccessException as err :
            return {"status" : "failure", "error" : err.args[0]}, 403
    
    @authenticate.token_required
    def delete(user, self, post_id) :
        try:
            comment = validate_routes.delete_comment(post_id, user)
            db.session.delete(comment)
            db.session.commit()
            return {"status" : "success", "message" : "Comment deleted succesfully."}, 200
        except UnautorizedAccessException as err :
            return {"status" : "failure", "error" : err.args[0]}, 400
        except CommentNotFoundException as err :
            return {"status" : "failure", "error" : err.args[0]}, 404

        
        
        