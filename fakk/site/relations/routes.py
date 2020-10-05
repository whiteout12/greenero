from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from fakk import db
from fakk.models import User, Relationship

relations_blueprint = Blueprint('relations_blueprint', __name__)


@relations_blueprint.route('/user')
@login_required
def user():
	print('going to user page')
	#flash('You were just logged out')
	return render_template("user.html", user=True)

@relations_blueprint.route('/users/<query>')
@login_required
def users(query):
	print(current_user.userid)
	#from models import User
	if query == '*':		
		return jsonify([i.serialize() for i in User.query.filter(current_user.username!=User.username).all()])
	search = "%{}%".format(query)
	return jsonify([i.serialize() for i in User.query.filter(User.username.ilike(search), current_user.username!=User.username).all()])


#route to send a friend request from current user to selected user i request mestod = POST. If request method= GET then friends status string is returned
@relations_blueprint.route('/relations/request', methods=['GET', 'POST'])
@login_required
def friendrequest():
	#from fakk import db
	#from models import User, Relationship
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

@relations_blueprint.route('/relations/accept', methods=['GET', 'POST'])
@login_required
def accept_friendrequest():
	#from models import User, Relationship
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

@relations_blueprint.route('/relations/reject', methods=['GET', 'POST'])
@login_required
def reject_friendrequest():
	#from models import User, Relationship
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

@relations_blueprint.route('/relations/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw_friendrequest():
	#from models import User, Relationship
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

@relations_blueprint.route('/relations/unfriend', methods=['GET', 'POST'])
@login_required
def unfriend():
	#from models import User, Relationship
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

@relations_blueprint.route('/relations/getrelations')
@login_required
def relations():
	#from models import User
	
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