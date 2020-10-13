from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from fakk import db
from fakk.models import User, Relationship



contacts = Blueprint('contacts', __name__, url_prefix='/site/contacts')


@contacts.route('/users/<query>')
@login_required
def users(query):
	print(current_user.userid)
	#from models import User
	if query == '*':		
		return jsonify([i.serialize() for i in User.query.filter(current_user.username!=User.username).all()])
	search = "%{}%".format(query)
	return jsonify([i.serialize() for i in User.query.filter(User.username.ilike(search), current_user.username!=User.username).all()])


@contacts.route('/friends')
@login_required
def friends():
	friends = current_user.friend_requester
	return render_template('friends.html', user=current_user, friends=friends, title='Kontakter')

@contacts.route('/search', methods=['GET', 'POST'])
@login_required
def friend_search():
	if request.method == 'POST':
		final_list = []
		query = "%{}%".format(request.form['user_search'])
		#print(len(request.form['user_search']))
		#if len(request.form['user_search']) == 0:
		#	flash('Inget sökord angivet', category="warning")
		#	return redirect(url_for('contacts.friends'))

		result = User.query.filter(User.username.ilike(query), current_user.username!=User.username).all()
		#print('result: ', result)
		if result:
			for user in result:
				#print (user.userid)
				relation = Relationship.query.filter_by(userid=current_user.userid, frienduserid=user.userid).first()
				if relation:
					r = {
						'user' : user,
						'status' : relation.statusid
						}
				else:
					r = {
						'user' : user,
						'status' : 0
						}
				final_list.append(r)
				#print(final_list)
			flash('Hittade '+str(len(result))+'st resultat.', category="success")
		#flash('search term ' +request.form['user_search'] , category='success')	
		#return render_template('friends.html', user=current_user, friends=current_user.friend_requester, title='Kontakter', searchresult=User.query.filter(User.username.ilike(query), current_user.username!=User.username).all())
		else:
			flash('Inga kontakter hittades när du sökte efter "'+ request.form['user_search']+'"', category="danger")
		return render_template('friends.html', user=current_user, friends=current_user.friend_requester, title='Kontakter', searchresult=final_list)

#route to send a friend request from current user to selected user i request mestod = POST. If request method= GET then friends status string is returned
@contacts.route('/request', methods=['GET', 'POST'])
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

#route to send a friend request from current user to selected user i request mestod = POST. If request method= GET then friends status string is returned
@contacts.route('/<friend_id>/request', methods=['GET', 'POST'])
@login_required
def friendrequest_site(friend_id):
	#from fakk import db
	#from models import User, Relationship
	
	if Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=3).first():
		flash('Redan vänner', category='warning')
		return redirect(url_for('contacts.friends'))
	if Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=2).first():
		flash('Vänförfrågan redan skickad, invänta svar', category='warning')
		return redirect(url_for('contacts.friends'))
	if Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=1).first():
		flash('Du har redan en vänförgrågan att svara på.', category='warning')
		return redirect(url_for('contacts.friends'))
	else:
		user_sending_req = Relationship(user=current_user.userid,
			receiving_user=friend_id,
			status=1)
		user_receiving_req = Relationship(user=friend_id,
			receiving_user=current_user.userid,
			status=2)
		#print(new_rel.userid)
		db.session.add(user_sending_req)
		db.session.add(user_receiving_req)
		db.session.commit()
		flash('Vänförfrågan skickad', category='success')
		return redirect(url_for('contacts.friends'))
		

	return {'message' : "No post in friend request"}

@contacts.route('/<friend_id>/accept', methods=['GET', 'POST'])
@login_required
def accept_friendrequest_site(friend_id):
	if(Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=1).first()):
		print('ja det finns en vänförfrågan')
		Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid).first().accept_req()
		Relationship.query.filter_by(userid=current_user.userid, frienduserid=friend_id).first().accept_req()
		flash('Vänförfrågan godkänd!', category='success')
		return redirect(url_for('contacts.friends'))
	else:
		print('hittade ingen vänförfrågan')
		flash('Vänförfrågan ej godkänd!', category='warning')
		return redirect(url_for('contacts.friends'))

@contacts.route('/<friend_id>/reject', methods=['GET', 'POST'])
@login_required
def reject_friendrequest_site(friend_id):
	if(Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=1).first()):
		print('ja det finns en vänförfrågan')
		Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid).first().delete()
		Relationship.query.filter_by(userid=current_user.userid, frienduserid=friend_id).first().delete()
		flash('Vänförfrågan avböjd!', category='success')
		return redirect(url_for('contacts.friends'))
	else:
		print('hittade ingen vänförfrågan')
		flash('Vänförfrågan gick ej att avböja!', category='warning')
		return redirect(url_for('contacts.friends'))

@contacts.route('/<friend_id>/withdraw', methods=['GET', 'POST'])
@login_required
def unfriend_site(friend_id):
	
	if(Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=3).first()):
			#print(user.username)
			Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=friend_id).first().delete()
			flash('Vänborttagen', category='success')
			
			return redirect(url_for('contacts.friends'))
	
	return redirect(url_for('contacts.friends'))

@contacts.route('/<friend_id>/unfriend', methods=['GET', 'POST'])
@login_required
def withdraw_friendrequest_site(friend_id):
	if(Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=3).first()):
			flash('Vänförfrågan redan accepterad', category='warning')
			return redirect(url_for('contacts.friends'))
	if(Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid, statusid=2).first()):
			#print(user.username)
			Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid).first().delete()
			Relationship.query.filter_by(userid=current_user.userid, frienduserid=friend_id).first().delete()
			flash('Vänförfrågan tillbakadragen!', category='success')
			
			return redirect(url_for('contacts.friends'))
	
	return redirect(url_for('contacts.friends'))

@contacts.route('/<friend_id>/view', methods=['GET', 'POST'])
@login_required
def friend_view_site(friend_id):
	friend = User.query.filter_by(userid=friend_id).first()
	relation = Relationship.query.filter_by(userid=friend_id, frienduserid=current_user.userid).first()
	if relation == None:
		status = 0
	else:
		status = relation.statusid		
	return render_template('friend.html', user=current_user, friend=friend, status=status, title=friend.username)


#TO BE MOVED TO API ROUTES

@contacts.route('/accept', methods=['GET', 'POST'])
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



@contacts.route('/reject', methods=['GET', 'POST'])
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

@contacts.route('/withdraw', methods=['GET', 'POST'])
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



@contacts.route('/unfriend', methods=['GET', 'POST'])
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

@contacts.route('/getrelations')
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
