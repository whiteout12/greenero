from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from forms import LoginForm, RegisterForm, ChangeUserForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from users_db import listAllUserNames
import psycopg2

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
	print('try to login1')
	#print(request.form)
	#print(request.form['username'])
	#print(request.form['password'])
	#print(str(request.method()))
	if request.method == 'POST':
		print(request.form['username'])
		if form.validate_on_submit():

			print('try to login')

			user = User.query.filter_by(username=request.form['username']).first()
			if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
			#user.password == request.form['password']:
			#if request.form['username'] != 'admin' or request.form['password'] != 'admin':
				login_user(user)
				#session['logged_in'] = True
				#flash('You were just logged in as: ' + current_user.username)
				return redirect(url_for('home'))

			else:
				error = 'Invalid credentials. Please try again!'
	return render_template("login.html", form=form, error=error)

#change or delete user
@app.route('/changeuser', methods=['GET', 'POST'])
@login_required
def changeuser():
	from models import User
	#form = RegisterForm(listAllUserNames(), listAllUserNames())
	form = ChangeUserForm()
	if form.validate_on_submit():
		current_user.update(
			username=form.username.data,
			email=form.email.data,
			phone=form.phone.data,
			password=form.password.data
			)
		print("username from form: ", form.username.data)
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
	#flash('Delete not possible')
	return {"message": "Delete not possible with get method"} 

#logout user
@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You were just logged out')
	return redirect(url_for('welcome'))

#route to send a friend request from current user to selected user i request mestod = POST. If request method= GET then friends status string is returned
@app.route('/friendrequest', methods=['GET', 'POST'])
@login_required
def friendrequest():
	
	if request.method == 'POST':
		#print('to post friendrequest')
		data = request.get_json()
		t="CALL createfriendrequest('"+str(current_user.userid)+"','"+str(data['FriendUserID'])+"');"
		db.session.execute(t)
		db.session.commit()
		
		return {"message": 'friend request sent from '+str(current_user.userid)+' to '+str(data['FriendUserID'])}

	print('trying to fetch friends by username')
	t="SELECT getfriendsbyusername('"+current_user.username+"');"
	#print(t)
	myFriends = db.session.execute(t).fetchall()
	#print(friends)
	return 'friend relations '+str(myFriends)

#route to send a friend request from current user to selected user i request mestod = POST. If request method= GET then friends status string is returned
@app.route('/relations/request', methods=['GET', 'POST'])
@login_required
def friendrequest2():
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
			print('to post friendrequest')
			
			#print(user.username)
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
			#print(user.username)
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
		if(Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=2).first()):
			#print(user.username)
			Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=data['FriendUserID']).first().delete()
			return {'message' : "friendrequest withdrawn"}
		else:
			return {'error' : "there was no friend request"}

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
			#print(user.username)
			Relationship.query.filter_by(userid=data['FriendUserID'], frienduserid=current_user.userid, statusid=3).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=data['FriendUserID'], statusid=3).first().delete()
			return {'message' : "friend removed"}
		else:
			return {'error' : "there was no friend request"}

		return {"message": 'friend request sent from '+str(current_user.username)+' to '+str(User.query.filter_by(userid=data['FriendUserID']).first().username)}

	return {'message' : "No post in accept friend request"}	

@app.route('/relation/getrelations')
@login_required
def relation():
	from models import User, Relationship
	relations = Relationship.query.filter_by(userid=current_user.userid).all()

	results = []
	friends =[]
	request_by_me = []
	request_to_me = []
	blocked_by_me = []
	blocked_to_me = []
	for i in relations:
		if User.query.filter_by(userid=i.frienduserid).first():
			username = User.query.filter_by(userid=i.frienduserid).first().username
		else:
			username = 'N/A'
		r = {
		'id' : i.frienduserid,
		'username' : username,
		#'id' : User.query.filter_by(userid=i.frienduserid).first().username,
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

#@app.route('/testprocedure')
#@login_required
#def testprocedure():
#	print('going to test procedures')
#	print(current_user.username)

#	myFriends = db.engine.execute("SELECT getfriendsbyusername(%s)", (current_user.username))
#	print(myFriends)
#	result = [dict(zip(tuple (myFriends.keys()) ,i)) for i in myFriends.cursor]
#	print(jsonify(result))
#	friends = []
#	for i in myFriends.cursor:
#		friends.append(i)
#		print(friends, ' vänner')
#	print('vänner')
#	return 'test'

#@app.route('/usernames')
#@login_required
#def usernames():
#	return jsonify(listAllUserNames())
	#return 'hej'

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
	print(current_user.userid)
	from models import User
	if query == '*':		
		return jsonify([i.serialize() for i in User.query.filter(current_user.username!=User.username).all()])
	search = "%{}%".format(query)
	return jsonify([i.serialize() for i in User.query.filter(User.username.ilike(search), current_user.username!=User.username).all()])


if __name__ == '__main__':
	app.run()