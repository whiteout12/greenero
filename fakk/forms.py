from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf, ValidationError, Optional, NumberRange
#from fakk import db
from fakk.models import User
from flask_login import current_user


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

def validate_username_reg(self,field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Användarnament är upptaget, väj ett annat!')
def validate_username(self,field):
    if User.query.filter(User.username==field.data, User.username!=current_user.username).first():
        raise ValidationError('Emailadressen är upptagen, väj ett annat!')

def validate_email(self,field):
    #if User.query.filter(User.email==field.data, User.confirmed_email, User.email!=current_user.email).first():
    if User.query.filter(User.email==field.data, User.email!=current_user.email).first():
        raise ValidationError('Emailadressen är upptagen, väj ett annat!')

def validate_phone(self,field):
    #if User.query.filter_by(phone=field.data, id=).first():
    if User.query.filter(User.phone==field.data, User.phone!=current_user.phone).first():
        raise ValidationError('Telefonnumret är upptaget, väj ett annat!')

def val_phone_format(self, field):
    if not field.data.startswith('07'):
        raise ValidationError('Fel format! Ska vara 07XXXXXXXX :)')

def validate_receiver(self,field):
    if field.data==-1:
        raise ValidationError('Välj en mottagare!')
        

def is_password_inserted(self,field):
    if field.data:
        return DataRequired()
    else:
        return Optional()

class RegisterForm(FlaskForm):

    
    username = TextField(
        'username',
        validators=[DataRequired(), validate_username_reg, Length(min=3, max=25)]
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
        validators=[DataRequired(), validate_username, Length(min=3, max=25)]
    )
    email = TextField(
        'email',
        validators=[Optional(), validate_email, Email(message=None), Length(min=6, max=40)]
    )
    phone = TextField(
        'phone',
        validators=[Optional(), validate_phone, val_phone_format,  Length(min=10, max=10)]
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
