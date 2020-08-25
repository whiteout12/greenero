from app import db, bcrypt
#from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# create user 
#class User(db.Model, UserMixin):
class User(db.Model):

    __tablename__ = "users"

    userid = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    #posts = relationship("BlogPost", backref="author")
    #requester = db.relationship('Relationship', foreign_keys='Relationship.userid', backref='requester')
    #receiver = db.relationship('Relationship', foreign_keys='Relationship.frienduserid', backref='received')

    def __init__(self, username, password):
        self.username = username
        #self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        #self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userid

    def get_username(self):
        return self.username

    def update(self, username, email, password, phone):
        if(username):
            self.username = username
        if(email):
            self.email = email
        if(phone):
            self.phone = phone
        if(password):
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()

    def serialize(self):
        return {
        'userid' : self.userid,
        'username' : self.username,
        'email' : self.email
        }
    def delete(self):
        db.session.delete(self)
        db.session.commit()

   # def __repr__(self):
    #	return '<name - {}>'.format(self.username)

class Relationship(db.Model):

    __tablename__ = "friends"

    friendshipid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    frienduserid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    statusid = db.Column(db.Integer)
    #__table_args__ = (db.UniqueConstraint('frienduserid', 'userid', name='_frienduserid_uc'), )
    #__table_args__ = (db.UniqueConstraint('receiving_user', 'requesting_user', name='_receiving_user_uc'), )
    def __init__(self, user, receiving_user, status):
        self.userid = user
        self.frienduserid = receiving_user
        self.statusid = status


    def get_id(self):
        return self.friendshipid

    def accept_req(self):
        self.statusid = 3
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return '<rel-userid - {}>'.format(self.userid)
   # def create_friend_req(self, receiving_user):
    #    
     #   return {'message' : friend request sent}