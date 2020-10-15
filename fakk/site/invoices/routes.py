from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash
from flask_login import login_required, current_user
from fakk.forms import CreateInvoice, ChangeInvoice
#from swish_qr_gen import swishQR, swishQRbase64
from fakk.utils.swish_qr_gen import swishQR, swishQRbase64
from flask_weasyprint import HTML, render_pdf
from fakk import mail
import io
from fakk import db
from fakk.models import User, Invoice
import urllib.parse
import json

invoices = Blueprint('invoices', __name__, url_prefix='/site/invoice')

#, url_prefix='/site'


@invoices.route('/create-emb=<embedded>', methods=['GET', 'POST'])
@login_required
def createInvoice(embedded):
	print("invoice")
	print(embedded)
	#from fakk import db
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
	if embedded=="False":
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
		print(emb)
		if emb:
			return {'message' : "Invoice sent"}
		else:
			return redirect(url_for('invoices.getAll'))
	
	print(emb)
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
		
		print('received',i.statusid)
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
		print(i.statusid)
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
  			'value':'0730514019'
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
	if form.validate_on_submit():
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


@invoices.route('/renderpdf/<inv>')
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

	#return render_template('swishcallback.html', token=invoice_token, callback=result['result'])
	return redirect(url_for('invoices.result_payment'))

@invoices.route('/swish/callback/')
def result_payment():

	return render_template('swishcallback.html')

