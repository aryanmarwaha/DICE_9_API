from flask import Flask,render_template,request,url_for,Blueprint
from flask_mail import Mail, Message

from cryptography.fernet import Fernet
import mysql.connector,datetime
import hashlib,json,os
from random import randint

from secrets import token_hex

app = Flask(__name__)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME'),
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
)
mail = Mail(app)

enc_key = os.environ.get('ENCRYPTION_KEY').encode()
fernet = Fernet(enc_key)

def establish_connection():
	mydb = mysql.connector.connect(
		host=os.environ.get('DATABASE_NAME'),
		user=os.environ.get('DATABASE_USER'),
		password=os.environ.get('DATABASE_PASSWORD'),
		database='users_dice9_'
	)
	return mydb

def nullSafe(var):
	if var is None:
		return ''
	return var
	
from dice9api.users.routes import users
from dice9api.validation.routes import validate
from dice9api.utils.routes import utils

app.register_blueprint(users)
app.register_blueprint(validate)
app.register_blueprint(utils)