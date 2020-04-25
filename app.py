from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from forms import LoginForm, RegisterForm
#from flask.ext.login import login_user, login_required, logout_user

app = Flask(__name__)

#app.secret_key = "mySecretKey"

# config
import os
app.config.from_object(os.environ['APP_SETTINGS'])
#print(app.config)
# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@app.route('/')
@login_required
def home():
	return render_template("index.html")

@app.route('/welcome')
def welcome():
	return render_template("welcome.html")

@app.route('/register',  methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(
			name=form.username.data,
			email=form.email.data,
			password=form.password.data
			)
		#db.session.add(user)
		#db.session.commit()
		login_user(user)
		return redirect(url_for('home.home'))
	return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != 'admin' or request.form['password'] != 'admin':
			error = 'Invalid credentials. Please try again!'
		else:
			session['logged_in'] = True
			flash('You were just logged in')
			return redirect(url_for('home'))
	return render_template("login.html", error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were just logged out')
	return redirect(url_for('welcome'))


if __name__ == '__main__':
	#app.run(debug=True)
	app.run()