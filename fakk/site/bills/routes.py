from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash, send_from_directory
from flask_login import login_required, current_user
from fakk.forms import CreateBill
#from swish_qr_gen import swishQR, swishQRbase64
from fakk.utils.swish_qr_gen import swishQR, swishQRbase64
from flask_weasyprint import HTML, render_pdf
from fakk import mail
import io, os
from fakk import db, mail, app
from fakk.models import User, Invoice, Bill, Receipt, BillDebt
import urllib.parse
import json
from fakk.utils.send_sms import sendSMS
from fakk.utils.tokens import load_invoice_token, generate_invoice_token
from flask_mail import Message
import secrets
from PIL import Image, ImageOps

bills = Blueprint('bills', __name__, url_prefix='/site/bill')




@bills.route('/', methods=['GET', 'POST'])
@login_required
def overviewBill():
	
	#bill = Bill(payee=current_user, amount_bill=23.45, amount_total=25.23, title='testbill')
	#print('bill', bill)
	#db.session.add(bill)
	#db.session.commit()
	#for bill in current_user.bills:
	#	bill.delete()
	#	db.session.commit()
	##self, userid, receiving_user, amount, description
	#billdebt = BillDebt(payer=current_user, bill=bill)
	#db.session.add(billdebt)
	#db.session.commit()
	#invoice =Invoice(userid=current_user.userid, receiving_user=current_user.userid, amount=0, description=bill.title, billdebtid=billdebt.billdebtid)
	#db.session.add(invoice)
	#db.session.commit()
	bills = current_user.bills	
	billdebts = current_user.billdebts
	invoices = current_user.invoice_receiver
	print(bills)
	print(billdebts)
	print(invoices)
	return render_template('Bill_Overview_all.html')

@bills.route('/<billid>/view', methods=['GET', 'POST'])
@login_required
def oneBill(billid):
	bill=Bill.query.filter_by(billid=billid).first()
	if bill.payee == current_user:
		return render_template('BillOverview.html', bill=bill)
	else:
		return 'Not authorized'

def save_receipt(form_receipt, folder):
	random_filename = secrets.token_hex(8)
	random_foldername = secrets.token_hex(8)
	#f_name
	_, f_ext = os.path.splitext(form_receipt.filename)
	receipt_fn = random_filename + f_ext
	receipt_path = os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder)
	#path = '/Users/bjorncarlsson/Python/fakk-images'
	if not os.path.isdir(receipt_path):
		print('skapar dir: ', receipt_path)
		os.mkdir(receipt_path)

	filepath =os.path.join(receipt_path, receipt_fn)
	output_size = (1000,1000)
	i = Image.open(form_receipt)
	i.thumbnail(output_size)
	i = ImageOps.exif_transpose(i)
	#i.rotate(270)

	#form_receipt.save(filepath)
	i.save(filepath)
	#return 'Receipt sparat som '+receipt_fn+' i '+receipt_path
	return receipt_fn


@bills.route('/create', methods=['GET', 'POST'])
@login_required
def createBillForm():

	shex = 1,2
	form = CreateBill()
	choices = []
	
	for i in current_user.get_friends():
		choices.append((i.rel_receiver.userid, i.rel_receiver.username))
	
	form.participants.choices = choices
	print(form.participants.choices)
	if request.method == 'POST':
		print(form.names.data)
		print(form.phones.data)
		print('participants post', form.participants.data)

	if form.validate_on_submit():
		#if form.receipt.data:
		
			
		#create bill
		#bill = createBill(form)
		participants = []
		for participantid in form.participants.data:
			participant = User.query.filter_by(userid=participantid).first()
			user = (participant, participant.username)
			participants.append(user)
		print('participants users to billdebt',participants)
		if(form.phones.data):
			phone_partcipants = []
			for i in range(len(form.phones)):
				user = (form.names[i].data, form.phones[i].data)
				phone_partcipants.append(user)
		print('phone_partcipants', phone_partcipants)
		for item in phone_partcipants:
			user = (getUser(item[1]), item[0])
			participants.append(user)
		print('participants users to billdebt with phonesusers',participants)
		#store receipt
			#shex = save_receipt(form.receipt.data)
		#check users
			#create users
		#create billdebt
		
		flash('skickad!')
		return "done"
		#return render_template('BillOverview.html', title='Skicka nota?')
		

	print('names',form.names.data)
	print('names errors',form.names.errors)
	print(form.phones.data)
	return render_template('createBill.html', form=form, img_url=shex, title='Skapa nota')



def createBill():

	bill = Bill(payee=current_user, amount_bill=form.amount.data, amount_total=form.totalamount.data, title=form.description.data)
	db.session.add(bill)
	db.session.commit()
	if form.receipt.data:
		shex = save_receipt(form.receipt.data, bill.filefolder)
		receipt = Receipt(owner=current_user, bill=bill, filename=shex, statusid=1)
		db.session.add(receipt)
		db.session.commit()
	return bill

def getUser(phone):
	confirmed_user = User.query.filter_by(phone=phone, confirmed_phone=True).first()
	if confirmed_user:
		return confirmed_user
	existing_dummy_user = User.query.filter_by(usertype=1, phone=phone).first()
	if existing_dummy_user:
		return existing_dummy_user
	newdummyuser = User(
				username=None,
				#email=form.email.data,
				password='dummy',
				usertype=1,
				credits=None 
				)
	db.session.add(newdummyuser)
	#db.session.commit()
	return newdummyuser

def createDummyUser():
	return

def createBillDebt(bill, participants):

	for participant in participants:
		billdebt = BillDebt(payer=participant[0], bill=bill, payer_screen_name=participant[1])
		db.session.add(billdebt)
		db.session.commit()
		createInvoice(billdebt)

	return billdebt

def createInvoice(billdebt):
	invoice =Invoice(userid=billdebt.bill.payee, frienduserid=billdebt.payer, amount=0, description=billdebt.bill.title, billdebtid=billdebt.billdebtid)
	db.session.add(invoice)
	db.session.commit()

	return


@bills.route('/<billid>/send', methods=['GET', 'POST'])
@login_required
def saveBill(billid):
	bill = Bill(payee=current_user, amount_bill=form.amount.data, amount_total=form.totalamount.data, title=form.description.data)
	db.session.add(bill)
	db.session.commit()
	if form.receipt.data:
		shex = save_receipt(form.receipt.data, bill.filefolder)
		receipt = Receipt(owner=current_user, bill=bill, filename=shex, statusid=1)
		db.session.add(receipt)
		db.session.commit()
	for contact in form.participants.data:
		billdebt = BillDebt(payer=User.query.filter_by(userid=contact).first(), bill=bill)
		db.session.add(billdebt)
		db.session.commit()
		invoice =Invoice(userid=current_user.userid, frienduserid=contact, amount=0, description=form.description.data, billdebtid=billdebt.billdebtid)
		db.session.add(invoice)
		db.session.commit()
	return render_template('createBill.html', form=form, title='Ändra nota')

@bills.route('/<billid>/change', methods=['GET', 'POST'])
@login_required
def changeBill(billid):
	form = CreateBill()
	bill = Bill.query.filter_by(billid=billid).first()

	if request.method == 'GET':
		choices = []
		already_chosen = []
		for claim in bill.claims:
			already_chosen.append(claim.payer.userid)
		if len(already_chosen) > 0:
			form.contact_bool.data = True
		for i in current_user.get_friends():
			choices.append((i.frienduserid, i.rel_receiver.username))
		print(choices)
		form.participants.choices = choices
		form.description.data = bill.title
		form.totalamount.data = bill.amount_total
		form.amount.data = bill.amount_bill
	if form.validate_on_submit():
		return 'hej'
	print(form.participants.choices)
	form.participants.data = already_chosen
	return render_template('createBill.html', form=form, title='Ändra nota')

@bills.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):


    #return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder, filename))
    return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder), filename)
