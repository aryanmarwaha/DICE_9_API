from dice9api import Blueprint
from dice9api import establish_connection
from dice9api import hashlib,token_hex,json
from dice9api import request, datetime
from dice9api import mysql

from dice9api.users.objects import RegisteringUser, RegisteringStudent
from dice9api.users.objects import RegisteringAdmin, EnrollingUser
from dice9api.users.methods import send_email_verification_otp
from dice9api.users.methods import send_staff_request

from random import randint

# main :

users = Blueprint('users',__name__,template_folder="templates")

@users.route("/reset",methods=['POST'])
def reset():
	mydb = establish_connection()
	mycursor = mydb.cursor()

	sql = "DELETE FROM dice_9_.verified_users"
	mycursor.execute(sql)

	sql = "DELETE FROM dice_9_.student_user_info"
	mycursor.execute(sql)

	sql = "DELETE FROM dice_9_.guest_user_info"
	mycursor.execute(sql)

	sql = "DELETE FROM dice_9_.staff_user_info"
	mycursor.execute(sql)

	sql = "DELETE FROM dice_9_.waiting_staff_cache"
	mycursor.execute(sql)

	sql = "DELETE FROM dice_9_.email_verification_cache"
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
		sql = "SELECT useremail FROM dice_9_.verified_users WHERE useremail = '{}'"
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
			sql = "INSERT INTO dice_9_.email_verification_cache (useremail,date_time,secret_Token) VALUES(%s,%s,%s)"
			values = (user.useremail, date_time, secretToken)
			mycursor.execute(sql,values)

		except mysql.connector.errors.IntegrityError:
			sql = "UPDATE dice_9_.email_verification_cache SET date_time = %s, secret_Token = %s WHERE useremail = %s"
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
		return json.dumps({'success': 'false', 'msg': "Internal Server Error"+str(e)})


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
		sql = "SELECT useremail FROM dice_9_.verified_users WHERE useremail = %s AND app_token = %s AND register_dt IS NULL"
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
			INSERT INTO dice_9_.student_user_info (useremail,first_name,second_name,
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
				sql = """INSERT INTO dice_9_.waiting_staff_cache (useremail,date_time,
						request_id) Values(%s,%s,%s)"""
				values = (user.useremail,date_time,token)
				mycursor.execute(sql,values)
				username =  user.firstname +' '+ user.secondname
				send_staff_request(mydb, username, user.useremail, token)

			# user.role==1: guest (DEFAULT)
			user.role = '1'
			sql = """
			INSERT INTO dice_9_.guest_user_info (useremail,first_name,second_name,
					age,gender) VALUES(%s,%s,%s,%s,%s)"""
			values = (user.useremail,user.firstname,user.secondname,user.age,
					user.gender)
			mycursor.execute(sql,values)
		
		#Updating mobile, password, register_dt And role
		token1_= token_hex(16)
		token2_= token_hex(16)

		user.password = hashlib.md5(str(user.password).encode()).hexdigest()

		sql = "UPDATE dice_9_.verified_users SET mobile_no = %s, app_token = %s, web_token = %s, password = %s, role = %s , register_dt = %s , status = 1"
		values = (user.mobile_no , token1_ , token2_ , user.password , user.role , date_time)
		mycursor.execute(sql,values)
		mycursor.fetchall()
		
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Register Successful"})
	except Exception as e:
		return json.dumps({'success':'false','msg':"Internal Server Error"+str(e)})


@users.route("/api/login",methods=['GET'])
def login():
	#Parameter Initialization
	useremail = request.form.get('useremail')
	password = str(request.form.get('password'))

	login_device = str(request.form.get('login_device'))

	#Parameter processing
	password = hashlib.md5(password.encode()).hexdigest()
	date_time = datetime.datetime.now()

	try:
		#Database Connection
		mydb = establish_connection()
		mycursor= mydb.cursor()

		# User Validation
		sql = "SELECT status, logged_in_app, logged_in_web FROM dice_9_.verified_users WHERE useremail = %s AND password = %s"
		values = (useremail,password)
		mycursor.execute(sql,values)
		res = mycursor.fetchall()
		if mycursor.rowcount == 0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
		
		elif res[0][0]==0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Register First"})

		elif res[0][0]==2:
			# pending----- for duration or if the suspension was over etc.
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Account Suspended"})
			
		elif res[0][0]==3:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Account Freezed"})
		
		res = res[0]
		secretToken = token_hex(16)
		
		# updating app_token
		if login_device == '0':
			if(res[1]==1):
				mydb.disconnect()
				return json.dumps({'success': 'false', 'msg': "You Are Already Logged In"})

			sql = "UPDATE dice_9_.verified_users SET logged_in_app = 1, app_token = %s, last_login_app = %s WHERE useremail = %s"
		
		# updating web_token
		elif login_device == '1':
			if(res[2]==1):
				mydb.disconnect()
				return json.dumps({'success': 'false', 'msg': "You Are Already Logged In Web"})

			sql = "UPDATE dice_9_.verified_users SET logged_in_web = 1,web_token = %s, last_login_web = %s WHERE useremail = %s"
		
		else:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})

		values = (secretToken , date_time , useremail)
		mycursor.execute(sql,values)
		
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Login Successfull", 'token': secretToken})
	
	except Exception as e:
		mydb.disconnect()
		return json.dumps({'success':'false','msg':"Internal Server Error"+str(e)})

@users.route("/api/logout",methods=['POST'])
def logout():
	useremail = request.form.get('useremail')
	token = request.form.get('token')
	login_device = request.form.get('login_device')

	try:
		#Database Connection
		mydb = establish_connection()
		mycursor = mydb.cursor()

		sql=''
		#User Validation
		if login_device == '0':
			sql = "SELECT logged_in_app FROM dice_9_.verified_users WHERE useremail = %s AND app_token= %s"
		elif login_device == '1':
			sql = "SELECT logged_in_web FROM dice_9_.verified_users WHERE useremail = %s AND web_token= %s"
		
		values = (useremail , token)
		mycursor.execute(sql,values)
		res = mycursor.fetchall()[0][0]

		if (mycursor.rowcount == 0 or res != 1):
			mydb.disconnect()
			return json.dumps({'success':'false','msg':"Bad Parameters"})

		#SQL Injection
		if login_device == '0':
			sql = "UPDATE dice_9_.verified_users SET logged_in_app = 0, app_token = '{}'"
			sql = sql.format(token_hex(16))
		
		elif login_device == '1':
			sql = "UPDATE dice_9_.verified_users SET logged_in_web = 0, web_token = '{}'"
			sql = sql.format(token_hex(16))

		mycursor.execute(sql)
		mydb.commit()

		mydb.disconnect()
		return json.dumps({'success':'true','msg':"Logout Successfull"})

	except Exception as e:
		return json.dumps({'success':'false','msg':"Internal Server Error"})






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
		sql = "SELECT useremail FROM dice_9_.admin WHERE useremail = '{}' AND password = '{}'"
		sql = sql.format(obj.authoriser, obj.password)
		mycursor.execute(sql)
		mycursor.fetchall()
		if mycursor.rowcount == 0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Access denied"})
		
		#SQL Injection
		sql = """INSERT INTO dice_9_.admin (useremail,user_name,password,authorised_by,
				authorised_at) VALUES (%s,%s,%s,%s,%s)"""
		values = (obj.useremail,obj.username,obj.new_password,obj.authoriser,date_time)

		mycursor.execute(sql,values)
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Admin Added"})
	except Exception as e:
		return json.dumps({'success': 'false', 'msg': "Internal Server Error"})
