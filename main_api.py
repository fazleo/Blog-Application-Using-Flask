from app import app,db
from werkzeug.security import generate_password_hash


from flask_restful import Api
from flask_restful import Resource
from flask_restful import fields, marshal_with,abort
from flask_restful import reqparse


from exception import NotfoundError, Succesmsg


from models import *


from flask_cors import CORS




api = Api(app)
CORS(app, supports_credentials=True)



user_fields={
    "id" : fields.Integer,
    "username" : fields.String,
    "email" : fields.String,
    #"profile_url" : fields.String
}

user_parser = reqparse.RequestParser()
user_parser.add_argument('id')
user_parser.add_argument('username')
user_parser.add_argument('email')
#user_parser.add_argument('profile_url')
user_parser.add_argument('password')

class UserApi(Resource):
    @marshal_with(user_fields)
    def get(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if user:
            return user,200
        else:
            raise NotfoundError(status_code = 404, msg="User not found")
        
    @marshal_with(user_fields)
    def put(self,user_id):
        args = user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)
        password = args.get("password", None)
        
        user = User.query.filter_by(id = user_id).first()
        if user:
            if username is None:
                raise NotfoundError(status_code = 400, msg="username not entered")
            if email is None:
                raise NotfoundError(status_code = 400, msg="email not entered")

            if len(email)<4 or '@' not in email:
                raise NotfoundError(status_code = 400, msg="invalid email")
            if len(password)<6:
                raise NotfoundError(status_code = 400, msg="invalid password")



            user.username = username
            user.email = email
            user.password = generate_password_hash(password, method = 'sha256')
            
            db.session.add(user)
            db.session.commit()
            return user, 200

        else:
            raise NotfoundError(status_code = 404, msg="User not found")
        

    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        username = args.get("username", None)
        email = args.get("email", None)
        password = args.get("password", None)
        if username is None:
            raise NotfoundError(status_code = 400, msg="username not entered")
        if email is None:
            raise NotfoundError(status_code = 400, msg="email not entered")

        if len(email)<4 or '@' not in email:
            raise NotfoundError(status_code = 400, msg="invalid email")
        if len(password)<6:
            raise NotfoundError(status_code = 400, msg="password is too short")
        
        user_email = User.query.filter_by(email = email).first()
        user_name = User.query.filter_by(username = username).first()

        if user_email:
            raise NotfoundError(status_code = 404, msg="Email already exist!")
        if user_name:
            raise NotfoundError(status_code = 404, msg="Usename already exist!")
            
        new_user = User(username = username, email = email, password = generate_password_hash(password, method = 'sha256'))
        
        db.session.add(new_user)
        db.session.commit()
        return new_user, 200



    @marshal_with(user_fields)
    def delete(self, user_id):
        user = User.query.filter_by(id = user_id).first()

        if not user:
            raise NotfoundError(status_code = 404, msg="User not found")
        
        likes = user.likes
        comments = user.comments
        posts = user.posts

        if posts:
            raise NotfoundError(status_code=400, msg="Cannot delete user, User has Posts")

        if likes:
            for like in likes:
                db.session.delete(like)

        if comments:
            for comm in comments:
                db.session.delete(comm)

        db.session.delete(user)
        db.session.commit()
        raise Succesmsg(status_code=200, msg="succesfully deleted")

        
        
        
            




api.add_resource(UserApi, "/api/user", "/api/user/<int:user_id>")






post_fields={
    "id" : fields.Integer,
    "title" : fields.String,
    "caption" : fields.String,
    "author" : fields.Integer,
    "timestamp" : fields.DateTime
}

post_parser = reqparse.RequestParser()
post_parser.add_argument('title')
post_parser.add_argument('caption')
post_parser.add_argument('author')



class PostApi(Resource):

    @marshal_with(post_fields)
    def get(self, post_id):
        post = Post.query.filter_by(id = post_id).first()
        if post:
            return post,200
        else:
            raise NotfoundError(status_code = 404, msg="Post not found")

    @marshal_with(post_fields)
    def put(self,post_id):
        args = post_parser.parse_args()
        title = args.get("title", None)
        caption = args.get("caption", None)
        author = args.get("author", None)
        
        
        post = Post.query.filter_by(id = post_id).first()
        if post:
            if title is None:
                raise NotfoundError(status_code = 404, msg="title not entered")
            if caption is None:
                raise NotfoundError(status_code = 404, msg="capition not entered")
            if author is None:
                raise NotfoundError(status_code = 404, msg="author not entered")
            

            if len(title)<3:
                raise NotfoundError(status_code = 404, msg="title is too short")

            author_exists = User.query.filter_by(id = author).first()
            if not author_exists:
                raise NotfoundError(status_code = 404, msg="Author not found")

            post.title = title
            post.caption = caption
            post.author = author
            
            db.session.add(post)
            db.session.commit()
            return post, 200

        else:
            raise NotfoundError(status_code = 404, msg="Post not found")
    

    @marshal_with(post_fields)
    def post(self):
        args = post_parser.parse_args()
        title = args.get("title", None)
        caption = args.get("caption", None)
        author = args.get("author", None)
        if author is None:
            raise NotfoundError(status_code = 404, msg="author not entered")
        if title is None:
            raise NotfoundError(status_code = 404, msg="title not entered")
        if caption is None:
            raise NotfoundError(status_code = 404, msg="capition not entered")
        
        if len(title)<3:
                raise NotfoundError(status_code = 404, msg="title is too short")

        author_exists = User.query.filter_by(id = author).first()

        if author_exists:
            new_post = Post(title = title, caption=caption, author = author)
            db.session.add(new_post)
            db.session.commit()
            return new_post, 200
        else:
            raise NotfoundError(status_code = 404, msg="Author not found")



    def delete(self, post_id):
        post = Post.query.filter_by(id = post_id).first()
        if not post:
            raise NotfoundError(status_code = 404, msg="Post not found")
        likes = post.likes
        comments = post.comments
        
        if likes:
            for like in likes:
                db.session.delete(like)

        if comments:
            for comm in comments:
                db.session.delete(comm) 

        db.session.delete(post)
        db.session.commit()
        raise Succesmsg(status_code=200, msg="succesfully deleted")
            

        
        




api.add_resource(PostApi, "/api/post", "/api/post/<int:post_id>")




class FeedApi(Resource):
    @marshal_with(post_fields)
    def get(self, user_id):
        user = User.query.filter_by(id = user_id).first()
        if user:
            following = user.following
            if following:
                user_posts = []
                feeds_f = False
                for follower in following:
                #incorperate user, post into a single list
                    posts = follower.posts
                    if posts:
                        feeds_f = True
                    user_posts.append(posts)

                #single list is appended to big list calle user_post
                if not feeds_f:
                    raise NotfoundError(status_code = 400, msg="No feeds")
                return user_posts,200
                
                
            else:
                raise NotfoundError(status_code = 400, msg="No followings")
        else:
            raise NotfoundError(status_code = 404, msg="User not found")
            
        



api.add_resource(FeedApi, "/api/feed", "/api/feed/<int:user_id>")
            
            

            