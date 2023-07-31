from flask import Flask,render_template,request,url_for,Blueprint
from flask_mail import Mail, Message

from cryptography.fernet import Fernet
import mysql.connector,datetime
import hashlib,json,os

from secrets import token_hex

app = Flask(__name__)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = os.environ.get('MAIL_SERVER_EMAILID'),
	MAIL_PASSWORD = os.environ.get('MAIL_SERVER_EMAIL_PASSWORD')
)
mail = Mail(app)

enc_key = os.environ.get('ENCRYPTION_KEY').encode()
fernet = Fernet(enc_key)

def establish_connection():
	mydb = mysql.connector.connect(
		host='localhost',
		user='root',
		password='root',
		database='dice_9_'
	)
	return mydb

def nullSafe(var):
	if var is None:
		return ''
	return var
	
from dice9api.users.routes import users
from dice9api.validation.routes import validate

app.register_blueprint(users)
app.register_blueprint(validate)