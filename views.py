from app import app, db, upload_folder, del_img
from flask import render_template,request,flash, redirect,url_for
from models import User,Post,Like,Comment
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from werkzeug.utils import secure_filename
import uuid as uuid
import os




@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully!')
                user_id = current_user.id
                return redirect(url_for('profile'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email not exists', category='error') 

        print('username: {},password: {} '.format(email,password))
    return render_template('login.html')




@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        email_exists = User.query.filter_by(email = email).first()
        username_exists = User.query.filter_by(username = username).first()
        
        if email_exists:
            flash('Email already used.', category='error')
        elif username_exists:
            flash('Username already used.', category='error')
        
        elif len(email)<4:
            flash('Invalid Email', category='error')

        elif password1 != password2:
            flash('Password do not match!', category='error')
        
        elif len(username)<2:
            flash('Username is too short, try another!', category='error')
        
        elif len(password1)<6:
            flash('Password is too short, try another!', category='error')
        
        else:
            new_user = User(email=email, username = username, password=generate_password_hash(password1, method = 'sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created')
            user_id = current_user.id
            return redirect(url_for('profile'))
        
        
    return render_template('signup.html')




@app.route('/logout')
@login_required
def logout():
    try:
       logout_user()
       flash('log out succesfully')
    except:
        flash('log out error', category='error')

    return redirect(url_for('index'))





#profile routing
@app.route('/blog')
@login_required
def profile():
    user = current_user
    followers = user.followers
    following = user.following
    posts = user.posts
    return render_template('profile.html',user = current_user, posts = posts)



@app.route('/blog/create_post', methods = ['POST','GET'])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        desc = request.form.get('desc')
        img = request.files['img']

        if len(title)<1:
            flash('title is too short',category='error') 
        else:

        #store img in the form of string
        #name of file


            img_name = secure_filename(img.filename)

            #generate random name
            img_uname = str(uuid.uuid1()) + "_" + img_name
            #changin img name to new name

            #save the image img
            img.save(os.path.join(app.config['UPLOAD_FOLDER'],img_uname))

            
            new_post = Post(title=title, caption=desc, img=img_uname, author=current_user.id)
            
            try:
                db.session.add(new_post)
                db.session.commit()
                flash('Post created')
            except:
                db.session.rollback()
                flash('Post creation error', category='error')
            return redirect(url_for('profile'))
        
    
    return render_template('create_post.html')


@app.route('/blog/users',methods=['POST','GET'])
@login_required
def users():
    if request.method == "POST":
        username = request.form.get('search_user')
        username = '%'+username+'%'


        userlist = User.query.filter(User.username.like(username)).all()
        if not userlist or username == '%%':
            flash('Users not found', category='error')
            return redirect(url_for('users'))

        followings = current_user.following
        print(followings)
        return render_template('user_search.html',userlist=userlist,followings=followings)
    users =''
    return render_template('user_search.html', users = users)


@app.route('/blog/post',methods=['POST','GET'])
@login_required
def posts():
    posts = current_user.posts

    return render_template('posts.html',posts=posts)




@app.route('/blog/follow/<int:user_id>',methods=['POST','GET'])
@login_required
def follow(user_id):
    user = User.query.get(user_id)
    current_user.following.append(user)
    db.session.commit()
    flash('followed {} succesfull'.format(user.username))
    return redirect(url_for('profile'))




@app.route('/blog/unfollow/<int:user_id>',methods=['POST','GET'])
@login_required
def unfollow(user_id):
    user = User.query.get(user_id)
    current_user.following.remove(user)
    db.session.commit()
    flash('unfollowed {} succesfully'.format(user.username))
    return redirect(url_for('profile'))


@app.route('/blog/followers',methods=['POST','GET'])
@login_required
def followers():
    following = current_user.following
    followers = current_user.followers
    return render_template('followers.html', followers=followers, following = following)



@app.route('/blog/following',methods=['POST','GET'])
@login_required
def following():
    following = current_user.following
    
    return render_template('following.html',followings = following)




@app.route('/blog/edit_post/<int:post_id>',methods=['POST','GET'])
@login_required
def edit_post(post_id):
    post = Post.query.filter_by(id = post_id).first()
    if request.method == "POST":
        title = request.form.get('title')
        desc = request.form.get('desc')
        img = request.files['pic']

        


        if not title:
            flash('title cannot be empty!',category='error')

        else:
            if img:
                #delete old image
                if post.img:
                    del_img(post.img)

                #getting name 
                img_name = secure_filename(img.filename)

                #generate random name
                img_uname = str(uuid.uuid1()) + "_" + img_name

                #save the image img
                img.save(os.path.join(app.config['UPLOAD_FOLDER'],img_uname))

            try:
                post.title = title
                post.caption = desc
                if img:
                    post.img = img_uname
                db.session.add(post)
                db.session.commit()
                flash('Post updated')

            except:
                db.session.rollback()
                flash('Post update error', category='error')

        return redirect('/blog/post')
        
    return render_template('edit_post.html',post = post)
        


@app.route('/blog/delete_post/<int:post_id>',methods=['POST','GET'])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id = post_id).first()
    #delete image
    if post.img:
        del_img(post.img)
    likes = Like.query.filter_by(post_id = post.id).all()
    comments = Comment.query.filter_by(post_id = post.id).all()
    try:
        for like in likes:
            db.session.delete(like)
        for comm in comments:
            db.session.delete(comm)
            
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted')
    except:
        db.session.rollback()
        flash('Post delete error', category='error')
    return redirect(url_for('posts'))



@app.route('/blog/feeds')
@login_required
def feeds():

    following = current_user.following
    followers = current_user.followers
    user_posts = []
    for user in following:
        #incorperate user, post into a single list
        
        posts = user.posts
        if posts:
            for post in posts:
                li = []
                li.append(user)
                li.append(post)

                user_posts.append(li) 
        #single list is appended to big list calle user_post
 

    user_posts.sort(key=lambda x: x[1].timestamp, reverse=True)

    return render_template("feeds.html", user_posts = user_posts )
    
    
@app.route('/blog/user/<int:user_id>')
@login_required
def user_post(user_id):
    user = User.query.get(user_id)
    following = user.following
    followers = user.followers
    posts = user.posts
    return render_template('user_feeds.html',posts=posts,user=user)


@app.route('/blog/user/<string:user_name>')
@login_required
def name_search(user_name):
    user = User.query.filter_by(username = user_name).first()
    following = user.following
    followers = user.followers
    posts = user.posts
    return render_template('user_feeds.html',posts=posts,user=user)





@app.route('/blog/like/<int:post_id>')
@login_required
def like(post_id):
    post = Post.query.filter_by(id = post_id).first()
    like = Like.query.filter_by(post_id = post_id, author = current_user.id).first()


    if not post:
        flash('post does not exist', category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        new_like = Like(author = current_user.id, post_id =post_id)
        db.session.add(new_like)
        db.session.commit()
    return redirect(url_for('profile'))


@app.route('/blog/create_comment/<int:post_id>', methods= ['POST','GET'])
@login_required
def create_comment(post_id):

    text = request.form.get('comment')

    
    if not text:
        flash('comment cannot be empty', category='error')
    else:
        post = Post.query.filter_by(id = post_id).first()
        
        if not post:
            flash('post does not exist', category='error')
        else:
            new_comment = Comment(comment = text, author = current_user.id, post_id =post_id)
            db.session.add(new_comment)
            db.session.commit()
            flash('comment added succesfully')
    return redirect(url_for('profile'))


@app.route('/blog/delete_comment/<int:comment_id>', methods= ['POST','GET'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id = comment_id).first()
    if not comment:
        flash('comment does not exist', category='error')
    else:            
        db.session.delete(comment)
        db.session.commit()
        flash('comment deleted succesfully')
    return redirect(url_for('profile'))


@app.route('/blog/user/edit_profile',methods=['POST','GET'])
@login_required
def update_user():
    user = current_user
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        p_img = request.files['pic']

        #checking username exists or not
        user_exists = User.query.filter_by(username = username).first()
        email_exists = User.query.filter_by(email = email).first()

        if user_exists and user_exists.id != current_user.id:
            flash('username exists', category='error')
        elif email_exists and email_exists.id != current_user.id:
            flash('email exists', category='error')

        elif not username:
            flash('usename cannot be empty!',category='error')

        elif len(email)<4:
            flash('Invalid Email', category='error')

        elif password1 != password2:
            flash('Password do not match!', category='error')
        
        elif len(username)<2:
            flash('Username is too short, try another!', category='error')
        
        elif len(password1)<6:
            flash('Password is too short, try another!', category='error')

        

        else:
            
            #delete old image

            user = current_user

            if p_img:
                if user.profile_img:
                    del_img(user.profile_img)

                #securing filename
                img_name = secure_filename(p_img.filename)
                
                #generate random name
                img_uname = str(uuid.uuid1()) + "_" + img_name

                #save the image img
                p_img.save(os.path.join(app.config['UPLOAD_FOLDER'],img_uname))
                user.profile_img = img_uname
                flash('profile image updated')

            
            user = current_user
            user.id = current_user.id
            user.username = username
            user.email = email
            user.password = generate_password_hash(password1, method = 'sha256')
            

            db.session.add(user)
            db.session.commit()
        return redirect(url_for('profile'))
               

    return render_template('edit_user.html', user=current_user)


@app.route('/blog/user/delete')
@login_required
def delete_user():
    user = current_user
    likes = user.likes
    comments = user.comments
    posts = user.posts
    try:
        for like in likes:
            db.session.delete(like)
        for comm in comments:
            db.session.delete(comm)
        for post in posts:
            db.session.delete(post)

        db.session.delete(user)
        db.session.commit()
        flash("Profile successfully deleted")
    except:
        flash("Profile deletion failed")
    return redirect('/')



