import mysql.connector
import datetime
def establish_connection():
	mydb = mysql.connector.connect(
		host='mysql_db',
		user='root',
		password='root',
		database='users_dice9_'
	)
	return mydb

# Main

# Clearing cache_dice9_
print("-"*80)
print("    CLEARING : cache_dice9_ ...")
print(" *  Date_Time : "+str(date_time))

mydb = establish_connection()
mycursor = mydb.cursor()

date_time = datetime.datetime.now()

date_time1 = date_time - datetime.timedelta(minutes=8)
sql = f"DELETE FROM cache_dice9_.verify_email WHERE date_time < '{date_time1}'"
mycursor.execute(sql)

date_time2 = date_time - datetime.timedelta(days=8)
sql = f"DELETE FROM cache_dice9_.pending_req_staff WHERE date_time < '{date_time2}'"
mycursor.execute(sql)

mydb.commit()
mydb.disconnect()

print("    Cleared Successfully ..!!!")
print("-"*80)

