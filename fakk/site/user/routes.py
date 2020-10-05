from flask import render_template, Blueprint, flash, url_for, redirect, request
from flask_login import login_required, current_user, login_user, logout_user
from fakk.forms import ChangeUserForm, RegisterForm, LoginForm
from fakk import bcrypt, db
from fakk.models import User


user = Blueprint('user', __name__)



#register new user
@user.route('/register', methods=['GET', 'POST'])
def register():
	#from models import User
	#from fakk import db
	#form = RegisterForm(listAllUserNames(), listAllUserNames())
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(
			username=form.username.data,
			#email=form.email.data,
			password=form.password.data
			)
		db.session.add(user)
		db.session.commit()
		#flash('You were just logged in as: ' + (user.name))
		login_user(user)
		return redirect(url_for('main.home'))
	return render_template('register.html', form=form)

#login user
@user.route('/login', methods=['GET', 'POST'])
def login():
	#from models import User
	error = None
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(username=request.form['username']).first()
			if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
				login_user(user)
				return redirect(url_for('main.home'))
			else:
				error = 'Invalid credentials. Please try again!'
	return render_template("login.html", form=form, error=error)

@user.route('/changeuser', methods=['GET', 'POST'])
@login_required
def changeuser():
	form = ChangeUserForm()
	if form.validate_on_submit():
		current_user.update(
			username=form.username.data,
			email=form.email.data,
			phone=form.phone.data,
			password=form.password.data
			)
		if(form.username.data == "" and form.email.data =="" and form.phone.data =="" and form.password.data ==""):
			flash('Nothing to update')
		else:
			flash('Your information was updated')
			return redirect(url_for('user.changeuser'))
	return render_template('register.html', form=form, change=True, username=current_user.username, email=current_user.email, phone=current_user.phone)

#change or delete user

@user.route('/deleteaccount', methods=['GET', 'POST'])
@login_required
def deleteaccount():
	if request.method == 'POST':
		from models import User, Relationship
		for i in Relationship.query.filter_by(userid=current_user.userid).all():
			i.delete()
		for i in Relationship.query.filter_by(frienduserid=current_user.userid).all():
			i.delete()
		current_user.delete()
		logout_user()
		flash('You were just logged out and your account was removed')
		return redirect(url_for('main.welcome'))
	return {"message": "Delete not possible with get method"} 

#logout user
@user.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You were just logged out')
	return redirect(url_for('main.welcome'))
