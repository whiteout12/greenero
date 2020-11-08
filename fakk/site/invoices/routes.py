from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash
from flask_login import login_required, current_user
from fakk.forms import CreateInvoice, ChangeInvoice
#from swish_qr_gen import swishQR, swishQRbase64
from fakk.utils.swish_qr_gen import swishQR, swishQRbase64
from flask_weasyprint import HTML, render_pdf
from fakk import mail
import io
from fakk import db, mail
from fakk.models import User, Invoice
import urllib.parse
import json
from fakk.utils.send_sms import sendSMS
from fakk.utils.tokens import load_invoice_token, generate_invoice_token
from flask_mail import Message


invoices = Blueprint('invoices', __name__, url_prefix='/site/invoice')

#, url_prefix='/site'


@invoices.route('/create-emb=<embedded>', methods=['GET', 'POST'])
@login_required
def createInvoice(embedded):
	
	form = CreateInvoice()

	choices = [(-1, 'Välj mottagare')]
	
	for i in current_user.get_friends():
		choices.append((i.frienduserid, i.rel_receiver.username))
	
	form.receiver.choices = choices
	#print(choices)
	if embedded=="False":
		emb=False
	else:
		emb=True
	#print("username: ", form.username.data)
	if form.validate_on_submit():
		
		if form.inv_type.data == 1:
			invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=form.receiver.data
				
				)
			#print(invoice)

			db.session.add(invoice)
			db.session.commit()
			#print(invoice.invoiceid)
			
			flash('Faktura skickad till '+invoice.receiver.username+'!', category='success')
		elif form.inv_type.data == 2:

			is_user_with_email = User.query.filter_by(email=form.email.data, confirmed_email=True).first()
			print(is_user_with_email)
			if(is_user_with_email):
				print('hittade riktig användare')
				invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=is_user_with_email.userid
				)
				print(invoice)

				db.session.add(invoice)
				db.session.commit()
				#print(invoice.invoiceid)
				print(current_user.credits)
				current_user.credits -= 2
				db.session.commit()
				print(current_user.credits)
				package_locked = generate_invoice_token(form.receiver.data, invoice.invoiceid)
				flash('Faktura skickad till '+form.email.data+'!', category='success')

			elif User.query.filter_by(usertype=1, email=form.email.data).first():
				#print('hittade dummy användare')
				dummyuser = User.query.filter_by(usertype=1, email=form.email.data).first()
				invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=dummyuser.userid
				
				)
				#print(invoice)

				db.session.add(invoice)
				db.session.commit()
				#print(invoice.invoiceid)
				print(current_user.credits)
				current_user.credits -= 2
				db.session.commit()
				print(current_user.credits)
				package_locked = generate_invoice_token(form.receiver.data, invoice.invoiceid)
				flash('Faktura skickad till '+form.email.data+'!', category='success')

			else:
				print('skapar ny dummy användare')
				newdummyuser = User(
				username=None,
				#email=form.email.data,
				password='dummy',
				usertype=1,
				credits=None 
				)
				db.session.add(newdummyuser)
				db.session.commit()
				newdummyuser.email = form.email.data
				db.session.commit()

				invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=newdummyuser.userid
				
				)
				#print(invoice)

				db.session.add(invoice)
				db.session.commit()
				#print(invoice.invoiceid)
				print(current_user.credits)
				current_user.credits -= 2
				db.session.commit()
				print(current_user.credits)
				package_locked = generate_invoice_token(form.receiver.data, invoice.invoiceid)
				flash('Faktura skickad till '+form.email.data+'!', category='success')
			#send email
			username=current_user.username
			#swish_qr_base64=swishQRbase64(sender.phone, invoice['invoice']['amount'], invoice['invoice']['description'])
			#htmlpdf = HTML(string=render_template('invoice_pdf_template.html', username=sender.username, invoice=invoice['invoice'], qrCode_base64=swish_qr_base64, css1=url_for('static', filename='invoice_pdf/boilerplate.css'), css2=url_for('static', filename='invoice_pdf/main.css'), css3=url_for('static', filename='invoice_pdf/normalize.css')))
			confirm_url = url_for('main.invoice_site', invoice_token=package_locked, _external=True)
			#pdf = io.BytesIO(htmlpdf.write_pdf())
			html = render_template('email_invoice.html', invoice_url=confirm_url, payee=current_user.email)
			
			msg = Message("Du har blivit fakkad :)",
		                  sender=('fakk.', 'faktura@fakk.tech'),
		                  recipients=[form.email.data])
			msg.body = "Du har blivit fakkad, se bifogat " + confirm_url
			msg.html = html
			#msg.attach('invoice.pdf', 'application/pdf', data=pdf.read())
			mail.send(msg)	
			#flash('Faktura skickad till '+ form.email.data, category='success')
		elif form.inv_type.data == 3:

			is_user_with_phone = User.query.filter_by(phone=form.phone.data, confirmed_phone=True).first()
			#print(is_user_with_phone)
			if(is_user_with_phone):
				invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=is_user_with_phone.userid
				
				)
				#print(invoice)

				db.session.add(invoice)
				db.session.commit()
				#print(invoice.invoiceid)
				#Skicka SMS
				package_locked = generate_invoice_token(form.receiver.data, invoice.invoiceid)
				

			elif User.query.filter_by(usertype=1, phone=form.phone.data).first():
				dummyuser = User.query.filter_by(usertype=1, phone=form.phone.data).first()
				invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=dummyuser.userid
				
				)
				#print(invoice)

				db.session.add(invoice)
				db.session.commit()
				#print(invoice.invoiceid)
				package_locked = generate_invoice_token(form.receiver.data, invoice.invoiceid)

			else:

				newdummyuser = User(
				username=None,
				#email=form.email.data,
				password='dummy',
				usertype=1,
				credits=None 
				)
				db.session.add(newdummyuser)
				db.session.commit()
				newdummyuser.phone = form.phone.data
				db.session.commit()

				invoice = Invoice(
				amount=form.amount.data,
				description=form.description.data,
				userid=current_user.userid,
				frienduserid=newdummyuser.userid
				
				)
				#print(invoice)

				db.session.add(invoice)
				db.session.commit()
				#print(invoice.invoiceid)
				package_locked = generate_invoice_token(form.receiver.data, invoice.invoiceid)

			confirm_url = url_for('main.invoice_site', invoice_token=package_locked, _external=True)
			message = 'Du har fått en faktura av ' + current_user.phone + ' ' + confirm_url
			#flash('Faktura skickad!', category='success')
			sms_status = sendSMS(form.phone.data, message)
			#print('sms_status', sms_status)
			current_user.credits -= 5
			db.session.commit()
			flash('Faktura skickad till ' +str(form.phone.data), category='success')
			#flash('Faktura skickad till '+ form.phone.data, category='success')
		if emb:
			return {'message' : "Invoice sent"}
		else:
			return redirect(url_for('invoices.getAll'))

	#print(emb)
	
	return render_template('invoice.html', form=form, embedded=emb)



@invoices.route('/getall')
@login_required
def getAll():
	#print(current_user.invoice_receiver)
	
	final_list = []

	received=current_user.invoice_receiver
	sent=current_user.invoice_sender
	inv_open = []
	inv_closed = []
	inv_rejected = []
	for i in received:
		
		#print('received',i.statusid)
		if i.statusid == 1:
			inv_open.append(i)
		if i.statusid == 2:
			inv_closed.append(i)
		if i.statusid == 3:
			inv_rejected.append(i)
	received2 = {
		'inv_open' : inv_open,
		'inv_closed' : inv_closed,
		'inv_rejected' : inv_rejected
		}
	inv_open = []
	inv_closed = []
	inv_rejected = []
	for i in sent:
		#print(i.statusid)
		if i.statusid == 1:
			inv_open.append(i)
		if i.statusid == 2:
			inv_closed.append(i)
		if i.statusid == 3:
			inv_rejected.append(i)
	sent2 = {
		'inv_open' : inv_open,
		'inv_closed' : inv_closed,
		'inv_rejected' : inv_rejected
		}
	#print(received2)
	#print(sent2)

	swishjson = {
 		'version':1,
		'payee':{
  			'value':''
			},
		'amount':{
			'value':200,
			'editable': False
			},
		'message':{
			'value':'Hälsningar the King',
			'editable' : False
			}
		}

	#tesjson = {"version":1,"payee":{"value":"0730514018"},"message":{"value":"fakturaID, Description", 'editable' : False}, "amount":{"value":200, 'editable' : False}}
	#import json
	#params_json2 = json.dumps(tesjson, indent=None)
	#import urllib.parse
	#result3 = urllib.parse.quote(params_json2, encoding='utf-8')
	#print('url', result3)

	#return render_template('invoices.html', title='Fakturor',received=current_user.invoice_receiver, sent=current_user.invoice_sender)
	return render_template('invoices.html', title='Fakturor',received=received2, sent=sent2)

@invoices.route('/<invoice_id>/view')
@login_required
def view_invoice_site(invoice_id):
	
	invoice = Invoice.query.filter_by(invoiceid=invoice_id).first()
	swish_qr_base64=swishQRbase64(invoice.sender.phone, invoice.amount, invoice.description)
	print(swish_qr_base64)

	return render_template('invoice2.html', title='Fakturor',invoice=invoice, qr_code=swish_qr_base64)

@invoices.route('/<invoice_token>/')

def view_open_invoice_site(invoice_token):
	
	package = load_invoice_token(invoice_token)
	print(package)
	
	invoice = Invoice.query.filter_by(invoiceid=package[1]).first()
	if not invoice:
		return "ingen faktura hittad."
	
	swish_qr_base64=swishQRbase64(invoice.sender.phone, invoice.amount, invoice.description)
	#print(swish_qr_base64)

	#return render_template('invoice2.html', title='Fakturor',invoice=invoice, qr_code=swish_qr_base64)
	return render_template('view_invoice.html', title='Faktura',invoice=invoice, qr_code=swish_qr_base64)

@invoices.route('/<invoice_id>/pay', methods=['GET', 'POST'])
@login_required
def payInvoice_site(invoice_id):

	Invoice.query.filter_by(invoiceid=invoice_id).first().change_status(2)
	flash('Fakturan är markerad som betald', category='success')
	
	return redirect(url_for('invoices.view_invoice_site', invoice_id=invoice_id))

@invoices.route('/<invoice_id>/reject', methods=['GET', 'POST'])
@login_required
def rejectInvoice_site(invoice_id):
	if request.method == 'POST':
		reason = request.form['reason']
		print(reason)
		invoice_to_reject=Invoice.query.filter_by(invoiceid=invoice_id).first()
		invoice_to_reject.reject(reason)
		flash('Fakturan tillbakaskickad!', category='success')
	return redirect(url_for('invoices.getAll'))

@invoices.route('/<invoice_id>/remove', methods=['GET', 'POST'])
@login_required
def removeInvoice_site(invoice_id):
	print("invoice")

	if request.method == 'POST':
		invoice_to_delete=Invoice.query.filter_by(invoiceid=invoice_id).first()
		invoice_to_delete.delete()
		flash('Fakturan raderad!', category='success')
		

	return redirect(url_for('invoices.getAll'))

@invoices.route('/<invoice_id>/change', methods=['GET', 'POST'])
@login_required
def changeInvoice_site(invoice_id):

	form = ChangeInvoice()

	
	emb=False
	invoice_to_change=Invoice.query.filter_by(invoiceid=invoice_id).first()
	from_rejected=invoice_to_change.statusid
	print(invoice_to_change)
	#print("username: ", form.username.data)
	if request.method == 'GET':
		form.description.data=invoice_to_change.description
	if form.validate_on_submit():
		if invoice_to_change.description == form.description.data and invoice_to_change.amount == form.amount.data:
			flash('Ingen ändring gjord', category='warning')
		else:
			invoice_to_change.update(form.description.data, form.amount.data)
			print(invoice_to_change)
			#db.session.add(invoice)
			#db.session.commit()
			#print(form.receiver.data, form.description.data, form.amount.data)
			if from_rejected == 3:
				flash('Fakturan uppdaterad och skickad!', category='success')
			else:	
				flash('Fakturan uppdaterad!', category='success')
		return redirect(url_for('invoices.getAll'))
	return render_template('invoice.html', form=form, embedded=emb, change=True, invoice=invoice_to_change)


@invoices.route('/pdf/<inv>')
@login_required
def renderpdf(inv):
	username=current_user.username
	invoice = Invoice.query.filter_by(invoiceid=inv).first()
	payee = User.query.filter_by(userid=invoice.frienduserid).first()
	sender = User.query.filter_by(userid=invoice.userid).first()
	#print('invoice_json: ', invoice)
	#print('payee: ', payee)
	#print('sender: ', sender)
	
		

	swish_qr_base64=swishQRbase64(sender.phone, invoice.amount, invoice.description)
	print_html = render_template('invoice_pdf_template.html', username=sender.username, invoice=invoice, qrCode_base64=swish_qr_base64, css1=url_for('static', filename='invoice_pdf/boilerplate.css'), css2=url_for('static', filename='invoice_pdf/main.css'), css3=url_for('static', filename='invoice_pdf/normalize.css'))
		
		
	return render_pdf(HTML(string=print_html), download_filename='invoice'+str(invoice.invoiceid)+'.pdf')
	
	
@invoices.route('/email/<inv>')
@login_required
def email_invoice(inv):
	print(current_user.userid)
	print(inv)
	invoice = getInvoice(inv).get_json()
	if(invoice['success']):
		payee = User.query.filter_by(userid=invoice['invoice']['receiverid']).first()
		sender = User.query.filter_by(userid=invoice['invoice']['senderid']).first()

		if payee.email:
			print('payee email: ', payee.email)
			if current_user.phone:
				
				username=current_user.username
				swish_qr_base64=swishQRbase64(sender.phone, invoice['invoice']['amount'], invoice['invoice']['description'])
				html = HTML(string=render_template('invoice_pdf_template.html', username=sender.username, invoice=invoice['invoice'], qrCode_base64=swish_qr_base64, css1=url_for('static', filename='invoice_pdf/boilerplate.css'), css2=url_for('static', filename='invoice_pdf/main.css'), css3=url_for('static', filename='invoice_pdf/normalize.css')))
				pdf = io.BytesIO(html.write_pdf())
				msg = Message("Du har blivit fakkad :)",
			                  sender=('fakk.', 'faktura@fakk.tech'),
			                  recipients=[payee.email])
				msg.body = "Du har blivit fakkad, se bifogat" 
				msg.attach('invoice.pdf', 'application/pdf', data=pdf.read())
				mail.send(msg)
				return {'message' : "Email sent!"}
			else:
				return {'message' : "You have no phone number registred which is needed to genarate swish QRcode :("}
		else:
			return {'message' : "Payee has no email address registered :("}
	else:

		return {'message' : invoice['message']}	

@invoices.route('/swish/<invoice_token>/res')
def test_callback(invoice_token):
	print(invoice_token)
	result_raw = request.args.get('res', None)
	
	result = json.loads(result_raw)
	print('invoice_token', invoice_token)
	print(result['result'])
	if result['result']=='paid':
		print('will be paid')
		invoice_to_pay = Invoice.query.filter_by(invoiceid=invoice_token).first()
		print(invoice_to_pay)
		invoice_to_pay.change_status(2)
		flash('Fakturan är markerad som betald', category='success')
		return redirect(url_for('invoices.result_payment'), success=True)
	#return render_template('swishcallback.html', token=invoice_token, callback=result['result'])
	else:

		return redirect(url_for('invoices.result_payment'), success=False)

@invoices.route('/swish/callback/')
def result_payment(success):

	return render_template('swishcallback.html', success=success)




