from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField
from wtforms.validators import DataRequired, URL, EqualTo
from flask_ckeditor import CKEditorField, CKEditor

ckeditor = CKEditor()

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class RegisterUserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo(password, "Password does not match")])
    submit = SubmitField("Set Me Up")

class LoginUserForm(FlaskForm):
    email = EmailField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let's Get Started")

class CommentForm(FlaskForm):
    comment = CKEditorField("Comment", validators=[DataRequired()], render_kw={"width" : "200%"})
    submit = SubmitField("Post Comment")

class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("E-mail", validators=[DataRequired()])
    phone = IntegerField("Phone", validators=[DataRequired()])
    message = CKEditorField("Message", validators=[DataRequired()], render_kw={"width" : "200%"})
    submit = SubmitField("Hear Me Out")
