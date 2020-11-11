from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash, send_from_directory
from flask_login import login_required, current_user
from fakk.forms import CreateBill, LobbyForm
#from swish_qr_gen import swishQR, swishQRbase64
from fakk.utils.swish_qr_gen import swishQR, swishQRbase64
from flask_weasyprint import HTML, render_pdf
from fakk import mail
import io, os
from fakk import db, mail, app
from fakk.models import User, Invoice, Bill, Receipt, BillDebt, InvoiceItem
import urllib.parse
import json
from fakk.utils.send_sms import sendSMS
from fakk.utils.tokens import load_invoice_token, generate_invoice_token
from flask_mail import Message
import secrets
from PIL import Image, ImageOps
from decimal import Decimal
from fakk.utils.tokens import generate_bill_token, load_bill_token, generate_billdebt_token, load_billdebt_token

bills = Blueprint('bills', __name__, url_prefix='/bills')




@bills.route('/', methods=['GET', 'POST'])
@login_required
def overviewBill():
	
	#bill = Bill(payee=current_user, amount_bill=23.45, amount_total=25.23, title='testbill')
	#print('bill', bill)
	#db.session.add(bill)
	#db.session.commit()
	#for bill in current_user.bills:
	
		#bill.delete()
	#	db.session.commit()
	

	#bills = Bill.query.all()
	#for bill in bills:
	#	bill.token = generate_bill_token(bill.billid)
	#	print('bill', bill)
	#	print('billtoken', bill.token)
	#	for debt in bill.claims:
	#		debt.token = generate_billdebt_token(debt.billdebtid)
	#		print('debt', debt)
	#		print('debttoken', debt.token)
	#db.session.commit()	
	##self, userid, receiving_user, amount, description
	#billdebt = BillDebt(payer=current_user, bill=bill)
	#db.session.add(billdebt)
	#db.session.commit()
	#invoice =Invoice(userid=current_user.userid, receiving_user=current_user.userid, amount=0, description=bill.title, billdebtid=billdebt.billdebtid)
	#db.session.add(invoice)
	#db.session.commit()
	#bills = current_user.bills	
	#billdebts = current_user.billdebts
	#invoices = current_user.invoice_receiver
	#print(bills)
	#print(billdebts)
	#print(invoices)
	return render_template('Bill_Overview_all.html', title='Notor')

@bills.route('/<billid>/view', methods=['GET', 'POST'])
@login_required
def oneBill(billid):
	bill=Bill.query.filter_by(billid=billid).first()
	if bill.payee == current_user:
		return render_template('BillOverview.html', bill=bill)
	else:
		return 'Not authorized'




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
		bill = createBill(form)
		print('bill', bill)
		participants = []
		for participantid in form.participants.data:
			participant = User.query.filter_by(userid=participantid).first()
			user = (participant, participant.username)
			participants.append(user)
		print('participants users to billdebt',participants)
		print('form phones',form.phones.data and form.sms_bool)
		print('sms bool form', form.sms_bool)
		if(form.phones.data and form.sms_bool.data):
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
		for participant in participants:
			billdebt = createBillDebt(bill, participant)
			print(billdebt)
		flash('Nota skapad', category='success')
		return redirect(url_for('bills.oneBill', billid=bill.billid))
		

	print('names',form.names.data)
	print('names errors',form.names.errors)
	print(form.phones.data)
	return render_template('createBill.html', form=form, img_url=shex, title='Skapa nota')

@bills.route('/update', methods=['GET', 'POST'])
@login_required
def updateBillForm():

	return

def createBill(form):

	bill = Bill(payee=current_user, amount_bill=form.amount.data, amount_total=form.totalamount.data, title=form.description.data)
	db.session.add(bill)
	db.session.commit()
	bill.token = generate_bill_token(bill.billid)
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
	db.session.commit()
	return newdummyuser

def createDebtUser(username):
	newddebtuser = User(username=username, password='dummy', usertype=3, credits=None)
	db.session.add(newddebtuser)
	db.session.commit()
	return newddebtuser

def createBillDebt(bill, participant):
		billdebt = BillDebt(payer=participant[0], bill=bill, payer_screen_name=participant[1])
		db.session.add(billdebt)
		db.session.commit()
		billdebt.token = generate_billdebt_token(billdebt.billdebtid)
		db.session.commit()
		invoice = createInvoice(billdebt)

		return billdebt

def createInvoice(billdebt):
	invoice =Invoice(userid=billdebt.bill.payee.userid, frienduserid=billdebt.payer.userid, amount=0, description=billdebt.bill.title, billdebtid=billdebt.billdebtid)
	db.session.add(invoice)
	db.session.commit()

	return invoice

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

def delete_receipt(path):
	return

def delete_receipts(bill):
	
	
	receipt_path = os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], bill.filefolder)
	#path = '/Users/bjorncarlsson/Python/fakk-images'
	#print('folder list', os.listdir(receipt_path))
	#print(len(os.listdir(receipt_path)))
	for receipt in bill.receipts:
		if os.path.exists(os.path.join(receipt_path, receipt.filename)):
 			 os.remove(os.path.join(receipt_path, receipt.filename))
 			 print("The file was removed: ", os.path.join(receipt_path, receipt.filename))
		else:
  			print("The file does not exist")

	#removing folder if empty
	if len(os.listdir(receipt_path)) == 0:
		print(receipt_path)
		print(len(receipt_path))

		print("Empty directory")
		os.rmdir(receipt_path)
	else:
		print(receipt_path)
		print(len(receipt_path))
		print("Not empty directory")

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

@bills.route('/<billid>/publish', methods=['GET', 'POST'])
@login_required
def publishBill(billid):

	if request.method == 'POST':
		bill = Bill.query.filter_by(billid=billid).first()
		bill.statusid = 2
		db.session.commit()
	return redirect(url_for('bills.oneBill', billid=billid))

@bills.route('/<billid>/close', methods=['GET', 'POST'])
@login_required
def closeBill(billid):

	if request.method == 'POST':
		bill = Bill.query.filter_by(billid=billid).first()
		bill.statusid = 3
		db.session.commit()
	return redirect(url_for('bills.oneBill', billid=billid))

@bills.route('/<billid>/delete', methods=['GET', 'POST'])
@login_required
def deleteBill(billid):

	if request.method == 'POST':
		bill = Bill.query.filter_by(billid=billid).first()
		#delete_receipts(bill)
		users_to_be_deleted = []
		for claim in bill.claims:
			if claim.payer.usertype == 3:
				users_to_be_deleted.append(claim.payer.userid)
				print('delete user', claim.payer)
				#claim.payer.delete()

		bill.delete()
		for userid in users_to_be_deleted:
			User.query.filter_by(userid=userid).first().delete()
	return redirect(url_for('bills.overviewBill'))

@bills.route('/<billid>/update', methods=['GET', 'POST'])
@login_required
def updateBill(billid):
	print(request.form)
	new_amount_payee = request.form['amount_payee'].replace(',','.')
	new_amount_bill = request.form['amount_bill'].replace(',','.')
	new_amount_total = request.form['amount_total'].replace(',','.')
	print('new_amount_payee',new_amount_payee)

	if request.method == 'POST':
		bill=Bill.query.filter_by(billid=billid).first()
		print('comapre share', str(bill.amount_payee) != str(new_amount_payee))
		print(bill.amount_payee)
		print(new_amount_payee)

		if str(bill.amount_payee) != str(new_amount_payee):
			bill.amount_payee = new_amount_payee
			flash('Uppdaterade din del till ' + request.form['amount_payee']+'kr', category='success')
		if str(bill.amount_bill) != str(new_amount_bill):
			bill.amount_bill = new_amount_bill
			flash('Uppdaterade notabelopp till ' + request.form['amount_bill']+'kr', category='success')
		if str(bill.amount_total) != str(new_amount_total):
			bill.amount_total = new_amount_total
			flash('Uppdaterade totalbelopp till ' + request.form['amount_total']+'kr', category='success')
		db.session.commit()
		for debt in bill.claims:
			if len(debt.invoice.items)>0:
				for item in debt.invoice.items:

					if item.type == 2:
						share = item.price 
				for item in debt.invoice.items:	
					if item.type == 3:
						service_fee = share*((bill.amount_total/bill.amount_bill)-1)
						item.price = service_fee
						db.session.commit()
		#flash('Uppdaterade din del till ' + request.form['amount_total']+'kr', category='success')

	return redirect(url_for('bills.oneBill', billid=billid))

@bills.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):


    #return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder, filename))
    return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder), filename)

@bills.route('/debt/<billdebtToken>/view', methods=['GET', 'POST'])
#@login_required
def oneDebt(billdebtToken):
	try:
		billdebtid = load_billdebt_token(billdebtToken)
		print('billdebid' ,billdebtid)
	except:
		flash('Länken ej gilitg.', category='danger')
		return 'Länken ej gilitg.'
	
	else:
		debt=BillDebt.query.filter_by(billdebtid=billdebtid).first()
		print(debt.bill)
		#if debt.payer == current_user and debt.bill.statusid==2:
		#	return render_template('DebtOverview.html', bill=bill)
		return render_template('DebtOverview.html', debt=debt)
		#else:
		#	return 'Not authorized'

@bills.route('/debt/<billdebtToken>/updateMyShare', methods=['GET', 'POST'])
#@login_required
def updateDebt_MyShare(billdebtToken):
	try:
		billdebtid = load_billdebt_token(billdebtToken)
	except:
		flash('Länken ej gilitg.', category='danger')
		return redirect(url_for('send-password-reset-link'))
	
	else:	
		print(request.form)
		new_amount = request.form['myshare']
		print(new_amount)
		new_amount = Decimal(new_amount.replace(',','.'))
		
		if request.method == 'POST':
			billdebt = BillDebt.query.filter_by(billdebtid=billdebtid).first()
			print('tips', billdebt.bill.amount_total/billdebt.bill.amount_bill)
			service_fee = new_amount*((billdebt.bill.amount_total/billdebt.bill.amount_bill)-1)
			print('service_fee ', service_fee)
			billdebt.amount_owed = new_amount
			db.session.commit()
			service = 0
			amount = 0
			if len(billdebt.invoice.items)>0:
				for item in billdebt.invoice.items:
					if item.type == 2:
						item.price = new_amount
						db.session.commit()
					if item.type == 3:
						item.price = service_fee
						db.session.commit()

			else:
				invoiceitem_amount = InvoiceItem(description='Andelskostnad', type=2, price=new_amount, invoice=billdebt.invoice, payed=False)
				invoiceitem_service = InvoiceItem(description='Servicekostnad', type=3, price=service_fee, invoice=billdebt.invoice, payed=False)
				print('invoiceitem_amount', invoiceitem_amount)
				#print('invoiceitem_service', invoiceitem_service)
				db.session.add(invoiceitem_amount)
				db.session.add(invoiceitem_service)

				#db.session.add_all([invoiceitem_amount, invoiceitem_service])
				db.session.commit()
			flash('Uppdaterade din del till ' + request.form['myshare']+'kr', category='success')

		return redirect(url_for('bills.oneDebt', billdebtToken=billdebt.token))

@bills.route('/lobby/<billToken>', methods=['GET', 'POST'])
#@login_required
def billLobby(billToken):
	try:
		billid = load_bill_token(billToken)
		print('billid', billid)
		if billid == False:
			raise ValueError
	except ValueError:
		
			flash('Länken ej gilitg.', category='danger')
			return render_template('billNotFound.html', title='404 ogilting länk')
	
	else:

		print('newuser?')
		if not Bill.query.filter_by(billid=billid).first():
			return render_template('billNotFound.html', title='404 inget här')
		bill=Bill.query.filter_by(billid=billid).first()
		
			
		form = LobbyForm()
		print(form.nickname.data)
		if form.validate_on_submit():
			print('creating new participant')
			newuser = createDebtUser(form.nickname.data)
			user = (newuser, newuser.username)
			
			billdebt = createBillDebt(bill, user)
			print(billdebt.token)
			print(billdebt)
			return redirect(url_for('bills.oneDebt', billdebtToken=billdebt.token))

		return render_template('billLobby.html', form=form, bill=bill, title='Dela kostnad för '+bill.title, lobbylink=True)	
