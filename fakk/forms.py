from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, TextAreaField, IntegerField, RadioField, SubmitField, SelectMultipleField, DecimalField, FloatField, FieldList, Form, FormField, BooleanField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField, FileAllowed
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

def validate_email_self(self,field):
    #if User.query.filter_by(phone=field.data, id=).first():
    if current_user.email == field.data:
        raise ValidationError('Du kan inte välja din egen adress, väj en annan!')

def val_phone_format(self, field):
    if not field.data.startswith('07'):
        raise ValidationError('Fel format! Ska vara 07XXXXXXXX :)')

def validate_receiver(self,field):
    if field.data==-1:
        raise ValidationError('Välj en mottagare!')

def validate_participants(self,field):
    if len(field.data)==0:
        raise ValidationError('Välj minst en deltagare!')

def validate_any_participants(self,field):
    print('kollar om nåt är valt överhuvudtaget')
    print('contact_bool', self.contact_bool)
    print(self.sms_bool)
    if self.contact_bool.data==False and self.sms_bool.data == False:

            raise ValidationError('Välj minst en deltagare från kontakter, via SMS eller båda')
        
def is_user_chosen(self,field):
    print('kollar user')
    
    if self.inv_type.data!=1:
        print('tar bort val för user')
        raise StopValidation()



def is_email_chosen(self,field):
    print('kollar mail')
    if self.inv_type.data!=2:
        print('tar bort val för mail')
        raise StopValidation()

def is_phone_chosen(self,field):
    print('kollar phone')
    if self.inv_type.data!=3:
        print('tar bort val för tele')
        raise StopValidation()
        
    else:
        return Optional()

def is_contact_false(self,field):
    print('kollar contacts', self.contact_bool.data)
    if self.contact_bool.data is False:
        raise StopValidation()

def is_sms_false(self, field):
    print('kollar sms', self.sms_bool.data)
    if self.sms_bool.data is False:
        #print('clear phones',self.phones.data)
        
        raise StopValidation()
        

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
    email = EmailField(
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
    
    
    inv_type = RadioField('Alternativ',  coerce=int, choices=[(1,'Kontakt på fakk.'),(2,'E-mail'),(3,'SMS')], default=1)

    receiver = SelectField('Receiver', coerce=int, validators=[is_user_chosen, validate_receiver], render_kw={'data-live-search': 'true'}
    )

    email = EmailField(
        'E-mail',
        validators= [is_email_chosen, validate_email_self, Email(message='Fel format för E-mail'), Length(min=6, max=40, message='Fel längd')]
    )

    phone = TextField(
        'Telefon',
        validators=[is_phone_chosen, val_phone_format, validate_phone_self,  Length(min=10, max=10, message='Måste vara 10 siffror'),Regexp('^[0-9]*$', message='Får bara innehålla sifror')]
    )


    description = TextAreaField(
        'description',
        validators=[DataRequired(message="Obligtoriskt fält"), Length(min=5, max=160, message="Lite längre är nog bra för tydlighetens skull :)")]
    )
    amount = IntegerField('amount', validators=[DataRequired(message="Obligtoriskt fält"), NumberRange(min=1, message='Inte en siffra')]
    )

class ChangeInvoice(FlaskForm):
    
    description = TextAreaField(
        'description',
        validators=[DataRequired(message="Obligtoriskt fält"), Length(min=5, max=160, message="Lite längre är nog bra för tydlighetens skull :)")]
    )
    amount = IntegerField('amount', validators=[DataRequired(message="Obligtoriskt fält"), NumberRange(min=1, message='')]
    )

class phoneForm(FlaskForm):

    phone = TextField('Telefonnummer', validators=[is_sms_false, val_phone_format, validate_phone_self,  Length(min=10, max=10, message='Måste vara 10 siffror'),Regexp('^[0-9]*$', message='Får bara innehålla sifror')]
    )

class FlexibleDecimalField(DecimalField):

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleDecimalField, self).process_formdata(valuelist)


class CreateBill(FlaskForm):
    
    description = TextField(
        'Avser',
        validators=[DataRequired(message="Obligtoriskt fält"), Length(min=2, max=160, message="Lite längre är nog bra för tydlighetens skull :)")]
    )

    contact_bool = BooleanField('Kontakt på fakk.', validators=[])
    #validate_any_participants

    sms_bool = BooleanField('SMS', validators=[])
    
    participants = SelectMultipleField('Kontakt', coerce=int,
        
        validators=[is_contact_false, validate_participants], render_kw={'data-live-search': 'true', 'title':'Välj kontakter', 'noneResultsText' : 'inga resultat för {0}'}
    )

    phones = FieldList(TextField('Telefonnummer', validators=[is_sms_false, val_phone_format, validate_phone_self,  Length(min=10, max=10, message='Måste vara 10 siffror'),Regexp('^[0-9]*$', message='Får bara innehålla sifror')],
    ), min_entries=1, validators=[])

    names = FieldList(TextField('Namn', validators=[is_sms_false, DataRequired(message="Obligtoriskt fält")]), min_entries=1)

    amount = FlexibleDecimalField('Belopp på nota', validators=[]
    )

    totalamount = FlexibleDecimalField('Belopp som betalats (inkl. ev dricks)', validators=[DataRequired(message="Obligtoriskt fält"), NumberRange(min=1, message='Inte en siffra')]
    )

    receipt = FileField('ladda upp bild på kvitto', validators=[FileAllowed(['jpg', 'png', 'heif', 'jpeg'])])

    submit = SubmitField('Skapa nota')

class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))  

class LobbyForm(FlaskForm):
    nickname = TextField('Jag väljer att kalla mig', validators=[DataRequired()])
    submit = SubmitField('Till notan')
    #password = PasswordField('Password', validators=[DataRequired()])    


