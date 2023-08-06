from dice9api import mail, Message, render_template
from dice9api import datetime, fernet

def send_email_verification_otp(useremail, otp_token):
	ttl = 5
	while True:
		try:
			msg = Message("One Time Password for Email Verification is {}".format(otp_token),
					sender="DICE chitkara university",
					recipients=[useremail])
			msg.body = f"One Time Password for Email Verification is {otp_token}. This OTP will expire with in 8 minutes."
			msg.html = render_template("mail_verify_otp.html", otp_token=otp_token)
			mail.send(msg)
			return
		except Exception as e:
			ttl-=1
			if ttl==0:
				raise ValueError("Mail Not Send")
			pass

def send_staff_request(mydb,username, useremail, token):
	ttl = 5
	while True:
		try:
			# SQL --fetch admins
			mycursor = mydb.cursor()
			mycursor.execute("SELECT useremail,user_name,user_key from users_dice9_.admin")
			admins_ = mycursor.fetchall()

			#Parameter Intitialization
			date_time = str(datetime.datetime.now()).split('.')[0]
			role_ = "Staff"
			#Email Handler
			subject = f"Someone is asking your permission after recently applying for a {role_} role."
			sender = "DICE chitkara university"

			for admin in admins_:
			
				#encryption-rule: "request_id|*|admin_token|*|useremail"
				t_token = token + '|*|' + admin[2] + '|*|' + useremail
				a_token = fernet.encrypt(t_token.encode()).decode()
				
				msg = Message(subject, sender=sender, recipients=[admin[0]])
				msg.html = render_template("role_request.html",admin_name=admin[1],
											user_name=username,useremail=useremail,
											date_time=date_time,role=role_,
											a_token=a_token)
				mail.send(msg)
			return
		except Exception as e:
			ttl-=1
			if ttl==0:
				raise ValueError("Mail Not Send || "+str(e))

def send_new_admin_alert(mydb,new_admin_email,new_admin_name,authoriser,date_time):
	ttl = 5
	while True:
		try:
			# SQL --fetch admins
			mycursor = mydb.cursor()
			mycursor.execute("SELECT useremail,user_name from users_dice9_.admin")
			admins_ = mycursor.fetchall()

			#Parameter Intitialization
			date_time = str(datetime.datetime.now()).split('.')[0]

			#Email Handler
			subject = f"URGENT: Security Alert - New Admin Added to the Organization"
			sender = "DICE chitkara university"

			for admin in admins_:

				msg = Message(subject, sender=sender, recipients=[admin[0]])
				msg.html = render_template("security_alert.html",new_admin_email=new_admin_email,
											new_admin_name=new_admin_name,
											authoriser=authoriser,
											date_time=date_time)
				mail.send(msg)
			return
		except Exception as e:
			ttl-=1
			if ttl==0:
				raise ValueError("Mail Not Send || "+str(e))