from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.form import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import secrets, os
from PIL import Image


# Enter dummy data
# posts = [
#     {
#         'author': 'lebogang',
#         'title': 'Post',
#         'content': 'Hey using flask is actually quite easy, and fun',
#         'date_posted': 'Jan 15, 1999'
#     },
#     {
#         'author': 'neophite',
#         'title': 'post',
#         'content': 'The steps, take them one at a time.',
#         'date_posted': 'Feb 18, 1029'
#     }
# ]

# Display the home page
@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template('home.html', posts=posts) # This is used to render the html so it can be displayed on the browser.


# Render the about page.
@app.route("/about")
def about():
    return render_template('about.html', title='About')


def save_picture(form_pic):
    rand_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_pic.filename)
    pic_fn =  rand_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/profile_pics', pic_fn)

    output_size = (110, 110)
    i = Image.open(form_pic)
    i.thumbnail(output_size)

    i.save(pic_path)

    return pic_fn



@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
           pic_file = save_picture(form.picture.data)
           current_user.image_file = pic_file
           
        current_user.username = form.username.data
        current_user.email  = form.email.data
        db.session.commit()
        flash('You account has been updated', 'success')
        return redirect( url_for('account') )
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("account.html", title='account', image_file=image_file, form=form)


# route for register
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Uses the Flask-login extension function that knows if a use has logged
    # in yet.
    if current_user.is_authenticated:
        return redirect( url_for('home') )
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password of the user.
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Create the user object with the given input from the form.
        user = User(username=form.username.data, email=form.email.data, password=hash_pw)
        # Add the user to the database.
        db.session.add(user)
        db.session.commit()
        # Display the a flash message
        flash(f'Account created for {form.username.data}, Try logging in!', 'success')
        # Redirect the user to the login.
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# route for login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect( url_for('home') )
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect( url_for('home') )
        else:
            flash('Login unsuccessful. Check the email and password', 'danger')

    return render_template('login.html', title='login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect( url_for('home') )

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("The post has been created.", 'success')
        return redirect( url_for('home') )
    return render_template('create_post.html', title='New Post', legend="New post" ,form=form)


@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("The post was updated", 'success')
        return redirect( url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title="Update post",legend='Update post', form=form)


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post was deleted!", 'info')
    return redirect( url_for('home') )


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    return render_template('user_posts.html', posts=posts, user=user) # This is used to render the html so it can be displayed on the browser.

