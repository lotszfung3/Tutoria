from datetime import datetime, timezone
from django.db import models
from django.utils.timezone import localtime
email_format='''
Email
---------------------------------------
Email Title: Tutoria :{}
Email recipient:{}
Email body:{}
---------------------------------------
'''
def getSlotIdfromDateTime(s_date,tutor_type):
    roundedA = s_date.replace(hour = 0, minute = 0)
    roundedB = datetime.now(timezone.utc).replace(hour = 0, minute = 0,second=0,microsecond=0)
    days = (roundedA - roundedB).days
    if(tutor_type=="Private"):
        days*=10
        days+=s_date.hour-1
    else:
        days*=20
        days+=(s_date.hour-1)*2+(0 if s_date.minute==0 else 1)
    return days
def uploadImage(file,user_id):
	tempPath='profilepic/{}.jpg'.format(str(user_id))
	with open('./mainApp/static/'+tempPath,'wb') as han:
		han.write(file.read())
		han.close()
	
def emailGateway(email_type,recipients,info):#recipent:[student name, tutor name]
    if(email_type=='session_cancel'):
        print(email_format.format(" Session has been cancelled",recipients[0],"Your Tutoria session at {} has been cancelled.\n The amount ${} has been refunded to your wallet.".format(localtime(info["datetime"]),info["amount"])))
        print(email_format.format(" Session has been cancelled",recipients[1],"Your Tutoria session at {} has been cancelled.".format(localtime(info["datetime"]))))
    elif(email_type=='session_book'):
        print(email_format.format(" Session has been booked",recipients[0],"The session at {} has been booked.\n The amount {} including commission fee {} has been deducted from your wallet.".format(localtime(info["datetime"]),info["amount"],info["commission"])))
        print(email_format.format(" Session has been booked",recipients[1],"The session at {} has been booked.".format(localtime(info["datetime"]))))
    elif(email_type=='session_book_coupon'):
        print(email_format.format(" Session has been booked",recipients[0],"The session at {} has been booked.\n The amount {} has been deducted from your wallet.".format(localtime(info["datetime"]),info["amount"])))
        print(email_format.format(" Session has been booked",recipients[1],"The session at {} has been booked.".format(localtime(info["datetime"]))))
    elif(email_type=='session_end'):
        print(email_format.format(" Session has ended",recipients[0],"The session (ID={}) at {} has ended.\n Your payment will be processed shortly.\n Please use the following link to submit a review: http://127.0.0.1:8000/main/submitReviews/{} \n".format(info.id,info.session_datetime,info.id)))
        print(email_format.format(" Session has ended",recipients[1],"The session (ID={}) at {} has ended.\n Your transaction will be processed shortly.".format(info.id,info.session_datetime)))
    elif(email_type=='session_lock'):
        print(email_format.format(" Upcoming Session", recipients[0], "You have a session (ID={}) with {} at {}. You can no longer cancel this session. ".format(info.id,info.session_tutor,info.session_datetime)))
        print(email_format.format(" Upcoming Session", recipients[1], "You have a session (ID={}) with {} at {}. They can no longer cancel this session. ".format(info.id,info.session_student,info.session_datetime)))
    elif(email_type=='transaction_received'):
        print(email_format.format(" Transaction completed.",recipients.name,"The transaction for your Tutoria session (ID={}) has been processed.\n {} has been added to your wallet".format(info.id,info.session_tutor.hourly_rate)))
    elif(email_type=='wallet_handle'):
        print(email_format.format(" Wallet transaction is done",recipients,"The amount {} has been {} your wallet".format(abs(info.amount),"added to" if info.amount>0 else "deducted from")))
    elif(email_type=='resetPw'):
        print(email_format.format("Reset your password",recipients,"You can use the following link to reset your password:\n{}".format(info)))

def paymentGateway(user,amount):
    wallet=user.student.wallet
    tempAmount=wallet.amount+amount
    wallet.amount=tempAmount
    wallet.save()
    return tempAmount
def test():
	print("asd")