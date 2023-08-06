from dice9api import Blueprint
from dice9api import establish_connection
from dice9api import hashlib,token_hex,json
from dice9api import request,datetime,randint
from dice9api import mysql

from dice9api.users.objects import RegisteringUser, RegisteringStudent
from dice9api.users.objects import RegisteringAdmin, EnrollingUser
from dice9api.users.objects import Validate_Session, Login_Form

from dice9api.users.methods import send_email_verification_otp
from dice9api.users.methods import send_staff_request,send_new_admin_alert


# main :

users = Blueprint('users',__name__,template_folder="templates")

@users.route("/reset",methods=['POST'])
def reset():
	mydb = establish_connection()
	mycursor = mydb.cursor()
	sql = "DELETE FROM users_dice9_.verified_users"
	mycursor.execute(sql)
	sql = "DELETE FROM users_dice9_.student_info"
	mycursor.execute(sql)
	sql = "DELETE FROM users_dice9_.guest_info"
	mycursor.execute(sql)
	sql = "DELETE FROM users_dice9_.staff_info"
	mycursor.execute(sql)
	sql = "DELETE FROM cache_dice9_.pending_req_staff"
	mycursor.execute(sql)
	sql = "DELETE FROM cache_dice9_.verify_email"
	mycursor.execute(sql)
	mydb.commit()
	return "done"

@users.route('/api/enroll_user',methods=['POST'])
def enroll_user():
	#Parameter Initialization
	try:
		user = EnrollingUser(request)
		date_time = datetime.datetime.now()
	except:
		return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
	try:
		mydb = establish_connection()
		mycursor= mydb.cursor()

		#Validating User
		sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = '{}'"
		sql = sql.format(user.useremail)
		mycursor.execute(sql)
		mycursor.fetchall()
		if(mycursor.rowcount==1):
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "User Already Exists"})

		#OTP Generation
		otp_token = ''.join([str(randint(0,9)) for _ in range(6)])
		secretToken = hashlib.md5(otp_token.encode()).hexdigest()

		#Inserting/Updating Secret-Token In Database
		try:
			sql = "INSERT INTO cache_dice9_.verify_email (useremail,date_time,secret_Token) VALUES(%s,%s,%s)"
			values = (user.useremail, date_time, secretToken)
			mycursor.execute(sql,values)

		except mysql.connector.errors.IntegrityError:
			sql = "UPDATE cache_dice9_.verify_email SET date_time = %s, secret_Token = %s WHERE useremail = %s"
			values = (date_time, secretToken, user.useremail)
			mycursor.execute(sql,values)

		#Email Handler
		send_email_verification_otp(user.useremail, otp_token)
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Mail Sent"})

	except ValueError as e:
		return json.dumps({'success': 'false', 'msg': str(e)})
	except Exception as e:
		return json.dumps({'success': 'false', 'msg': "Some Error Occured"+str(e)})

@users.route("/api/register",methods=['POST'])
def register():
	#Parameter Initialization
	try:
		user = RegisteringUser(request)
		date_time = datetime.datetime.now()
	except:
		return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
	try:
		#Database Connection
		mydb = establish_connection()
		mycursor = mydb.cursor()

		#User Validation
		sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = %s AND app_token = %s AND register_dt IS NULL"
		values = (user.useremail,user.token)
		mycursor.execute(sql,values)
		mycursor.fetchall()
		if mycursor.rowcount == 0:
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
		
		#SQL Injection

		# user.role==0: student
		if user.role == '0':
			student = RegisteringStudent(request)
			sql = """
			INSERT INTO users_dice9_.student_info (useremail,first_name,second_name,
					age,gender,roll_no,branch,hosteler,address,interest_ids,skill_ids,
					open_to_work) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
			values = (user.useremail,user.firstname,user.secondname,user.age,user.gender,
					student.rollno,student.branch,student.hosteler,student.address,
					student.interests,student.skills,student.open_to_work)
			mycursor.execute(sql,values)

		#user.role == guest 1 / staff 2
		elif user.role == '1' or user.role=='2':
			
			#user.role==2: staff
			token = token_hex(16)
			if user.role == '2':
				sql = """INSERT INTO cache_dice9_.pending_req_staff (useremail,date_time,
						request_id) Values(%s,%s,%s)"""
				values = (user.useremail,date_time,token)
				mycursor.execute(sql,values)
				username =  user.firstname +' '+ user.secondname
				send_staff_request(mydb, username, user.useremail, token)

			# user.role==1: guest (DEFAULT)
			user.role = '1'
			sql = """
			INSERT INTO users_dice9_.guest_info (useremail,first_name,second_name,
					age,gender) VALUES(%s,%s,%s,%s,%s)"""
			values = (user.useremail,user.firstname,user.secondname,user.age,
					user.gender)
			mycursor.execute(sql,values)
		
		#Updating mobile, password, register_dt And role
		token1_= token_hex(16)
		token2_= token_hex(16)

		user.password = hashlib.md5(str(user.password).encode()).hexdigest()

		sql = "UPDATE users_dice9_.verified_users SET mobile_no = %s, app_token = %s, web_token = %s, password = %s, role = %s , register_dt = %s , status = 1"
		values = (user.mobile_no , token1_ , token2_ , user.password , user.role , date_time)
		mycursor.execute(sql,values)
		mycursor.fetchall()
		
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Register Successful"})
	except Exception as e:
		return json.dumps({'success':'false','msg':"Some Error Occured"+str(e)})

@users.route("/api/login",methods=['GET'])
def login():
	#Parameter Initialization
	try:
		req = Login_Form(request)
		date_time = datetime.datetime.now()
	except:
		return json.dumps({'success':'false','msg':"Bad Parameters"})
	try:
		#Database Connection
		mydb = establish_connection()
		mycursor= mydb.cursor()

		# User Validation
		sql = "SELECT status, logged_in_app, logged_in_web FROM users_dice9_.verified_users WHERE useremail = %s AND password = %s"
		values = (req.useremail,req.password)
		mycursor.execute(sql,values)
		res = mycursor.fetchall()
		if mycursor.rowcount == 0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
		res = res[0]
		if res[0]==0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Register First"})

		elif res[0]==2:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Account Suspended"})

		# Creating New Session
		new_token = token_hex(16)
		if req.device == '0':
			sql = """UPDATE users_dice9_.verified_users SET logged_in_app = 1,\
					 app_token = %s WHERE useremail = %s"""
		if req.device == '1':
			sql = """UPDATE users_dice9_.verified_users SET logged_in_web = 1,\
					 web_token = %s WHERE useremail = %s"""
		values = (new_token, req.useremail)
		mycursor.execute(sql,values)
		
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Login Successfull", 'token': new_token})
	
	except Exception as e:
		print(str(e))
		mydb.disconnect()
		return json.dumps({'success':'false','msg':"Some Error Occured"})

@users.route("/api/logout",methods=['POST'])
def logout():
	#Parameter Initialization
	try:
		req = Validate_Session(request)
		date_time = datetime.datetime.now()
	except:
		print("you")
		return json.dumps({'success':'false','msg':"Bad Parameters"})
	try:
		#Database Connection
		mydb = establish_connection()
		mycursor = mydb.cursor()

		#Session Validation
		if req.device == '0':
			sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = %s AND app_token= %s"
		elif req.device == '1':
			sql = "SELECT useremail FROM users_dice9_.verified_users WHERE useremail = %s AND web_token= %s"
		
		values = (req.useremail , req.token)
		mycursor.execute(sql,values)
		logged_in = mycursor.fetchall()

		if (mycursor.rowcount == 0):
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})

		# Logging-Out User
		if req.device == '0':
			sql = "UPDATE users_dice9_.verified_users SET logged_in_app = 0, app_token = %s, last_login_app =%s"
		elif req.device == '1':
			sql = "UPDATE users_dice9_.verified_users SET logged_in_web = 0, web_token = %s, last_login_web =%s"
		
		values = (token_hex(16),date_time)
		mycursor.execute(sql,values)
		
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success':'true','msg':"Logout Successfull"})

	except Exception as e:
		return json.dumps({'success':'false','msg':"Some Error Occured"})

@users.route("/api/add_administrator",methods=['POST'])
def add_administrator():
	#Parameter Initialization
	obj = RegisteringAdmin(request)

	try:
		obj.password = hashlib.md5(obj.password.encode()).hexdigest()
		obj.new_password = hashlib.md5(obj.new_password.encode()).hexdigest()
		date_time = datetime.datetime.now()

		mydb = establish_connection()
		mycursor = mydb.cursor()


		#Admin Validation
		sql = "SELECT useremail FROM users_dice9_.admin WHERE useremail = '{}' AND password = '{}'"
		sql = sql.format(obj.authoriser, obj.password)
		mycursor.execute(sql)
		mycursor.fetchall()
		if mycursor.rowcount == 0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Access denied"})

		user_key = token_hex(4)
		#SQL Injection
		sql = """INSERT INTO users_dice9_.admin (useremail,user_name,password,authorised_by,
				authorised_at,user_key) VALUES (%s,%s,%s,%s,%s,%s)"""
		values = (obj.useremail,obj.username,obj.new_password,obj.authoriser,date_time,user_key)

		mycursor.execute(sql,values)
		send_new_admin_alert(mydb,obj.useremail,obj.username,obj.authoriser,date_time)
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Admin Added"})
	except mysql.connector.errors.IntegrityError:
		return json.dumps({'success': 'false', 'msg': "Bad Parameters"})

	except Exception as e:
		return json.dumps({'success': 'false', 'msg': "Some Error Occured"+str(e)})