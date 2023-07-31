class Verify_Email():
	def __init__(self, request):
		from dice9api import nullSafe, hashlib

		self.useremail = nullSafe(request.form.get('useremail'))
		self.otp = nullSafe(str(request.form.get('otp')))
		self.otp = hashlib.md5(self.otp.encode()).hexdigest()
		

class Staff_Req():
	def __init__(self, request):
		from dice9api import nullSafe, fernet
		
		#encryption-rule: "request_id|*|admin_token|*|useremail"
		temp = nullSafe(request.form.get('a_token'))
		temp = fernet.decrypt(temp.encode()).decode().split('|*|')
		self.u_token = temp[0]
		self.admin_token = temp[1]
		self.useremail = temp[2]