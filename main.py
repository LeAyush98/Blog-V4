from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterUserForm
from flask_gravatar import Gravatar
from models import db, BlogPost, Users
from dotenv import load_dotenv
import os

load_dotenv("./.env")

SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
ckeditor = CKEditor(app)
Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def get_all_posts(): 
    db.session.commit()
    # Users.__table__.drop(db.engine) #Drops a table
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user = current_user)


@app.route('/register', methods = ["GET", "POST"])
def register():
    form = RegisterUserForm()
    if request.method == "GET":
        return render_template("register.html", form = form)
    elif request.method == "POST":
        print(form.password.data)
        print(form.confirm_password.data)
        if form.password.data == form.confirm_password.data:
            db.create_all()
            hashed = generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=8)
            user = Users(email=form.email.data, password= hashed, name=form.name.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("Password does not match")
            return redirect(url_for("register"))


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/new-post', methods = ["GET", "POST"])
@login_required
def new():
    form = CreatePostForm()
    if request.method == "GET":
        return render_template("make-post.html", form = form)
    
    elif request.method == "POST":
        post = BlogPost(title=form.title.data, author=form.author.data, subtitle=form.subtitle.data, img_url=form.img_url.data, body=form.body.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))


@app.route("/edit-post/<int:index>", methods = ["GET", "POST"])
def edit_post(index):
    form = CreatePostForm()
    post = BlogPost.query.filter_by(id = index).first()
    if request.method == "GET":  
        if post:
            form.title.data = post.title
            form.subtitle.data = post.subtitle
            form.img_url.data = post.img_url
            form.author.data = post.author
            form.body.data = post.body
            return render_template("make-post.html", form=form)
        else: 
            return jsonify({"error": "Please enter a valid ID"})   
    elif request.method == "POST":
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data
        post.author = form.author.data
        post.body = form.body.data
        db.session.commit()


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
