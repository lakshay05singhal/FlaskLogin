from flask import Flask, render_template, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

from flask_login import (LoginManager, 
						 UserMixin, 
						 login_user, 
						 login_required, 
						 logout_user, 
						 current_user)

from security import encrypt_password, check_encrypted_password



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:@localhost/Stock"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'this/is/a/special/key/12345'
db = SQLAlchemy(app)

@app.before_first_request
def create_tables():
	db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class Users(UserMixin, db.Model):
	"""for user registration and login"""
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False)
	email = db.Column(db.String(20), nullable=False)
	password = db.Column(db.String(300), nullable=False)
	date = db.Column(db.String(15), nullable=True)
	

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))



@app.route("/")
def home():
	return "<h1> Welcome To the Market </h1>"


@app.route("/login", methods = ['GET', 'POST'])
def login():
	if(request.method == 'POST'):
		username = request.form.get('username')
		password = request.form.get('password')

		user = Users.query.filter_by(username=username).first()
		if user:
			if check_encrypted_password(password, user.password):
				login_user(user, remember=request.form.get('remember'))
				return redirect("/dashboard")
			else:
				return "problem in password"
		else:
			return "No such user"

	return render_template("login.html")


@app.route("/register", methods = ['GET', 'POST'])
def register():
	if(request.method == 'POST'):
		username = request.form.get('username')
		email = request.form.get('email')
		password = request.form.get('password')
		hashpassword = encrypt_password(password)

		entry = Users(username=username, email=email, password=hashpassword, date=datetime.now())
		db.session.add(entry)
		db.session.commit()
		return redirect("/login")

	return render_template("register.html")


@app.route('/dashboard')
@login_required
def dashboard():
	return "This is dashboard."


@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("/")


if __name__ == '__main__':
	app.run(debug=True)