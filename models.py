from app import db, bcrypt
#from flask_login import UserMixin

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
        'id' : self.userid,
        'username' : self.username,
        'email' : self.email
        }
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
    	return '<name - {}>'.format(self.username)