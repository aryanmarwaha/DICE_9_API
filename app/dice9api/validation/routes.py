from dice9api import Blueprint,render_template
from dice9api import establish_connection
from dice9api import nullSafe,token_hex,json
from dice9api import request, datetime
from dice9api import fernet

from dice9api.validation.objects import Verify_Email, Staff_Req

# main:
validate = Blueprint('validate',__name__,
					template_folder='templates',
					static_folder='/validation/static')


@validate.route("/api/verify_email",methods=['POST'])
def verify_email():

	#Parameter Initialization
	try:
		req = Verify_Email(request)
		date_time = datetime.datetime.now()
	except Exception as e:
		return json.dumps({'success': 'false', 'msg': "Bad Parameters"+str(e)})
	
	try:
		#Database Connection
		mydb = establish_connection()
		mycursor= mydb.cursor()

		#User Validation
		sql = "SELECT date_time FROM cache_dice9_.verify_email WHERE useremail = %s AND secret_Token = %s"
		values = (req.useremail,req.otp)
		mycursor.execute(sql,values)
		enroll_dt = mycursor.fetchall()
		
		#Validating OTP
		if mycursor.rowcount == 0:
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "Bad Parameters"})
		
		elif (date_time-enroll_dt[0][0]).total_seconds() > 480 :
			sql = "DELETE FROM cache_dice9_.verify_email WHERE useremail ='{}'"
			sql = sql.format(req.useremail)
			mycursor.execute(sql)

			mydb.commit()
			mydb.disconnect()
			return json.dumps({'success': 'false', 'msg': "OTP Expired"})

		#Generating Random token and password
		token_ = token_hex(16)
		paswd_ = token_hex(16)
		
		#SQL Injection
		sql = "DELETE FROM cache_dice9_.verify_email WHERE useremail ='{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)
		mycursor.fetchall()
		
		sql = "INSERT INTO users_dice9_.verified_users (useremail,email_verified_at,password,app_token,web_token) VALUES(%s,%s,%s,%s,%s)"
		values = (req.useremail,date_time,paswd_,token_,token_)
		mycursor.execute(sql,values)
		mycursor.fetchall()
		
		mydb.commit()
		mydb.disconnect()
		return json.dumps({'success': 'true', 'msg': "Email Verification Successful", 'token': token_})
	except Exception as e:
		print(e)
		return json.dumps({'success': 'false', 'msg': "Some Error Occured"})


@validate.route("/api/approve_staff_req",methods=['POST'])
def approve_staff_req():
	# Parameter Initialisation
	try:
		req = Staff_Req(request)
		date_time = datetime.datetime.now()
	except:
		print("yo")
		return render_template('failed_action.html', title="Failure", msg="Access denied!",
			reply="{'success': 'false', 'msg': 'Bad Parameters'}")
	try:
		mydb = establish_connection()
		mycursor = mydb.cursor()

		#Admin Validation
		sql = "SELECT user_name FROM users_dice9_.admin WHERE user_key = '{}'"
		sql = sql.format(req.admin_token)
		mycursor.execute(sql)

		admin_name = mycursor.fetchall()
		if mycursor.rowcount == 0:
			print("ho")
			return render_template('failed_action.html', title="Failure", msg="Access denied!",
				reply="{'success': 'false', 'msg': 'Bad Parameters'}")
		admin_name = admin_name[0][0]

		#User Validation
		sql = "SELECT date_time from cache_dice9_.pending_req_staff WHERE useremail = '{}' AND request_id='{}'"
		sql = sql.format(req.useremail,req.u_token)
		mycursor.execute(sql)
		res_dt = mycursor.fetchall()

		if mycursor.rowcount == 0:
			return render_template('failed_action.html', title="Failure", msg="Access denied!",
				reply="{'success': 'false', 'msg': 'Bad Parameters'}")

		elif (date_time-res_dt[0][0]).days >= 2 :
			sql = "DELETE FROM cache_dice9_.pending_req_staff WHERE useremail ='{}'"
			sql = sql.format(req.useremail)
			mycursor.execute(sql)

			mydb.commit()
			mydb.disconnect()
			return render_template('failed_action.html', title="Failure", msg="Deadline Exceeded!",
				reply="{'success': 'false', 'msg': 'Approval Time Exceeded'}")
		
		# Switching User from guest to staff
		
		# Deleting user-entry from waiting_staff_chache
		sql = "DELETE FROM cache_dice9_.pending_req_staff where useremail = '{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)

		# fetching user-details from guest_user_info
		sql = "SELECT * FROM users_dice9_.guest_info where useremail = '{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)
		user_data = mycursor.fetchall()[0]

		# Deleting user-entry from guest_user_info
		sql = "DELETE FROM users_dice9_.guest_info where useremail = '{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)

		#SQL Injection
		sql = """
			INSERT INTO users_dice9_.staff_info (useremail,first_name,second_name,
			age,gender,approved_by,approved_at) VALUES(%s,%s,%s,%s,%s,%s,%s)"""
		values = (nullSafe(user_data[0]),nullSafe(user_data[1]),nullSafe(user_data[2]),
			nullSafe(user_data[3]),nullSafe(user_data[4]),admin_name,date_time)
		mycursor.execute(sql,values)

		#Updating role
		sql = "UPDATE users_dice9_.verified_users SET role = 2 where useremail = '{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)

		mydb.commit()
		mydb.disconnect()
		return render_template('success_action.html', title="Success",
			reply="{'success': 'true', 'msg': 'User Switched From Guest To Staff'}")
	except Exception as e:
		print(str(e))
		mydb.disconnect()
		return render_template('failed_action.html', title="Some Error Occured", msg="Try Again!",
			reply="{'success': 'false', 'msg': 'Some Error Occured: '"+str(e)+"}")


@validate.route("/api/reject_staff_req", methods=['POST'])
def reject_staff_req():
	# Parameter Initialisation
	try:
		req = Staff_Req(request)
		date_time = datetime.datetime.now()
	except:
		return render_template('failed_action.html', title="Failure", msg="Access denied!",
				reply="{'success': 'false', 'msg': 'Bad Parameters'}")
	try:
		mydb = establish_connection()
		mycursor = mydb.cursor()

		#Admin Validation
		sql = "SELECT user_name FROM users_dice9_.admin WHERE user_key = '{}'"
		sql = sql.format(req.admin_token)
		mycursor.execute(sql)
		admin_name = mycursor.fetchall()
		if mycursor.rowcount == 0:
			return render_template('failed_action.html', title="Failure", msg="Access denied!",
				reply="{'success': 'false', 'msg': 'Bad Parameters'}")
		admin_name = admin_name[0][0]

		#User Validation
		sql = "SELECT useremail from cache_dice9_.pending_req_staff WHERE useremail = '{}' AND request_id = '{}'"
		sql = sql.format(req.useremail,req.u_token)
		mycursor.execute(sql)
		res_dt = mycursor.fetchall()
		if mycursor.rowcount == 0:
			return render_template('failed_action.html', title="Failure", msg="Access denied!",
				reply="{'success': 'false', 'msg': 'Bad Parameters'}")

		# Deleting user-entry from waiting_staff_chache
		sql = "DELETE FROM cache_dice9_.pending_req_staff where useremail = '{}'"
		sql = sql.format(req.useremail)
		mycursor.execute(sql)

		mydb.commit()
		mydb.disconnect()
		return render_template('success_action.html', title="Success",
			reply="{'success': 'true', 'msg': 'Action Successfull'}")
	except Exception as e:
		mydb.disconnect()
		return render_template('failed_action.html', title="Failure", msg="Try Again!",
			reply="{'success': 'false', 'msg': 'Some Error Occured: '"+str(e)+"}")