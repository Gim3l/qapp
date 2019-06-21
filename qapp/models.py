from qapp import db, login_manager
from flask_login import UserMixin
from datetime import datetime

#Middleware function connecting flask-login to flask-sqlalchemy
@login_manager.user_loader
def user_loader(user_id):
	return User.query.get(int(user_id))

#Create user table
class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(60), unique=True, nullable=False)
	image_file = db.Column(db.String(60), nullable=False, default = 'default.jpg')
	password = db.Column(db.String(60), nullable=False)
	questions = db.relationship('Question', backref='author')
	answers = db.relationship('Answer', backref='author')
	join_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name = db.Column(db.String(30))
		
	def __repr__(self):
		return '<User %r>' % self.username
		
#Table that holds questions asked by each user
class Question(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(60), nullable=False)
	body = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	answers = db.relationship('Answer', backref='question')
	
	def __repr__(self):
		return '<Question %r>' % self.title

class Answer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text, nullable=False)
	pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	for_ques = db.Column(db.Integer, db.ForeignKey('question.id'))
	posted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Answer %r ...>' % self.content[:16]
	

