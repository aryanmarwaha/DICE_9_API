from dice9api import mail,Message,render_template

def send_reset_password_otp(useremail, otp_token):
	ttl = 5
	while True:
		try:
			msg = Message("One Time Password for Password Reset is {}".format(otp_token),
					sender="DICE chitkara university",
					recipients=[useremail])

			msg.body = f"One Time Password for Password Reset is {otp_token}. This OTP will expire with in 8 minutes."
			msg.html = render_template("reset_password_otp.html", otp_token=otp_token)
			mail.send(msg)
			return
		except Exception as e:
			ttl-=1
			if ttl==0:
				raise ValueError("Mail Not Send")
			pass