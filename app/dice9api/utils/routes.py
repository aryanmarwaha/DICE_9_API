from dice9api import Blueprint
from dice9api import establish_connection
from dice9api import request, json, nullSafe
from dice9api import mysql,hashlib,randint
from dice9api import datetime,token_hex

from dice9api.utils.methods import send_reset_password_otp
from dice9api.utils.objects import Validate_OTP, Reset_Password

utils = Blueprint('utils',__name__,template_folder="templates")

# main :

@utils.route("/api/request-reset-password",methods=['POST'])
def request_reset_password():
	useremail = nullSafe(request.form.get('useremail'))
	date_time = datetime.datetime.now()
	try:
		mydb = establish_connection()
		mycursor = mydb.cursor()
		
		#Validating User
		sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = '{}'"
		sql = sql.format(useremail)
		mycursor.execute(sql)
		mycursor.fetchall()
		if(mycursor.rowcount==0):
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "User Does Not Exists"})

		#OTP Generation
		otp_token = ''.join([str(randint(0,9)) for _ in range(6)])
		secretToken = hashlib.md5(otp_token.encode()).hexdigest()

		#Inserting/Updating Secret-Token In Database
		try:
			sql = "INSERT INTO cache_dice9_.reset_password (useremail,date_time,secret_Token) VALUES(%s,%s,%s)"
			values = (useremail, date_time, secretToken)
			mycursor.execute(sql,values)

		except mysql.connector.errors.IntegrityError:
			sql = "UPDATE cache_dice9_.reset_password SET date_time = %s, secret_Token = %s WHERE useremail = %s"
			values = (date_time, secretToken, useremail)
			mycursor.execute(sql,values)

		#Email Handler
		send_reset_password_otp(useremail, otp_token)
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Mail Sent"})

	except ValueError as e:
		return json.dumps({'success': 'false', 'msg': str(e)})
	except Exception as e:
		return json.dumps({'success': 'false', 'msg': "Some Error Occured"+str(e)})


@utils.route("/api/verify-reset-password",methods=['POST'])
def verify_reset_password():
	#Parameter Initialization
	try:
		req = Validate_OTP(request)
		date_time = datetime.datetime.now()
	except Exception as e:
		return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
	
	try:
		#Database Connection
		mydb = establish_connection()
		mycursor= mydb.cursor()

		#Request Validation
		sql = "SELECT date_time FROM cache_dice9_.reset_password WHERE useremail = %s AND secret_Token = %s"
		values = (req.useremail,req.otp)
		mycursor.execute(sql,values)
		enroll_dt = mycursor.fetchall()
		
		#Validating OTP
		if mycursor.rowcount == 0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
		
		elif (date_time-enroll_dt[0][0]).total_seconds() > 480 :
			sql = "DELETE FROM cache_dice9_.reset_password WHERE useremail ='{}'"
			sql = sql.format(req.useremail)
			mycursor.execute(sql)

			mydb.commit()
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "OTP Expired"})
		# Descarding OTP
		sql = "DELETE FROM cache_dice9_.reset_password WHERE useremail ='{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)

		#Logging Out && Resetting Password && returning login_token
		app_token = token_hex(16)
		web_token = token_hex(16)

		sql = """UPDATE users_dice9_.verified_users SET logged_in_app=0,\
				 logged_in_web=0, app_token=%s, web_token=%s, password=%s"""
		values = (app_token,web_token,token_hex(16))
		mycursor.execute(sql,values)

		# device==0: app || device==1: web
		if(req.device == '0'):
			mydb.commit()
			mydb.disconnect()
			return json.dumps({'success': 'true', 'msg': "Ready To Set Password", 'token': app_token})

		elif(req.device == '1'):
			mydb.commit()
			mydb.disconnect()
			return json.dumps({'success': 'true', 'msg': "Ready To Set Password", 'token': web_token})

		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Some Error Occured"})

	except Exception as e:
		print(e)
		mydb.disconnect()
		return json.dumps({'success': 'false', 'msg': "Some Error Occured" +str(e)})


@utils.route("/api/reset-password",methods=['POST'])
def reset_password():
	try:
		req = Reset_Password(request)
	except:
		return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
	try:
		#Database Connection
		mydb = establish_connection()
		mycursor= mydb.cursor()

		#User Validation
		# device==0: app || device==1: web
		if req.device=='0':
			sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = %s AND app_token = %s"
		elif req.device=='1':
			sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = %s AND web_token = %s"

		values = (req.useremail,req.token)
		mycursor.execute(sql,values)
		mycursor.fetchall()
		if mycursor.rowcount==0:
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})

		#Logging Out of All Sessions
		app_token = token_hex(16)
		web_token = token_hex(16)
		sql = """UPDATE users_dice9_.verified_users SET logged_in_app=0,\
				 logged_in_web=0, app_token=%s, web_token=%s, password=%s"""
		values = (app_token,web_token,token_hex(16))
		mycursor.execute(sql,values)

		#Updating Password
		sql = "UPDATE users_dice9_.verified_users SET password = '{}'"
		sql = sql.format(req.password)
		mycursor.execute(sql)
		if req.login =='1':
			token_ = app_token if device=='0' else web_token
			mydb.commit()
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Login Successfull", 'token': token_})
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'false', 'msg': "Login Successfull"})

	except Exception as e:
		mydb.disconnect()
		return json.dumps({'success': 'false', 'msg': "Some Error Occured"})