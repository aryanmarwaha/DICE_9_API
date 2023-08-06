class Validate_OTP():
	def __init__(self, request):
		from dice9api import nullSafe,hashlib

		self.useremail = nullSafe(request.form.get('useremail'))
		self.device = nullSafe(request.form.get('device'))
		self.otp = nullSafe(str(request.form.get('otp')))
		self.otp = hashlib.md5(self.otp.encode()).hexdigest()

class Reset_Password():
	def __init__(self,request):
		from dice9api import nullSafe,hashlib

		self.useremail = nullSafe(request.form.get('useremail'))
		self.token = nullSafe(request.form.get('token'))
		self.device = nullSafe(request.form.get('device'))
		self.password = nullSafe(str(request.form.get('password')))
		self.password = hashlib.md5(self.password.encode()).hexdigest()
		self.login = nullSafe(str(request.form.get(login)))

		if self.device not in ['0','1']:
			raise ValueError("device value not satisfied")
		if self.login != '1':
			self.login = '0'