import mysql.connector
import datetime
def establish_connection():
	mydb = mysql.connector.connect(
		host='localhost',
		user='root',
		password='root',
		database='dice_9_'
	)
	return mydb

# Main
mydb = establish_connection()
mycursor = mydb.cursor()

date_time = datetime.datetime.now()

date_time1 = date_time - datetime.timedelta(minutes=8)
sql = f"DELETE FROM dice_9_.enroll_mail_cache WHERE date_time < '{date_time1}'"
mycursor.execute(sql)

print("----------------------------------------------------------")
print("    CLEARING : TABLE 'enroll_mail_cache' ...")
print(" *  Date_Time : "+str(date_time))
print(" *  Total Rows Effected :"+str(mycursor.rowcount)+"\n")
print("    TABLE 'enroll_mail_cache' : CLEARED Successfully ..!!!")
print("----------------------------------------------------------")

date_time2 = date_time - datetime.timedelta(days=8)
sql = f"DELETE FROM dice_9_.waiting_staff_cache WHERE date_time < '{date_time2}'"
mycursor.execute(sql)

print("----------------------------------------------------------")
print("    CLEARING : TABLE 'waiting_staff_cache' ...")
print(" *  Date_Time : "+str(date_time))
print(" *  Total Rows Effected :"+str(mycursor.rowcount)+"\n")
print("    TABLE 'waiting_staff_cache' : CLEARED Successfully ..!!!")
print("----------------------------------------------------------")

mydb.commit()
mydb.disconnect()