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
def createBill():
	shex = 1,2
	form = CreateBill()
	choices = []
	
	for i in current_user.get_friends():
		choices.append((i.frienduserid, i.rel_receiver.username))
	
	form.participants.choices = choices
	
	if form.validate_on_submit():
		#if form.receipt.data:

		#	shex = save_receipt(form.receipt.data)
		
		
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
		
		flash('Nota sparad!', category="success")
		return render_template('BillOverview.html', bill=bill)
	
	return render_template('createBill.html', form=form, img_url=shex, title='Skapa nota')

@bills.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):


    #return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder, filename))
    return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder), filename)
