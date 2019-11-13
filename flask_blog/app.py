# Import the template.
from flask import Flask, render_template, url_for, flash, redirect
from form import RegistrationForm, LoginForm
app= Flask(__name__)

app.config['SECRET_KEY'] = '371ce8e3ade7cb21af3ebc9d42bd6b88a0d79890fc531362'
# Enter dummy data
posts = [
    {
        'author': 'lebogang',
        'title': 'Post',
        'content': 'Hey using flask is actually quite easy, and fun',
        'date_posted': 'Jan 15, 1999'
    },
    {
        'author': 'neophite',
        'title': 'post',
        'content': 'The steps, take them one at a time.',
        'date_posted': 'Feb 18, 1029'
    }
]

# Display the home page
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts) # This is used to render the html so it can be displayed on the browser.

# Render the about page.
@app.route("/about")
def about():
    return render_template('about.html', title='About')


# route for register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

# route for login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@dummy.com' and form.password.data == 'password':
            flash(f'You are successfully logged in!!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check the email and password', 'danger')

    return render_template('login.html', title='login', form=form)



if __name__ == '__main__':
    app.run(debug=True)
