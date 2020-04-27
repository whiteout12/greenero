from flask import Flask, render_template, redirect, url_for, request, flash
from forms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user

#from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine, text
import psycopg2
#from flask.ext.login import login_user, login_required, logout_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
#db = create_engine("postgresql://localhost/postgres")
#db = create_engine("postgresql+psycopg2://localhost/postgres")
#app.secret_key = "mySecretKey"

# config
import os
app.config.from_object(os.environ['APP_SETTINGS'])
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)


#print(db)
#print(app.config)

login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
	from models import User
	return User.query.filter(User.id == int(user_id)).first()


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
	from models import User
	error = None
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(name=request.form['username']).first()
			if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
			#user.password == request.form['password']:
			#if request.form['username'] != 'admin' or request.form['password'] != 'admin':
				login_user(user)
				#session['logged_in'] = True
				flash('You were just logged in as: ' + str(user.name))
				return redirect(url_for('home'))

			else:
				error = 'Invalid credentials. Please try again!'
	return render_template("login.html", form=form, error=error)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You were just logged out')
	return redirect(url_for('welcome'))


if __name__ == '__main__':
	#app.run(debug=True)
	app.run()