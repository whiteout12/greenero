from fakk import db, bcrypt
#from flask_login import UserMixin
from sqlalchemy import ForeignKey, func, DateTime
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship, backref
import secrets

# create user 
#class User(db.Model, UserMixin):
class User(db.Model):

    __tablename__ = "users"

    userid = db.Column(db.Integer, primary_key=True)
    usertype = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    phone = db.Column(db.String)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    username = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    confirmed_email = db.Column(db.Boolean, nullable=True)
    confirmed_email_on = db.Column(db.DateTime, nullable=True)
    confirmed_email_otp = db.Column(db.Integer, nullable=True)
    confirmed_phone = db.Column(db.Boolean, nullable=True)
    confirmed_phone_on = db.Column(db.DateTime, nullable=True)
    confirmed_phone_otp =db.Column(db.Integer, nullable=True)
    #posts = relationship("BlogPost", backref="author")
    friend_requester = db.relationship('Relationship', foreign_keys='Relationship.userid')
    friend_receiver = db.relationship('Relationship', foreign_keys='Relationship.frienduserid')
    invoice_sender = db.relationship('Invoice', foreign_keys='Invoice.userid')
    invoice_receiver = db.relationship('Invoice', foreign_keys='Invoice.frienduserid')

    bills = relationship('Bill', backref='payee')
    billdebts = relationship('BillDebt', backref='payer')
    billreceipts = relationship('Receipt', backref='owner')


    

    def __init__(self, username, password, usertype, credits):
        self.username = username
        #self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        #self.confirmed_email = False
        #self.confirmed_email_on = None
        #self.confirmed_phone = False
        #self.confirmed_phone_on = None
        self.usertype = usertype
        self.credits=credits
        

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.userid

    def get_friends(self):
        result = []
        for i in self.friend_requester:
            if i.statusid == 3:
                result.append(i)
        #return self.friend_requester.query.filter_by(statusid=3).all()
        return result
        #return self.query.(friend_requester).filter(statusid==3).all()


    def is_friend(self, frienduserid):
        for i in self.friend_requester:
            if i.frienduserid == frienduserid and i.statusid == 3:
                return True
            else:
                return False

    def get_username(self):
        return self.username

    def update(self, username, email, password, phone):
        if(username):
            self.username = username
        if(email):
            self.email = email
        else:
            self.email = None
            self.confirmed_email = None
            self.confirmed_email_on = None
        if(phone):
            self.phone = phone
        else:
            self.phone =  None
        if(password):
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
    def updatePassword(self, password):
        
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
    rel_sender = relationship('User', foreign_keys='Relationship.userid')
    rel_receiver = relationship('User', foreign_keys='Relationship.frienduserid')


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
        #return '<rel-friendshipid - {}>'.format(self.friendshipid)
        return 'Relationship(Id: %s, Sender: %s, Receiver: %s, Statusid: %s)' % (self.friendshipid, self.userid, self.frienduserid, self.statusid)

class Invoice(db.Model):

    __tablename__ = "invoices"

    invoiceid = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    description = db.Column(db.String)
    userid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    frienduserid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    statusid = db.Column(db.Integer, default=1)
    #invoice_date = db.Column(DateTime(timezone=True), server_default=func.now())
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(DateTime(timezone=True))
    date_due = db.Column(DateTime(timezone=True), default=func.now() + timedelta(days=7))
    #duedate = db.Column(db.Date)
    message = db.Column(db.String, default=None)
    invoice_version = db.Column(db.Integer, default=1)
    items = relationship('InvoiceItem', backref='invoice', cascade='all, delete')
    sender = relationship('User', foreign_keys='Invoice.userid')
    receiver = relationship('User', foreign_keys='Invoice.frienduserid')
    billdebtid = db.Column(db.Integer, ForeignKey('billdebts.billdebtid'))
    
    billdebt = relationship("BillDebt", back_populates="invoice")

    
    #billdebt = relationship('BillDebt', backref=backref("BillDebt", cascade="all, delete"))
    
    #__table_args__ = (db.UniqueConstraint('frienduserid', 'userid', name='_frienduserid_uc'), )
    #__table_args__ = (db.UniqueConstraint('receiving_user', 'requesting_user', name='_receiving_user_uc'), )
    #def __init__(self, userid, receiving_user, amount, description, billdebtid):
     #   self.userid = userid
      #  self.frienduserid = receiving_user
       # self.statusid = 1
        #self.amount = amount
        #self.invoice_version = 1
        #self.description = description
        #self.date_due = func.now() + timedelta(days=7)
        #self.billdebtid = billdebtid

    def update(self, description, amount):
        if(amount):
            self.amount = amount
        if(description):
            self.description = description
        self.invoice_version += 1
        self.statusid = 1
        self.message = None
        self.date_updated = func.now()
        db.session.commit()

    def get_id(self):
        return self.invoiceid

    def get_amount(self):
        return self.amount

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def reject(self, message):
        self.statusid = 3
        self.message = message
        db.session.commit()

    def change_status(self, status):
        self.statusid = status
        db.session.commit()


    def __repr__(self):
        #return '<rel-invoiceid - {}>'.format(self.invoiceid)
        return 'Invoice(Id: %s, Receiver: %s, amount: %s, description: %s, sender: %s, receiver: %s)' % (self.invoiceid, self.frienduserid, self.amount, self.description, self.sender, self.receiver)

class InvoiceItem(db.Model):

    __tablename__ = "invoiceitems"

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    description = db.Column(db.String)
    price = db.Column(db.Numeric, default=0)
    status = db.Column(db.Integer, default=1)
    type = db.Column(db.Integer, default=1)
    payed = db.Column(db.Boolean, nullable=True)
    
    
    invoiceid = db.Column(db.Integer, ForeignKey('invoices.invoiceid'))
    
    def __repr__(self):
        #return '<rel-invoiceid - {}>'.format(self.invoiceid)
        return 'InvoiceItem(Id: %s, Description: %s, price: %s, invoiceid: %s)' % (self.id, self.description, self.price, self.invoiceid)


class Bill(db.Model):

    __tablename__ = "bills"

    billid = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    
    
    payeeid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    statusid = db.Column(db.Integer, default=1)
    title = db.Column(db.String)
    amount_bill = db.Column(db.Numeric)
    amount_total = db.Column(db.Numeric)
    amount_payee = db.Column(db.Numeric, default=0)
    filefolder = db.Column(db.String, default=secrets.token_hex(8))
    token = db.Column(db.String)
    #amount_claimed = db.Column(db.Numeric)

    claims = relationship('BillDebt', backref='bill', cascade='all, delete')
    receipts = relationship('Receipt', backref='bill', cascade='all, delete')


    
        

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return 'Bill(Id: %s, Payee: %s, Payeeid: %s, Title: %s, Statusid: %s, Filefolder: %s)' % (self.billid, self.payee, self.payeeid, self.title, self.statusid, self.filefolder)

class BillDebt(db.Model):

    __tablename__ = "billdebts"

    billdebtid = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    statusid = db.Column(db.Integer, default=0)
    token = db.Column(db.String)
    payerid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    payer_screen_name = db.Column(db.String)
    
    amount_owed = db.Column(db.Numeric, default=0)
    sms = db.Column(db.Boolean, nullable=True)
    sms_attempts = db.Column(db.Integer, default=0)
    #invoice = relationship('Invoice', foreign_keys='Relationship.userid')
    
    billid = db.Column(db.Integer, ForeignKey('bills.billid'))
    #invoiceid = db.Column(db.Integer, ForeignKey('invoices.invoiceid'))
    #invoices = relationship('Invoice', backref='billdebt', cascade='all, delete')
    invoice = relationship("Invoice", uselist=False, back_populates="billdebt", cascade='all, delete')
    #invoice = relationship("Invoice", back_populates="invoices")
    #payer = relationship("User", back_populates="users")





    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return 'BillDebt(Id: %s, Payer: %s, Amount_owed: %s, Statusid: %s)' % (self.billdebtid, self.payerid, self.amount_owed, self.statusid)

class Receipt(db.Model):

    __tablename__ = "receipts"

    receiptid = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    statusid = db.Column(db.Integer)
    
    billid = db.Column(db.Integer, db.ForeignKey("bills.billid"), nullable=False)
    filename = db.Column(db.String)

    ownerid = db.Column(db.Integer, db.ForeignKey("users.userid"), nullable=False)
    


    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def __repr__(self):
        return 'Receipt(Id: %s, filename: %s, Ownerid: %s, Billid: %s)' % (self.receiptid, self.filename, self.ownerid, self.billid)