from flask import render_template, url_for, flash, redirect, request, abort
from qapp import app, bcrypt, db
from .models import Question, User, Answer
from .forms import LoginForm, RegistrationForm, QuestionForm, EditAccountForm, ChangePasswordForm, AnswerForm
from flask_login import login_user, current_user, logout_user, login_required
from random import choice
import os, secrets

def save_image(image):
	new_prefix = secrets.token_hex(6)
	_, ext = os.path.splitext(image.filename)
	image_name = new_prefix+ext
	path = os.path.join(app.root_path, 'static/images/users', image_name)
	image.save(path)
	return image_name

@app.route('/')
def home():
   current_page = request.args.get('page', 1, type=int)
   questions = Question.query.order_by(Question.pub_date.desc()).paginate(per_page=5, page=current_page)
   styles = ['danger', 'info', 'warning', 'purple']
   
   return render_template('home.html', title='Homepage', questions=questions, styles=styles, choice=choice, current_page=current_page)
   
 
@app.route('/question/<question_id>', methods=['GET', 'POST'])
def question(question_id):
	question = Question.query.get_or_404(question_id)
	form = AnswerForm()
	
	if form.validate_on_submit():
		ans = Answer(content=form.content.data, for_ques=question_id, author=current_user)
		db.session.add(ans)
		db.session.commit()
		flash('Your answer has been submitted.', category='success')
		return redirect(url_for('question', question_id=question_id))
		
	return render_template('question.html', ques=question, title=question.title, form=form)   

	
@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
	form = QuestionForm()
	ques = Question.query.get_or_404(question_id)
	
	if current_user == ques.author:
		
		if form.validate_on_submit():
			ques.title = form.title.data
			ques.body = form.body.data
			db.session.commit()
			flash('Question saved.', category='success')
			return redirect(url_for('question', question_id=question_id))
	else:
		abort(403)
		
	if request.method == 'GET':
		form.title.data = ques.title
		form.body.data = ques.body
		
	return render_template('submit_question.html', title='Edit Question', form=form)

	
@app.route('/question/submit', methods=['GET', 'POST'])
@login_required
def submit_question():
	form = QuestionForm()
	if form.validate_on_submit():
		ques = Question(title=form.title.data, body=form.body.data, author=current_user)
		db.session.add(ques)
		db.session.commit()
		flash('Question submitted.', category='success')
		return redirect(url_for('home'))
		
	return render_template('submit_question.html', title='Submit Question', form=form)

		



@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if current_user.is_authenticated:
		return redirect(url_for('home'))
		
	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data
		user = User.query.filter_by(email=email).first()
		
		if bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			flash('Account logged in.', category='success')
			return redirect(url_for('home'))
		else:
			flash('Invalid credentials. Try again.', category='danger')
			
	return render_template('login.html', title='Login', form=form)
	


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = EditAccountForm()
	change_pass_form = ChangePasswordForm()
	
	if form.validate_on_submit():
		if form.name.data: current_user.name = form.name.data
		if form.username.data: current_user.username = form.username.data
		if form.email.data: current_user.email = form.email.data
		if form.image.data: current_user.image_file = save_image(form.image.data)
		db.session.commit()
		flash('Account details updated.', category='success')
		return redirect(url_for('account'))
	
	
	if not form.validate_on_submit() and request.method == 'POST':
		flash('Unable to update account information. Please check your details.', category='danger') 
		
	if change_pass_form.validate_on_submit():
		user = User.query.get(current_user.id)
		new_pass_hash = bcrypt.generate_password_hash(change_pass_form.new_password.data).decode('utf-8')
		user.password = 'change_pass_form.new_password.data'
		db.session.add(user)
		db.session.commit()
		flash("Password changed!")
	
		return redirect(url_for('account'))
		
		
	return render_template('account.html', title='Account', form=form, change_pass_form=change_pass_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	
	if current_user.is_authenticated:
		return redirect(url_for('home'))
		
	if form.validate_on_submit():
		account = User(username=form.username.data, email=form.email.data, 
			password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'))
		flash('Account created.', category='success')
		db.session.add(account)
		db.session.commit()
		redirect(url_for('home'))
		
	return render_template('register.html', title='Registration', form=form)


@app.route('/logout')
@login_required
def logout():
	logout_user()
	
	return redirect(url_for('home'))
