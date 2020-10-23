from flask import render_template, Blueprint, flash, url_for, Markup, redirect
from flask_login import login_required, current_user


main = Blueprint('main', __name__)


# our beloved index page, here is where the magic will happen
@main.route('/')
@login_required
def home():
	#print(current_user)
	if not current_user.email:
		flash(Markup('TIPS: Ange en E-mail till ditt konto. Då kan du maila fakturor till andra. Du gör det <a href="%s" class="alert-link">här</a>') % url_for('user.profile'), category='warning')
	elif not current_user.confirmed_email:
		flash('TIPS: du behöver bekräfta din E-mail, kolla din email efter en länk eller gå till dina uppgifter och skicka efter en ny', category='warning')
	if not current_user.phone:
		flash(Markup('TIPS: Ange ett telefonnummer till ditt konto. Då kan du låta andra betala dina fakturor med Swish och skicka fakturor med SMS. Du gör det <a href="%s" class="alert-link">här</a>') % url_for('user.profile'), category='warning')
	elif not current_user.confirmed_phone:
		flash('TIPS: du behöver bekräfta ditt telefonnummer, gå till din profil och ange koden i smset eller skicka efter en ny kod', category='warning')
	return render_template("index.html", invoices_rec=len(current_user.invoice_receiver), invoices_sent=len(current_user.invoice_sender))

# if you are not logged in you will be directed to here
@main.route('/welcome')
def welcome():
	#print(current_user)
	#return render_template("welcome.html", user=current_user)
	return render_template("welcome.html")

@main.route('/<invoice_token>/')

def invoice_site(invoice_token):
	
	return redirect(url_for('invoices.view_open_invoice_site', invoice_token=invoice_token))