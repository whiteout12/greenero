from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf, ValidationError, Optional, NumberRange
#from users_db import listAllUserNames


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

def validate_username(self,field):
    from app import db
    from models import User
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Username has been taken, please choose another!')

def validate_email(self,field):
    from app import db
    from models import User
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('The emailadress has been registered already!')

def validate_phone(self,field):
    from app import db
    from models import User
    if User.query.filter_by(phone=field.data).first():
        raise ValidationError('The phone number has been registered already!')

def validate_receiver(self,field):
    if field.data==-1:
        raise ValidationError('choose a receiver!')
        

def is_password_inserted(self,field):
    if field.data:
        return DataRequired()
    else:
        return Optional()

class RegisterForm(FlaskForm):

    
    username = TextField(
        'username',
        validators=[DataRequired(), validate_username, Length(min=3, max=25)]
    )
    #email = TextField(
    #    'email',
    #    validators=[DataRequired(), validate_email, Email(message=None), Length(min=6, max=40)]
    #)
    password = PasswordField(
        'password',
        validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[
            DataRequired(), EqualTo('password', message='Passwords must match.')
        ]
    )
class ChangeUserForm(FlaskForm):

    username = TextField(
        'username',
        validators=[Optional(), validate_username, Length(min=3, max=25)]
    )
    email = TextField(
        'email',
        validators=[Optional(), validate_email, Email(message=None), Length(min=6, max=40)]
    )
    phone = TextField(
        'phone',
        validators=[Optional(), validate_phone, Length(min=10, max=10)]
    )
    password = PasswordField(
        'password',
        validators=[Optional(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        'Repeat password',
        validators=[is_password_inserted, 
            EqualTo('password', message='Passwords must match.')
        ]
    )

class CreateInvoice(FlaskForm):
    
    receiver = SelectField('Receiver', coerce=int,
        
        validators=[DataRequired(), validate_receiver]
    )
    description = TextAreaField(
        'description',
        validators=[DataRequired(), Length(min=6, max=400)]
    )
    amount = IntegerField('amount', validators=[NumberRange(min=1, message='Invalid length')]
    )

class ChangeInvoice(FlaskForm):
    
    description = TextAreaField(
        'description',
        validators=[Optional(), Length(min=6, max=400)]
    )
    amount = IntegerField('amount', validators=[Optional(), NumberRange(min=1, message='Invalid length')]
    )
