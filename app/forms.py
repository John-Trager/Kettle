import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField,  BooleanField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, State

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])

    email = StringField('Email', validators=[DataRequired(),Email()])

    password = PasswordField('Password', validators=[DataRequired(), Length(max=10)]) #could add min/max length

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=10), EqualTo('password')]) #could add min/max length

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is in use. Please use a different one ')

class LoginForm(FlaskForm):
    #could use username to login but in this case we are using email

    email = StringField('Email', validators=[DataRequired(),Email()])

    password = PasswordField('Password', validators=[DataRequired(), Length(max=10)]) #could add min/max length
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])

    email = StringField('Email', validators=[DataRequired(),Email()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose another')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is in use. Please use a different one ')

class StateForm(FlaskForm):

    mon = BooleanField("Monday")
    tue = BooleanField("Tuesday")
    wed = BooleanField("Wednesday")
    thu = BooleanField("Thursday")
    fri = BooleanField("Friday")
    sat = BooleanField("Saturday")
    sun = BooleanField("Sunday")
    
    hour = IntegerField("Hour", validators=[DataRequired()])
    minute = IntegerField("Minutes")

    submit = SubmitField('Add')

    def validate_hour(self, hour):
        if hour.data < 0 and hour.data > 23:
            raise ValidationError('Hour must be in the range 0-23')

    def validate_minute(self, minute):
        if minute.data == None:
            raise ValidationError('Minute must be in the range 0-59')
        elif minute.data < 0 and minute.data > 59:
            raise ValidationError('Minute must be in the range 0-59')

    def validate_days(self, mon, tue, wed, thu, fri, sat, sun):
        if mon.data or tue.data or wed.data or thu.data or fri.data or sat.data or sun.data:
            pass
        else:
            raise ValidationError('You must select at least one day')

