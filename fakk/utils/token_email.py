from itsdangerous import URLSafeTimedSerializer
#import os
from flask import flash, url_for, render_template
from fakk import app, mail
from flask_mail import Message



def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=900):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def send_confirmation_link_email(user_email):
    token = generate_confirmation_token(user_email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('confirm_email.html', confirm_url=confirm_url)
    msg = Message("Bekräfta emailadress - länk", sender=('fakk.', 'noreply@fakk.tech'), recipients=[str(user_email)])
    msg.html = html
    msg.body = "Följ länken nedan för att bekräfta din emailadress på fakk. " + str(confirm_url)
    mail.send(msg)
    #print('email skickat')
    flash('En länk har skickats till ' +str(user_email), category='success')
    return

def send_password_link_email(user_email):
    token = generate_confirmation_token(user_email)
    password_url = url_for('user.reset_password_token', token=token, _external=True)
    html = render_template('reset_password_email.html', reset_url=password_url)
    msg = Message("fakk. - Återställ lösenord - länk", sender=('fakk.', 'noreply@fakk.tech'), recipients=[str(user_email)])
    msg.html = html
    msg.body = "Följ länken nedan för att återställa ditt lösenord. " + str(password_url)
    mail.send(msg)
    
    return

def send_confirmation_link_email2(user_email, code):
    #token = generate_confirmation_token(user_email)
    #confirm_url = url_for('user.confirm_email', token=token, _external=True)
    print('email: ', user_email)
    print('code: ', code)
    #html = render_template('confirm_email.html', confirm_url=confirm_url)
    msg = Message("fakk. - Bekräfta ditt telefonnummer - kod", sender="tjena@fakk.tech", recipients=[str(user_email)])
    #msg.html = html
    msg.body = "Bekräfta med denna kod " + str(code)
    mail.send(msg)
    flash('Ett sms (just nu email) har skickats till ' +str(user_email), category='success')
    return

