from app import db, bcrypt
<<<<<<< HEAD
from flask_login import UserMixin

# create user 
=======
#from flask_login import LoginManager
from flask_login import UserMixin


>>>>>>> 400a8281184cc1ca8bb014707cc75b71f73bdf25
class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String)
    #posts = relationship("BlogPost", backref="author")

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
<<<<<<< HEAD
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        #self.password = password

#	def is_authenticated(self):
#		return True
#
#	def is_active(self):
#		return True
#	
#	def is_anonymous(self):
#		return False
#
#	def get_id(self):
#		return unicode(self.id)
	def to_json(self):
	#"""Return object data in easily serializable format"""
		return {
			'id' : self.id,
			'name' : self.name,
			'email' : self.email
		}

    def __repr__(self):
    	#return '<name {}'.format(self.name).decode('utf-8')
    	#return '<name - {}>'.format(self.name)
		return '<name %r>' % self.name
		#return f"User('{self.name}','{self.email}')"
	#def __repr__(self):
		#return f"User('{self.name}','{self.email}')"
		#return '<User %r>' % self.username
=======
        self.password = bcrypt.generate_password_hash(password)
        #self.password = password

	def is_authenticated(self):
		return True

	def is_active(self):
		return True
	
	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

    def __repr__(self):
        return '<name {}'.format(self.name)
>>>>>>> 400a8281184cc1ca8bb014707cc75b71f73bdf25
