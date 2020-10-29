from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash, send_from_directory
from flask_login import login_required, current_user
from fakk.forms import CreateBill
#from swish_qr_gen import swishQR, swishQRbase64
from fakk.utils.swish_qr_gen import swishQR, swishQRbase64
from flask_weasyprint import HTML, render_pdf
from fakk import mail
import io, os
from fakk import db, mail, app
from fakk.models import User, Invoice
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
	
	return render_template('BillOverview.html', title='Notor')

def save_receipt(form_receipt):
	random_filename = secrets.token_hex(8)
	random_foldername = secrets.token_hex(8)
	#f_name
	_, f_ext = os.path.splitext(form_receipt.filename)
	receipt_fn = random_filename + f_ext
	receipt_path = os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], random_foldername)
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
	return random_foldername, receipt_fn


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
		if form.receipt.data:

			shex = save_receipt(form.receipt.data)
		flash('allt ifyllt korrektn!', category="success")
		flash('Skickar nota till:', category="success")
		if form.sms_bool.data:
			flash(form.phones.data, category="success")
		if form.contact_bool.data:
			flash(form.participants.data, category="success")
		flash('Summa: ' + str(form.amount.data), category="success")
		flash('Totalsumma: ' + str(form.totalamount.data), category="success")
		
	
	return render_template('createBill.html', form=form, img_url=shex, title='Skapa nota')

@bills.route('/uploads/<folder>/<filename>')
def uploaded_file(folder, filename):


    #return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder, filename))
    return send_from_directory(os.path.join(app.config['RECEIPT_UPLOAD_FOLDER'], folder), filename)
