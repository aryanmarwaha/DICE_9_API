class EnrollingUser:
	def __init__(self, request):
		from dice9api import nullSafe

		self.useremail = nullSafe(request.form.get('useremail'))


class RegisteringUser:
	def __init__(self, request):
		from dice9api import nullSafe

		self.useremail = nullSafe(request.form.get('useremail'))
		self.token = nullSafe(request.form.get('token'))
		self.password = nullSafe(request.form.get('password'))
		self.role = nullSafe(request.form.get('role'))
		self.firstname = nullSafe(request.form.get('firstname'))
		self.secondname = nullSafe(request.form.get('secondname'))
		self.age = nullSafe(request.form.get('age'))
		self.gender = nullSafe(request.form.get('gender'))
		self.mobile_no = nullSafe(request.form.get('mobile'))


class RegisteringStudent:
	def __init__(self, request):
		from dice9api import nullSafe
		
		self.rollno = nullSafe(request.form.get('rollno'))
		self.branch = nullSafe(request.form.get('branch'))
		self.hosteler = nullSafe(request.form.get('hosteler'))
		self.address = nullSafe(request.form.get('address'))
		self.interests = nullSafe(request.form.get('interests'))
		self.skills = nullSafe(request.form.get('skills'))
		self.open_to_work = nullSafe(request.form.get('open_to_work'))


class RegisteringAdmin:
	def __init__(self, request):
		from dice9api import nullSafe

		self.useremail = nullSafe(request.form.get('useremail'))
		self.username = nullSafe(request.form.get('username'))
		self.new_password = nullSafe(request.form.get('new_password'))
		self.authoriser = nullSafe(request.form.get('authoriser'))
		self.password = nullSafe(request.form.get('password'))