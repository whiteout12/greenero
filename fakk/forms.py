from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf, ValidationError, Optional, NumberRange, StopValidation, Regexp
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
    if User.query.filter(User.email==field.data, User.confirmed_email, User.email!=current_user.email).first():
    #if User.query.filter(User.email==field.data, User.email!=current_user.email).first():
        raise ValidationError('Emailadressen är upptagen, väj ett annat!')

def validate_phone(self,field):
    #if User.query.filter_by(phone=field.data, id=).first():
    if User.query.filter(User.phone==field.data, User.confirmed_phone, User.phone!=current_user.phone).first():
        raise ValidationError('Telefonnumret är upptaget, väj ett annat!')

def validate_phone_self(self,field):
    #if User.query.filter_by(phone=field.data, id=).first():
    if current_user.phone == field.data:
        raise ValidationError('Du kan inte välja ditt eget nummer, väj ett annat!')

def val_phone_format(self, field):
    if not field.data.startswith('07'):
        raise ValidationError('Fel format! Ska vara 07XXXXXXXX :)')

def validate_receiver(self,field):
    if field.data==-1:
        raise ValidationError('Välj en mottagare!')
        
def is_user_chosen(self,field):
    
    
    if self.inv_type.data!=1:
        print('user is chosen')
        raise StopValidation()

def is_email_chosen(self,field):

    if self.inv_type.data!=2:
        print('email is chosen')
        #self.receiver.StopValidation
        raise StopValidation()
        #return (DataRequired(), validate_email, Email(message=None), Length(min=6, max=40))

def is_phone_chosen(self,field):
    
    if self.inv_type.data!=3:
        print('phone is chosen')
        raise StopValidation()
        
    else:
        return Optional()

def is_password_inserted(self,field):
    print('field', field.data)
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
            DataRequired(), EqualTo('password', message='Lösenorden överensstämmer inte')
        ]
    )

class ResetPasswordForm(FlaskForm):


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
        validators=[Optional(), validate_phone, val_phone_format,  Length(min=10, max=10), Regexp('^[0-9]*$', message='Får bara innehålla sifror')]
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
    
    
    inv_type = RadioField('Alternativ',  coerce=int, choices=[(1,'Till någon av dina kontakter på fakk.'),(2,'Till någons E-mail'),(3,'Till någons telefon')], default=1)

    receiver = SelectField('Receiver', coerce=int,
        
        validators=[is_user_chosen, validate_receiver]
    )

    email = TextField(
        'E-mail',
        validators= [is_email_chosen, Email(message='Fel format för E-mail'), Length(min=6, max=40, message='Fel längd')]
    )

    phone = TextField(
        'Telefon',
        validators=[is_phone_chosen, val_phone_format, validate_phone_self,  Length(min=10, max=10, message='Måste vara 10 siffror'),Regexp('^[0-9]*$', message='Får bara innehålla sifror')]
    )


    description = TextAreaField(
        'description',
        validators=[DataRequired(), Length(min=5, max=160, message="Lite längre är nog bra för tydlighetens skull :)")]
    )
    amount = IntegerField('amount', validators=[DataRequired(), NumberRange(min=1, message='')]
    )

class ChangeInvoice(FlaskForm):
    
    description = TextAreaField(
        'description',
        validators=[DataRequired(), Length(min=5, max=160, message="Lite längre är nog bra för tydlighetens skull :)")]
    )
    amount = IntegerField('amount', validators=[DataRequired(), NumberRange(min=1, message='')]
    )
