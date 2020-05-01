from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from forms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

#from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine, text
import psycopg2

from config import DevelopmentConfig
#from flask.ext.login import login_user, login_required, logout_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
#db = create_engine("postgresql://localhost/postgres")
#db = create_engine("postgresql+psycopg2://localhost/postgres")
#app.secret_key = "mySecretKey"

# config
import os
app.config.from_object(DevelopmentConfig)
login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)




login_manager.login_view = "login"

# get user by id, used by login_manager
@login_manager.user_loader
def load_user(user_id):
	from models import User
	return User.query.filter(User.id == int(user_id)).first()

# our beloved index page, here is where the magic will happen
@app.route('/')
@login_required
def home():
	print(current_user)
	return render_template("index.html")

# if you are not logged in you will be directed to here
@app.route('/welcome')
def welcome():
	print(current_user)
	return render_template("welcome.html", user=current_user)

#register new user
@app.route('/register',  methods=['GET', 'POST'])
def register():
	from models import User
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(
			name=form.username.data,
			email=form.email.data,
			password=form.password.data
			)
		db.session.add(user)
		db.session.commit()
		flash('You were just logged in as: ' + (user.name))
		login_user(user)
		return redirect(url_for('home'))
	return render_template('register.html', form=form)

#login user
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
				flash('You were just logged in as: ' + current_user.name)
				return redirect(url_for('home'))

			else:
				error = 'Invalid credentials. Please try again!'
	return render_template("login.html", form=form, error=error)

#logout user
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You were just logged out')
	return redirect(url_for('welcome'))

@app.route('/user')
@login_required
def user():
	print('going to user page')
	#flash('You were just logged out')
	return render_template("user.html", user=True)

@app.route('/claim')
@login_required
def claim():
	print('going to claim page')
	#flash('You were just logged out')
	return render_template("claim.html", claim=True)

@app.route('/users/<query>')
@login_required
def users(query):
	from models import User
	print query
	print('try to query all')
	
	#print(user.name)
	#print(user.email)
	#print(user.password)
	if query == '*':
		users = db.session.query(User).all()
		all_users = []
		for d in users:
			d = {
				'id' : d.id,
				'name' : d.name,
				'email' : d.email
			}
			all_users.append(d)
			print (all_users)
			jsonify(all_users)
		return jsonify(all_users)
	else:
		user = User.query.filter_by(name = query).first()
		user_2 = {
		'id' : user.id,
		'name' : user.name,
		'email' : user.email
		}
		print (user_2)
	return jsonify(user_2)
		
	#print(user.toJson())
	#users = User.query().all()
	#print(users)
	#users = db.session.query(User).all()
	#result = [dict(zip(tuple (users.keys()) ,user)) for user in users]
	#for user in users
	#users = session.query(User).all()
	#users = User.query.all()
	#for user in users:
	#print (users)
	#print (db.session.query(User).all())
	#result = [d.__dict__ for d in users]
	#print jsonify(all_users)
	#json_list=[i.serialize() for i in users]
	#print(json_list)
	#return jsonify(all_users)
	#return jsonify(user_2)


if __name__ == '__main__':
	app.run()
