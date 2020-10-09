from flask import render_template, Blueprint, flash, url_for, redirect, request
from flask_login import login_required, current_user, login_user, logout_user
from fakk.forms import ChangeUserForm, RegisterForm, LoginForm
from fakk import bcrypt, db, mail
from fakk.models import User, Relationship
from fakk.utils.token_email import generate_confirmation_token, confirm_token
from flask_mail import Message
from datetime import datetime



user = Blueprint('user', __name__, static_folder='/fakk/static')



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
				flash('Inloggad! Välkommen in i värmen', category="success")
				return redirect(url_for('main.home'))
			else:
				error = 'Invalid credentials. Please try again!'
				print(error)
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
			flash('Your information was updated', category='success')
			return redirect(url_for('user.changeuser'))
	return render_template('register.html', form=form, change=True, username=current_user.username, email=current_user.email, phone=current_user.phone)

#change or delete user

@user.route('/deleteaccount', methods=['GET', 'POST'])
@login_required
def deleteaccount():
	if request.method == 'POST':
		for i in Relationship.query.filter_by(userid=current_user.userid).all():
			i.delete()
		for i in Relationship.query.filter_by(frienduserid=current_user.userid).all():
			i.delete()
		current_user.delete()
		logout_user()
		flash('You were just logged out and your account was removed', category='success')
		return redirect(url_for('main.welcome'))
	return {"message": "Delete not possible with get method"} 

#logout user
@user.route('/logout')
@login_required
def logout():
	logout_user()
	flash('Utloggad, välkommen åter', category='success')
	return redirect(url_for('main.welcome'))

@user.route('/confirm/<token>')
#@login_required
def confirm_email(token):
	try:
		email = confirm_token(token)
	except:
		flash('The confirmation link is invalid or has expired.', 'danger')
	user = User.query.filter_by(email=email).first_or_404()
	if user.confirmed_email:
		flash('Account already confirmed. Please login.', 'success')
	else:
		user.confirmed_email = False
		user.confirmed_email_on = datetime.now()
		db.session.add(user)
		db.session.commit()
		flash('You have confirmed your account. Thanks!', 'success')
	return redirect(url_for('main.home'))

@user.route('/send-email-confirmation-link')
@login_required
def send_email_confirmation_link():
	token = generate_confirmation_token(current_user.email)
	confirm_url = url_for('user.confirm_email', token=token, _external=True)
	html = render_template('confirm_email.html', confirm_url=confirm_url)
    #subject = "Please confirm your email"
    #send_email(current_user.email, subject, html)
	msg = Message("Du har bekräftelseemail", sender="bjorncarlsson87@gmail.com", recipients=[str(current_user.email)])
	msg.html = html
	msg.body = "bekräftelslänk" + str(confirm_url)
	mail.send(msg)
	flash('A new confirmation email has been sent.', 'success')
	return redirect(url_for('main.home'))
