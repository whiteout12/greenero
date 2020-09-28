from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, make_response
from flask_mail import Mail, Message
from forms import LoginForm, RegisterForm, ChangeUserForm, CreateInvoice, ChangeInvoice
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
#from users_db import listAllUserNames
import psycopg2
from swish_qr_gen import swishQR, swishQRbase64
#from weasyprint import HTML
from flask_weasyprint import HTML, render_pdf
import io

#from jinja2 import jinja_template

#from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine, text
import psycopg2
#from flask.ext.login import login_user, login_required, logout_user

app = Flask(__name__)
mail = Mail(app)
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
mail = Mail(app)
#engine = create_engine('postgresql://bjorn:kerbus@whiteout.ddns.net:5432/DEV01FAKK')



login_manager.login_view = "welcome"

# get user by id, used by login_manager
@login_manager.user_loader
def load_user(user_id):
	from models import User
	return User.query.filter(User.userid == int(user_id)).first()

# our beloved index page, here is where the magic will happen
@app.route('/')
@login_required
def home():
	print(current_user)
	return render_template("index.html")

# if you are not logged in you will be directed to here
@app.route('/welcome')
def welcome():
	#print(current_user)
	#return render_template("welcome.html", user=current_user)
	return render_template("welcome.html")

#register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
	from models import User
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
			user = User.query.filter_by(username=request.form['username']).first()
			if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
				login_user(user)
				return redirect(url_for('home'))
			else:
				error = 'Invalid credentials. Please try again!'
	return render_template("login.html", form=form, error=error)

#change or delete user
@app.route('/changeuser', methods=['GET', 'POST'])
@login_required
def changeuser():
	from models import User
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
			return redirect(url_for('changeuser'))
	return render_template('register.html', form=form, change=True, username=current_user.username, email=current_user.email, phone=current_user.phone)

@app.route('/deleteaccount', methods=['GET', 'POST'])
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
		return redirect(url_for('welcome'))
	return {"message": "Delete not possible with get method"} 

#logout user
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You were just logged out')
	return redirect(url_for('welcome'))

#route to send a friend request from current user to selected user i request mestod = POST. If request method= GET then friends status string is returned
@app.route('/relations/request', methods=['GET', 'POST'])
@login_required
def friendrequest():
	from models import User, Relationship
	if request.method == 'POST':
		data = request.get_json()
		if Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=3).first():
			return {'message' : "already friends"}
		if Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=2).first():
			return {'message' : "friend request already sent, wait for confirmation"}
		if Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=1).first():
			return {'message' : "friend request pending. Either accept or reject."}
		else:
			user_sending_req = Relationship(user=current_user.userid,
				receiving_user=data['FriendUserID'],
				status=1)
			user_receiving_req = Relationship(user=data['FriendUserID'],
				receiving_user=current_user.userid,
				status=2)
			#print(new_rel.userid)
			db.session.add(user_sending_req)
			db.session.add(user_receiving_req)
			db.session.commit()
			return {"message": 'friend request sent from '+str(current_user.username)+' to '+str(User.query.filter_by(userid=data['FriendUserID']).first().username)}

	return {'message' : "No post in friend request"}

@app.route('/relations/accept', methods=['GET', 'POST'])
@login_required
def accept_friendrequest():
	from models import User, Relationship
	if request.method == 'POST':

		data = request.get_json()
		print(data)
		if(Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=1).first()):
			Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid).first().accept_req()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=data['FriendUserID']).first().accept_req()
			return {'message' : "friendrequest acepted"}
		else:
			return {'error' : "there was no friend request"}

		return {"message": 'friend request sent from '+str(current_user.username)+' to '+str(User.query.filter_by(userid=data['FriendUserID']).first().username)}

	return {'message' : "No post in accept friend request"}

@app.route('/relations/reject', methods=['GET', 'POST'])
@login_required
def reject_friendrequest():
	from models import User, Relationship
	if request.method == 'POST':
		data = request.get_json()
		print(data)
		if(Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=1).first()):
			Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=data['FriendUserID']).first().delete()
			return {'message' : "friendrequest rejected"}
		else:
			return {'error' : "there was no friend request"}

		return {"message": 'friend request sent from '+str(current_user.username)+' to '+str(User.query.filter_by(userid=data['FriendUserID']).first().username)}

	return {'message' : "No post in accept friend request"}

@app.route('/relations/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw_friendrequest():
	from models import User, Relationship
	if request.method == 'POST':

		data = request.get_json()
		print(data)
		if(Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=3).first()):
			return {'message' : "request already accepted"}
		if(Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=2).first()):
			#print(user.username)
			Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=data['FriendUserID']).first().delete()
			return {'message' : "friendrequest withdrawn"}
		else:
			return {'error' : "there was no friend request",
					'message' : "already rejected"}

		return {"message": 'friend request sent from '+str(current_user.username)+' to '+str(User.query.filter_by(userid=data['FriendUserID']).first().username)}

	return {'message' : "No post in accept friend request"}

@app.route('/relations/unfriend', methods=['GET', 'POST'])
@login_required
def unfriend():
	from models import User, Relationship
	if request.method == 'POST':

		data = request.get_json()
		print(data)
		if(Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=3).first()):
		#if(current_user.rel_sender.frienduserid=:
			#print(user.username)
			Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=3).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=data['FriendUserID'], statusid=3).first().delete()
			return {'message' : "friend removed"}
		else:
			return {'error' : "there was no friend request"}

		return {"message": 'friend request sent from '+str(current_user.username)+' to '+str(User.query.filter_by(userid=data['FriendUserID']).first().username)}

	return {'message' : "No post in accept friend request"}	

@app.route('/relations/getrelations')
@login_required
def relations():
	from models import User
	
	results = []
	friends =[]
	request_by_me = []
	request_to_me = []
	blocked_by_me = []
	blocked_to_me = []
	for i in current_user.friend_requester:

		r = {
		'id' : i.frienduserid,
		'username' : i.rel_receiver.username,
		'status' : i.statusid
		}

		if i.statusid == 3:
			friends.append(r)
		elif i.statusid == 1:
				request_by_me.append(r)
		elif i.statusid == 2:
				request_to_me.append(r)
		elif i.statusid == 4:
			blocked_by_me.append(r)
		elif i.statusid == 5:
			blocked_to_me.append(r)

	return jsonify({
		'friends' : friends,
		'request_by_me' : request_by_me,
		'request_to_me' : request_to_me,
		'blocked_by_me' : blocked_by_me,
		'blocked_to_me' : blocked_to_me,
		})

@app.route('/test')
@login_required
def test():
	print('going to test procedures')
	from models import Relationship

	allusers = db.engine.execute("SELECT * FROM users")
	result = [dict(zip(tuple (allusers.keys()) ,i)) for i in allusers.cursor]
	print(result)

	return jsonify(result)


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

@app.route('/invoice/create-emb=<embedded>', methods=['GET', 'POST'])
@login_required
def createInvoice(embedded):
	print("invoice")
	from models import User, Invoice
	form = CreateInvoice()
	#form.receiver.choices = [(g.frienduserid, User.query.filter_by(userid=g.frienduserid).first().username) for g in Relationship.query.filter_by(userid=current_user.userid, statusid=3).all()]
	#form.receiver.choices = [(g.frienduserid, g.rel_receiver.username) for g in current_user.get_friends()]
	choices = [(-1, 'Select receiver')]
	print(choices)
	for i in current_user.get_friends():
		choices.append((i.frienduserid, i.rel_receiver.username))
	#choices.append((g.frienduserid, g.rel_receiver.username) for g in current_user.get_friends())
	print(choices)
	form.receiver.choices = choices
	#form.receiver.choices = ([(g.frienduserid, g.rel_receiver.username) for g in current_user.get_friends()])
	if embedded=="false":
		emb=False
	else:
		emb=True
	#print("username: ", form.username.data)
	if form.validate_on_submit():
		invoice = Invoice(
			amount=form.amount.data,
			description=form.description.data,
			userid=current_user.userid,
			receiving_user=form.receiver.data
			
			)
		print(invoice)
		db.session.add(invoice)
		db.session.commit()
		print(form.receiver.data, form.description.data, form.amount.data)
		print({'message' : "Invoice sent"})
		return {'message' : "Invoice sent"}
	return render_template('invoice.html', form=form, embedded=emb)

@app.route('/invoice/getinvoices')
@login_required
def getInvoices():
	from models import User, Invoice
	print(current_user.userid)
	received = []
	sent = []
	
	for i in current_user.invoice_receiver:
		
		r = {
		'invoiceid' : i.invoiceid,
		'senderid' : i.userid,
		'sender' : i.sender.username,
		'description' : i.description,
		'amount' : i.amount,
		'invoicestatus' : i.statusid,
		'message' : i.message
		}
		#print(r)
		received.append(r)
	
	for i in current_user.invoice_sender:
		
		r = {
		'invoiceid' : i.invoiceid,
		'recieverid' : i.frienduserid,
		'receiver' : i.receiver.username,
		'description' : i.description,
		'amount' : i.amount,
		'invoicestatus' : i.statusid,
		'message' : i.message
		}
		#print(r)
		sent.append(r)

	return jsonify({
		'received' : received,
		'sent' : sent
		})

@app.route('/invoice/getinvoice<invoiceid>')
@login_required
def getInvoice(invoiceid):
	from models import User, Invoice
	print('currentuserID ', current_user.userid)
	print('invoiceid to look for ',invoiceid)
	
	invoice_to_get=Invoice.query.filter_by(invoiceid=invoiceid).first()
	
	if(invoice_to_get):
		if(invoice_to_get.userid==current_user.userid or invoice_to_get.frienduserid==current_user.userid):
			invoice = {
				'invoiceid' : invoice_to_get.invoiceid,
				'receiverid' : invoice_to_get.frienduserid,
				'receiver' : invoice_to_get.receiver.username,
				'description' : invoice_to_get.description,
				'amount' : invoice_to_get.amount,
				'invoicestatus' : invoice_to_get.statusid,
				'message' : invoice_to_get.message,
				'senderid' : invoice_to_get.userid,
				'sender' : invoice_to_get.sender.username,
				'duedate' : invoice_to_get.duedate,
				'createddate' : invoice_to_get.invoice_date,
				'version' : invoice_to_get.invoice_version
				}

			return jsonify({
					'success' : True,
					'invoice' : invoice
					})
		return jsonify({
		'success' : False,
		'message' : 'not authorized'
		})
	return jsonify({
		'success' : False,
		'message' : 'no invoice found'
		})


@app.route('/invoice/pay', methods=['GET', 'POST'])
@login_required
def payInvoice():

	from models import Invoice
	if request.method == 'POST':
		data = request.get_json()
		print(data)
		Invoice.query.filter_by(invoiceid=data['InvoiceID']).first().change_status(2)

	

	return jsonify({
		'message' : 'invoice marked as payed'
		})

@app.route('/invoice/reject', methods=['GET', 'POST'])
@login_required
def rejectInvoice():

	from models import Invoice
	if request.method == 'POST':
		data = request.get_json()
		print(data)
		invoice_to_reject=Invoice.query.filter_by(invoiceid=data['InvoiceID']).first()
		invoice_to_reject.reject(data['message'])
	

		return jsonify({
			'message' : 'invoice marked as rejected'
			})
	return {'message' : "No post in reject invoice"}	

@app.route('/invoice/remove', methods=['GET', 'POST'])
@login_required
def removeInvoice():
	print("invoice")
	#print(invoiceid)
	from models import Invoice
	if request.method == 'POST':
		data = request.get_json()

		invoice_to_delete=Invoice.query.filter_by(invoiceid=data['InvoiceID']).first()
		invoice_to_delete.delete()
		return {'message' : "invoice removed"}

	return {'message' : "No post in accept friend request"}	

@app.route('/invoice/change<invoice>', methods=['GET', 'POST'])
@login_required
def changeInvoice(invoice):
	print("invoice")
	print(invoice)
	from models import User, Invoice
	form = ChangeInvoice()
	
	emb=True
	invoice_to_change=Invoice.query.filter_by(invoiceid=invoice).first()
	print(invoice_to_change)
	#print("username: ", form.username.data)
	if form.validate_on_submit():
		invoice_to_change.update(form.description.data, form.amount.data)
		print(invoice_to_change)
		#db.session.add(invoice)
		#db.session.commit()
		#print(form.receiver.data, form.description.data, form.amount.data)
		print({'message' : "Invoice changed"})
		return {'message' : "Invoice changed"}
	return render_template('invoice.html', form=form, embedded=emb, change=True, invoice=invoice_to_change)

@app.route('/invoices/renderpdf/<inv>')
@login_required
def renderpdf(inv):
	
	username=current_user.username
	invoice = getInvoice(inv).get_json()
	if(invoice['success']):
		

		swish_qr_base64=swishQRbase64(current_user.phone, invoice['invoice']['amount'], invoice['invoice']['description'])
		print_html = render_template('invoice_pdf_template.html', username=username, invoice=invoice['invoice'], qrCode_base64=swish_qr_base64, css1=url_for('static', filename='invoice_pdf/boilerplate.css'), css2=url_for('static', filename='invoice_pdf/main.css'), css3=url_for('static', filename='invoice_pdf/normalize.css'))
		
		
		return render_pdf(HTML(string=print_html), download_filename='invoice'+str(invoice['invoice']['invoiceid'])+'.pdf')
	else:

		return {'message' : invoice['message']}
	
@app.route('/invoices/email/<inv>')
@login_required
def email_invoice(inv):
	print(current_user.userid)
	print(inv)
	invoice = getInvoice(inv).get_json()
	if(invoice['success']):
		from models import User, Invoice
		payee = User.query.filter_by(userid=invoice['invoice']['receiverid']).first()

		if payee.email:
			print('payee email: ', payee.email)
			if current_user.phone:
				
				username=current_user.username
				swish_qr_base64=swishQRbase64(current_user.phone, invoice['invoice']['amount'], invoice['invoice']['description'])
				html = HTML(string=render_template('invoice_pdf_template.html', username=username, invoice=invoice['invoice'], qrCode_base64=swish_qr_base64, css1=url_for('static', filename='invoice_pdf/boilerplate.css'), css2=url_for('static', filename='invoice_pdf/main.css'), css3=url_for('static', filename='invoice_pdf/normalize.css')))
				pdf = io.BytesIO(html.write_pdf())
				msg = Message("Du har blivit fakkad :)",
			                  sender="bjorncarlsson87@gmail.com",
			                  recipients=[payee.email])
				msg.body = "Du har blivit fakkad, se bifogat" 
				msg.attach('invoice.pdf', 'application/pdf', data=pdf.read())
				mail.send(msg)
				return {'message' : "Email sent!"}
			else:
				return {'message' : "You have no phone number registred which is needed to genarate swish QRcode :("}
		else:
			return {'message' : "Payee has no email address registered :("}
	else:

		return {'message' : invoice['message']}	
		
	

@app.route('/users/<query>')
@login_required
def users(query):
	print(current_user.userid)
	from models import User
	if query == '*':		
		return jsonify([i.serialize() for i in User.query.filter(current_user.username!=User.username).all()])
	search = "%{}%".format(query)
	return jsonify([i.serialize() for i in User.query.filter(User.username.ilike(search), current_user.username!=User.username).all()])


if __name__ == '__main__':
	app.run()