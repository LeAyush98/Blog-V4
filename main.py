from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterUserForm, LoginUserForm, CommentForm, ContactForm, ckeditor
from models import db, BlogPost, Users, Comment
from dotenv import load_dotenv
import os
import smtplib

load_dotenv("./.env")

SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///blog.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
ckeditor.init_app(app)

def admin(function):
    def wrapper(*args, **kw):
        print("wrapper working")
        if current_user.id == 1:
            return function(*args, **kw)
        else: 
            print("else statement is running")
            return render_template("void.html")    
    wrapper.__name__ = function.__name__       # wrapper is using same endpoint as our functions, so to prevent error, change wrapper name to the function's 
    return wrapper

def get_author_name():
    id = current_user.id 
    user = Users.query.filter_by(id=id).first()
    return user.name

def get_names_list(comments_on_post)-> list:
    names = []
    for comment in comments_on_post:
        author = Users.query.filter_by(id = comment.user_id).first()
        names.append(author.name)
    return names

def send_mail(name, email, phone, message):
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    connection = smtplib.SMTP("smtp.gmail.com")
    connection.starttls()
    connection.login(user=EMAIL, password=PASSWORD)
    connection.sendmail(
        from_addr=email,
        to_addrs=EMAIL,
        msg=f"Subject:Hello I am {name}!\n\n{message}\n\nPlease reach me out at {phone}"
    )
    connection.close()

@app.route('/')
def get_all_posts(): 
    db.create_all()
    number_of_posts = db.session.query(BlogPost).count()
    # Users.__table__.drop(db.engine) #Drops a table
    posts = BlogPost.query.all()
    for post in posts:
        print(post.author)
    return render_template("index.html", all_posts=posts, current_user = current_user, number_of_posts = number_of_posts)


@app.route('/register', methods = ["GET", "POST"])
def register():
    
    form = RegisterUserForm()
    if request.method == "GET":
        return render_template("register.html", form = form)
    elif request.method == "POST":
        if form.password.data == form.confirm_password.data:
            hashed = generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=8)
            user = Users(email=form.email.data, password= hashed, name=form.name.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("Password does not match")
            return redirect(url_for("register"))


@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginUserForm()
    if request.method == "GET":
        return render_template("login.html", form = form)
    elif request.method == "POST":
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password ,form.password.data):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash(f"Password is incorrect")
                return redirect(url_for('login'))
        else:
            flash(f"E-mail {form.email.data} does not exist here, Please register first")
            return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods = ["GET", "POST"])
def show_post(post_id):
    comment_form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    comments_on_post = Comment.query.filter_by(post_id = post_id)
    comment_count = Comment.query.filter_by(post_id = post_id).count()
    author_list = get_names_list(comments_on_post)
    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(comment=comment_form.comment.data, user_id=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('show_post', post_id = post_id))
        else:
            flash("Please Login or Register first")
            return redirect(url_for('show_post', post_id = post_id))
        
    else:
        
        return render_template("post.html", post=requested_post, current_user = current_user, comment_form = comment_form, comments_on_post = comments_on_post, 
                               authors = author_list, comment_count = comment_count)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods = ["GET", "POST"])
def contact():
    contact = ContactForm()
    if request.method == "GET":
        return render_template("contact.html", form = contact)
    elif request.method == "POST":
        send_mail(contact.name.data, contact.email.data , contact.phone.data, contact.message.data)
        return redirect(url_for('get_all_posts'))


@app.route('/new-post', methods = ["GET", "POST"])
@login_required
def new():
    form = CreatePostForm()
    if request.method == "GET":
        return render_template("make-post.html", form = form, is_edit = False)
    
    elif request.method == "POST":
        author = get_author_name()
        post = BlogPost(title=form.title.data, author=author, subtitle=form.subtitle.data, img_url=form.img_url.data, body=form.body.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))


@app.route("/edit-post/<int:index>", methods = ["GET", "POST"])
@login_required
@admin
def edit_post(index):
    form = CreatePostForm()
    post = BlogPost.query.filter_by(id = index).first()
    if request.method == "GET":  
        if post:
            form.title.data = post.title
            form.subtitle.data = post.subtitle
            form.img_url.data = post.img_url
            form.body.data = post.body
            return render_template("make-post.html", form=form, is_edit = True)
        else: 
            return jsonify({"error": "Please enter a valid ID"})   
    elif request.method == "POST":
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for("get_all_posts"))


@app.route("/delete/<int:post_id>")
@login_required
@admin
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
