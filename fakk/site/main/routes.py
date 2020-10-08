from flask import render_template, Blueprint
from flask_login import login_required, current_user


main = Blueprint('main', __name__)


# our beloved index page, here is where the magic will happen
@main.route('/')
@login_required
def home():
	#print(current_user)
	return render_template("index.html", invoices_rec=len(current_user.invoice_receiver), invoices_sent=len(current_user.invoice_sender))

# if you are not logged in you will be directed to here
@main.route('/welcome')
def welcome():
	#print(current_user)
	#return render_template("welcome.html", user=current_user)
	return render_template("welcome.html")