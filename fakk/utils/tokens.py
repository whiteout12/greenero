from itsdangerous import URLSafeTimedSerializer, URLSafeSerializer, BadSignature
#import os
from flask import flash, url_for, render_template
from fakk import app




def generate_invoice_token(invoiceID, userID):
    package = [invoiceID, userID]
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(package, salt=app.config['SECURITY_PASSWORD_SALT'])


def load_invoice_token(token):
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    try:
        package = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT']
            
        )
    except:
        return False
    return package

def generate_bill_token(billID):
    
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(billID, salt=app.config['SECURITY_BILL_SALT'])


def load_bill_token(token):
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    try:
        billid = serializer.loads(
            token,
            salt=app.config['SECURITY_BILL_SALT']
            
        )
    except:
        return False
    return billid

def generate_billdebt_token(billDebtID):
    
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(billDebtID, salt=app.config['SECURITY_BILLDEBT_SALT'])


def load_billdebt_token(token):
    serializer = URLSafeSerializer(app.config['SECRET_KEY'])
    try:
        billdebtid = serializer.loads(
            token,
            salt=app.config['SECURITY_BILLDEBT_SALT']
            
        )
    except:
        return False
    return billdebtid

