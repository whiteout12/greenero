from flask import Blueprint, request, jsonify, render_template, url_for
from flask_login import login_required, current_user
from fakk.forms import CreateInvoice, ChangeInvoice
from swish_qr_gen import swishQR, swishQRbase64
from flask_weasyprint import HTML, render_pdf
from fakk import mail
import io
from fakk import db
from fakk.models import User, Invoice

invoices_api = Blueprint('invoices_api', __name__)

#, url_prefix='/api'

@invoices_api.route('/claim')
@login_required
def claim():
	print('going to claim page')
	return render_template("claim.html", claim=True)

@invoices_api.route('/invoice/create-emb=<embedded>', methods=['GET', 'POST'])
@login_required
def createInvoice(embedded):
	print("invoice")
	form = CreateInvoice()
	#form.receiver.choices = [(g.frienduserid, User.query.filter_by(userid=g.frienduserid).first().username) for g in Relationship.query.filter_by(userid=current_user.userid, statusid=3).all()]
	#form.receiver.choices = [(g.frienduserid, g.rel_receiver.username) for g in current_user.get_friends()]
	choices = [(-1, 'Select receiver')]
	print(choices)
	for i in current_user.get_friends():
		choices.append((i.frienduserid, i.rel_receiver.username))
	#choices.append((g.frienduserid, g.rel_receiver.username) for g in current_user.get_friends())
	print(choices)
	form.receiver.choices = choices
	#form.receiver.choices = ([(g.frienduserid, g.rel_receiver.username) for g in current_user.get_friends()])
	if embedded=="false":
		emb=False
	else:
		emb=True
	#print("username: ", form.username.data)
	if form.validate_on_submit():
		invoice = Invoice(
			amount=form.amount.data,
			description=form.description.data,
			userid=current_user.userid,
			receiving_user=form.receiver.data
			
			)
		print(invoice)
		db.session.add(invoice)
		db.session.commit()
		print(form.receiver.data, form.description.data, form.amount.data)
		print({'message' : "Invoice sent"})
		return {'message' : "Invoice sent"}
	return render_template('invoice.html', form=form, embedded=emb)

@invoices_api.route('/invoice/change<invoice>', methods=['GET', 'POST'])
@login_required
def changeInvoice(invoice):

	form = ChangeInvoice()
	
	emb=True
	invoice_to_change=Invoice.query.filter_by(invoiceid=invoice).first()
	print(invoice_to_change)
	#print("username: ", form.username.data)
	if form.validate_on_submit():
		invoice_to_change.update(form.description.data, form.amount.data)
		print(invoice_to_change)
		#db.session.add(invoice)
		#db.session.commit()
		#print(form.receiver.data, form.description.data, form.amount.data)
		print({'message' : "Invoice changed"})
		return {'message' : "Invoice changed"}
	return render_template('invoice.html', form=form, embedded=emb, change=True, invoice=invoice_to_change)

@invoices_api.route('/invoices/renderpdf/<inv>')
@login_required
def renderpdf(inv):
	username=current_user.username
	invoice = getInvoice(inv).get_json()
	payee = User.query.filter_by(userid=invoice['invoice']['receiverid']).first()
	sender = User.query.filter_by(userid=invoice['invoice']['senderid']).first()
	#print('invoice_json: ', invoice)
	#print('payee: ', payee)
	#print('sender: ', sender)
	if(invoice['success']):
		

		swish_qr_base64=swishQRbase64(sender.phone, invoice['invoice']['amount'], invoice['invoice']['description'])
		print_html = render_template('invoice_pdf_template.html', username=sender.username, invoice=invoice['invoice'], qrCode_base64=swish_qr_base64, css1=url_for('static', filename='invoice_pdf/boilerplate.css'), css2=url_for('static', filename='invoice_pdf/main.css'), css3=url_for('static', filename='invoice_pdf/normalize.css'))
		
		
		return render_pdf(HTML(string=print_html), download_filename='invoice'+str(invoice['invoice']['invoiceid'])+'.pdf')
	else:

		return {'message' : invoice['message']}
	
@invoices_api.route('/invoices/email/<inv>')
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
			                  sender="bjorncarlsson87@gmail.com",
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

#TO BE MOVED TO API ROUTES

@invoices_api.route('/invoice/getinvoices')
@login_required
def getInvoices():
	print(current_user.userid)
	received = []
	sent = []
	
	for i in current_user.invoice_receiver:
		
		r = {
		'invoiceid' : i.invoiceid,
		'senderid' : i.userid,
		'sender' : i.sender.username,
		'description' : i.description,
		'amount' : i.amount,
		'invoicestatus' : i.statusid,
		'message' : i.message
		}
		#print(r)
		received.append(r)
	
	for i in current_user.invoice_sender:
		
		r = {
		'invoiceid' : i.invoiceid,
		'recieverid' : i.frienduserid,
		'receiver' : i.receiver.username,
		'description' : i.description,
		'amount' : i.amount,
		'invoicestatus' : i.statusid,
		'message' : i.message
		}
		
		sent.append(r)

	return jsonify({
		'received' : received,
		'sent' : sent
		})

@invoices_api.route('/invoice/getinvoice<invoiceid>')
@login_required
def getInvoice(invoiceid):

	print('currentuserID ', current_user.userid)
	print('invoiceid to look for ',invoiceid)
	
	invoice_to_get=Invoice.query.filter_by(invoiceid=invoiceid).first()
	
	if(invoice_to_get):
		if(invoice_to_get.userid==current_user.userid or invoice_to_get.frienduserid==current_user.userid):
			invoice = {
				'invoiceid' : invoice_to_get.invoiceid,
				'receiverid' : invoice_to_get.frienduserid,
				'receiver' : invoice_to_get.receiver.username,
				'description' : invoice_to_get.description,
				'amount' : invoice_to_get.amount,
				'invoicestatus' : invoice_to_get.statusid,
				'message' : invoice_to_get.message,
				'senderid' : invoice_to_get.userid,
				'sender' : invoice_to_get.sender.username,
				'duedate' : invoice_to_get.date_due,
				'createddate' : invoice_to_get.date_created,
				'version' : invoice_to_get.invoice_version
				}

			return jsonify({
					'success' : True,
					'invoice' : invoice
					})
		return jsonify({
		'success' : False,
		'message' : 'not authorized'
		})
	return jsonify({
		'success' : False,
		'message' : 'no invoice found'
		})


@invoices_api.route('/invoice/pay', methods=['GET', 'POST'])
@login_required
def payInvoice():

	if request.method == 'POST':
		data = request.get_json()
		print(data)
		Invoice.query.filter_by(invoiceid=data['InvoiceID']).first().change_status(2)

	

	return jsonify({
		'message' : 'invoice marked as payed'
		})

@invoices_api.route('/invoice/reject', methods=['GET', 'POST'])
@login_required
def rejectInvoice():

	if request.method == 'POST':
		data = request.get_json()
		print(data)
		invoice_to_reject=Invoice.query.filter_by(invoiceid=data['InvoiceID']).first()
		invoice_to_reject.reject(data['message'])
	

		return jsonify({
			'message' : 'invoice marked as rejected'
			})
	return {'message' : "No post in reject invoice"}	

@invoices_api.route('/invoice/remove', methods=['GET', 'POST'])
@login_required
def removeInvoice():
	print("invoice")

	if request.method == 'POST':
		data = request.get_json()

		invoice_to_delete=Invoice.query.filter_by(invoiceid=data['InvoiceID']).first()
		invoice_to_delete.delete()
		return {'message' : "invoice removed"}

	return {'message' : "No post in accept friend request"}	
