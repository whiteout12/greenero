from itsdangerous import URLSafeTimedSerializer
#import os
from flask import flash, url_for, render_template
from fakk import app




def generate_invoice_token(invoiceID, userID):
    package = [invoiceID, userID]
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(package, salt=app.config['SECURITY_PASSWORD_SALT'])


def load_invoice_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        package = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT']
            
        )
    except:
        return False
    return package

