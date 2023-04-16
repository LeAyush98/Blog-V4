from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship 
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import datetime

db = SQLAlchemy()

class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    
    def __init__(self, email:str, name:str, password:str) -> None:
        self.email = email
        self.name = name
        self.password = password

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    users = relationship("Users", backref=db.backref("posts"))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) # here "users" show the table name

    def __init__(self, title, subtitle, body, author, img_url, user_id) -> None:
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.author = author
        self.img_url = img_url
        self.user_id = user_id
        date = datetime.datetime.now()
        self.date = date.strftime("%B %d, %Y")

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(250), nullable=False)
    users = relationship("Users", backref=db.backref("comment"))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    posts = relationship("BlogPost", backref=db.backref("comment"))
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id')) # here "blog_posts" show the table name

    def __init__(self, comment:str, user_id:int, post_id:int) -> None:
        self.comment = comment
        self.user_id = user_id
        self.post_id = post_id
