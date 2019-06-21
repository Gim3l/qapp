from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from .models import User
from qapp import bcrypt
from flask_login import current_user

class LoginForm(FlaskForm):
	email = TextField('Email', validators=[DataRequired(),
		Email("A valid email address is required")])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data)
		if not user: raise ValidationError('Invalid email provided.')


class RegistrationForm(FlaskForm):
	username = TextField('Username', validators=[DataRequired(), Length(3, 12)])
	email = TextField('Email', validators=[DataRequired(), 
		Email(message='Invalid email format! A valid email address is required.')])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=8,
		message='Your password cannot be shorter than 8 characters, sorry :( ')])
	confirm_password = PasswordField('Confirm Password',
		validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
	
	#Checks if email is unique
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is already in use.')
			
	#Checks if username is unique
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Try something unique.')
			

#Form for editing account details
class EditAccountForm(FlaskForm):
	name = TextField('Full Name')
	username = TextField('Username', validators=[Optional(), Length(3, 12)])
	email = TextField('Email', validators=[Optional(), Email(message='Invalid email format! A\
	valid email address is required.')])
	current_password = PasswordField('Current Password',
		validators=[DataRequired()])
	image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message='Images only, sorry.')])
	submit = SubmitField('Update')
	
	#Validate whether prev pass supplied to form is current user's password
	def validate_current_password(self, previous_password):
		res = bcrypt.check_password_hash(current_user.password, previous_password.data)
		if res == False:
			raise ValidationError('Make sure you entered your current password correctly.')
	
	#Validate whether username is taken
	def validate_username(self, username):
		if username.data != current_user.username:	#If username is same as current_user's, 
			user = User.query.filter_by(username=username.data).first()
			if user: #then skip validation
				raise ValidationError('That username is taken. Please try a different one.')
	
	#Validate whether username is taken
	def validate_email(self, email):
		if email.data != current_user.email:	#If username is same as current_user's, 
			user = User.query.filter_by(email=email.data).first()
			if user: #then skip validation
				raise ValidationError('That email is taken. Please try a different else.')
	
#Form for changing password
class ChangePasswordForm(FlaskForm):
	new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8,
		message='Your password cannot be shorter than 8 characters, sorry :( ')])
	confirm_password = PasswordField('Confirm Password',
		validators=[Optional(), EqualTo('new_password')])
	current_password = PasswordField('Current Password',
		validators=[DataRequired()])
	submit = SubmitField('Change')
	
	#Validate whether prev pass supplied to form is current user's password
	def validate_current_password(self, current_password):
		res = bcrypt.check_password_hash(current_user.password, current_password.data)
		if res == False:
			raise ValidationError('Make sure you entered your current password correctly.')
	
	
#Form for submitting questions
class QuestionForm(FlaskForm):
	title = TextField('Question', validators = [DataRequired(), 
		Length(min=20, message='You must supply atleast 20 characters for\
			this question to be submitted.')])
	body = TextAreaField('Additional Details')
	submit = SubmitField('Submit Question')
	#Check if title ends with question mark, if not, adds question mark
	def validate_title(self, title):
		if not title.data.endswith('?'):
			title.data += '?'
			return False
		return True
		
		
#Form for submitting answers
class AnswerForm(FlaskForm):
	content = TextAreaField('Question', validators = [DataRequired(), 
		Length(min=20, message='You must supply atleast 20 characters for\
			this question to be submitted.')])
	submit = SubmitField('Submit Answer')
	
