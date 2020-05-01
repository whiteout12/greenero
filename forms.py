from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf


class LoginForm(FlaskForm):
    username = TextField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    
    username = TextField(
        'username',
        validators=[DataRequired(), Length(min=3, max=25),NoneOf(['m'], message='email already in database', values_formatter=None)]
        #validators=[DataRequired(), Length(min=3, max=25),NoneOf([User.query.filter_by(name=username).first()], message='email already in database', values_formatter=None)]
    )
    email = TextField(
        'email',
        validators=[DataRequired(), Email(message=None), Length(min=6, max=40), NoneOf(['bjorncarlsson87@gmail.com','hej@test.com','h@t.m'], message='email already in database', values_formatter=None)]
    )
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