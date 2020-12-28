from flask import render_template, Blueprint, flash, url_for, redirect, request
from flask_login import login_required, current_user, login_user, logout_user
from fakk.forms import ChangeUserForm, RegisterForm, LoginForm, ResetPasswordForm
from fakk import bcrypt, db
from fakk.models import User, Relationship, Invoice
from fakk.utils.token_email import generate_confirmation_token, confirm_token, send_confirmation_link_email, send_confirmation_link_email2, send_password_link_email
from datetime import datetime
import random
from fakk.utils.send_sms import sendSMS



user = Blueprint('user', __name__, url_prefix='/user')



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
			password=form.password.data,
			usertype=2,
			credits=100 
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
				next = request.args.get('next')
				
				
				flash('Inloggad! Välkommen in i värmen', category="success")
				return redirect(next or url_for('main.home'))
			else:
				error = 'Felaktiga inloggningsuppgifter. Försök igen!'
				print(error)
	return render_template("login.html", form=form, error=error)

@user.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	return render_template("user_profile.html")


@user.route('/change', methods=['GET', 'POST'])
@login_required
def changeuser():
	form = ChangeUserForm()
	if form.validate_on_submit():
		
		update = False
		if current_user.username != form.username.data:
			current_user.username = form.username.data
			flash('Användarnamnet uppdaterat', category='success')
			update = True
		if current_user.email != form.email.data:
			if len(form.email.data)==0:
				if current_user.email:
					current_user.email = None
					current_user.confirmed_email = None
					current_user.confirmed_email_on = None
					flash('Emailadress borttagen', category='success')
					update = True
			else:
				current_user.email = form.email.data
				current_user.confirmed_email = None
				current_user.confirmed_email_on = None				
				flash('Emailadress uppdaterad', category='success')
				send_confirmation_link_email(form.email.data)		
				update = True
		print('test ', current_user.phone != form.phone.data)
		if current_user.phone != form.phone.data:
			if len(form.phone.data)==0:
				if current_user.phone:
					current_user.phone = None
					current_user.confirmed_phone = None
					current_user.confirmed_phone_on = None
					flash('Telefonnumret borttaget', category='success')
					update = True
			else:
				current_user.phone = form.phone.data
				send_sms_confirmation_code(form.phone.data)
				update = True
		
		if(form.password.data):
			current_user.updatePassword(
			password=form.password.data
			)
			flash('Lösenord uppdaterat', category='success')
			passwordWasUpdated = True
		if update:
			db.session.commit()
		elif update == False or not passwordWasUpdated :
			flash('Inget att uppdatera', category="warning")
		#if(form.username.data == "" and form.email.data =="" and form.phone.data =="" and form.password.data ==""):
		#	flash('Nothing to update')
		#else:
		#	flash('Your information was updated', category='success')
		#	if form.email.data:
		#		send_confirmation_link_email(form.email.data)
		return redirect(url_for('user.profile'))
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

@user.route('/confirm/email/<token>')
#@login_required
def confirm_email(token):

	email = confirm_token(token)
	print('confirm token', email)
	if email==False:
		print('email', email)
		flash('Länken har utgått eller är ej gilitg.', category='danger')
	else:
		user = User.query.filter_by(usertype=2, email=email).first()
		if user.confirmed_email:
			flash('Emailadressen redan bekräftad.', category='success')
		else:
			user.confirmed_email = True
			user.confirmed_email_on = datetime.now()
			db.session.add(user)
			db.session.commit()
			flash('Din E-mailadress har bekräftats!', category='success')
			print('letar fakturor')
			print(email)
			if User.query.filter_by(usertype=1, email=email).first():
				print('hittade anv')
				print(user)
				print(user.userid)
				dummyuser = User.query.filter_by(usertype=1, email=email).first()
				print('dummyuser', dummyuser)
				if dummyuser:
					invoices = Invoice.query.filter_by(frienduserid=dummyuser.userid).all()
					for invoice in invoices:
						print(invoice)
						invoice.frienduserid = user.userid
						db.session.commit()
					dummyuser.delete()
					db.session.commit()
					flash('Hittade lite fakturor som tidigare varit kopplad till din E-mailadress. De är nu kopplade till ditt konto.', category='success')
			#print('går mot main.home')
	return redirect(url_for('user.profile'))

@user.route('/reset/<token>', methods=['GET', 'POST'])
#@login_required
def reset_password_token(token):
	try:
		email = confirm_token(token)
	except:
		flash('Länken har utgått eller är ej gilitg.', category='danger')
		return redirect(url_for('send-password-reset-link'))
	
	else:
		user = User.query.filter_by(email=email, confirmed_email=True).first_or_404()
		form=ResetPasswordForm()
		if form.validate_on_submit():
			user.updatePassword(form.password.data)
			flash('Lösenordet uppdaterat.', category="success")
			return (redirect(url_for('user.login')))

		return render_template('resetpassword.html', form=form, user=user)	
	#return redirect(url_for('reset/', token=token))

#NOT USED YET
@user.route('/confirm/email', methods=['GET', 'POST'])
#@login_required
def confirm_email2():
	try:
		email = confirm_token(token)
	except:
		flash('Länken har utgått eller är ej gilitg.', category='danger')
	user = User.query.filter_by(email=email).first_or_404()
	if user.confirmed_email:
		flash('Emailadressen redan bekräftad.', category='success')
	else:
		user.confirmed_email = True
		user.confirmed_email_on = datetime.now()
		db.session.add(user)
		db.session.commit()
		flash('Din emailadress har bekräftats!', category='success')
		print('letar fakturor')
		if User.query.filter_by(usertype=1, email=email).first_or_404():
			print('hittade anv')
			dummyuser = User.query.filter_by(usertype=1, email=email).first_or_404()
			invoices = Invoice.query.filter_by(frienduserid=dummyuser.userid).all()
			for invoice in invoices:
				print(invoice)
				invoice.frienduserid = user.userid
			dummyuser.delete()
			db.session.commit()
			flash('Hittade en eller flera fakturor som tidigare varit kopplad till din E-mailadress. De är nu kopplade till ditt konto.', category='success')
	return redirect(url_for('main.home'))

@user.route('/confirm/phone', methods=['GET', 'POST'])
@login_required
def confirm_phone():

	if request.method == 'POST':
		
		#print(isinstance(int(request.form['sms_code']), int))
		try:
			int(request.form['sms_code'])
			if int(request.form['sms_code']) == current_user.confirmed_phone_otp:

				current_user.confirmed_phone = True
				current_user.confirmed_phone_on = datetime.now()
				current_user.confirmed_phone_otp = None
				db.session.commit()
				users = User.query.filter(User.usertype==2, User.phone==current_user.phone, User.confirmed_phone==None).all()
				print(users)
				if users:
					for user in users:
						user.phone = None
					db.session.commit()
				flash('Telefonummer bekräftat', category='success')
				print('letar fakturor')
				if User.query.filter_by(usertype=1, phone=current_user.phone).first():
					print('hittade anv')
					#print(user)
					#print(user.userid)
					dummyuser = User.query.filter_by(usertype=1, phone=current_user.phone).first_or_404()
					print(dummyuser)
					invoices = Invoice.query.filter_by(frienduserid=dummyuser.userid).all()
					for invoice in invoices:
						print(invoice)
						invoice.frienduserid = current_user.userid
						db.session.commit()
					dummyuser.delete()
					db.session.commit()
					flash('Hittade en eller flera fakturor som tidigare varit kopplade till ditt telefonnummer. De är nu kopplade till ditt konto.', category='success')
			else:
				print('Kod ej gilitg. Du kan skicka efter en ny')
				flash('Kod ej gilitg. Du kan skicka efter en ny', category='warning')
		except ValueError:
			flash('Kod har fel format.', category='danger')
	return redirect(url_for('user.profile'))

@user.route('/send-email-confirmation-link')
@login_required
def send_email_confirmation_link():
	send_confirmation_link_email(current_user.email)

	return redirect(url_for('user.profile'))

@user.route('/send-sms-confirmation-code')
@login_required
def send_sms_code_current():
	send_sms_confirmation_code(current_user.phone)
	return redirect(url_for('user.profile'))
	

def send_sms_confirmation_code(number):
	print('send SMS code')
	n = random.randint(1000,9999)
	print('otp code: ', n)
	current_user.confirmed_phone_otp = n
	current_user.confirmed_phone_on = None
	current_user.confirmed_phone = None
	db.session.commit()
	message = 'Ange koden för att bekräfta telefonnummer. Kod: ' + str(n)
	sms_status = sendSMS(number, message)
	flash('Ett SMS har skickats till ' +str(number), category='success')
	return 


@user.route('/send-password-reset-link', methods=['GET', 'POST'])
def send_password_reset_link():

	if request.method == 'POST':
		#request.form['sms_code']
		if User.query.filter_by(email=request.form['email'], confirmed_email=True).first():
			send_password_link_email(request.form['email'])
		flash('Om emailadressen du angav finns bekräftad så har ett email skickats med en länk för återställning av lösenord', category='success')
	return render_template('forgotpassword.html')
