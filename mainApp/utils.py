from datetime import datetime, timezone
from django.db import models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

email_format='''
Email Title: Tutoria :{}
Email recipient:{}
Email body:{}
'''
def getSlotIdfromDateTime(s_date,tutor_type):
    roundedA = s_date.replace(hour = 0, minute = 0)
    roundedB = datetime.now(timezone.utc).replace(hour = 0, minute = 0,second=0,microsecond=0)
    days = (roundedA - roundedB).days
    print("days: "+str(roundedA)+" "+str(roundedB))
    if(tutor_type=="Private"):
        days*=10
        days+=s_date.hour-1
    else:
        days*=20
        days+=(s_date.hour-1)*2+(0 if s_date.minute==0 else 1)
    return days
def uploadImage(file,user_id):
	with open(path,'wb') as han:
		han.write(file.read())
		han.close()
def emailGateway(email_type,recipients,info):#recipent:[student name, tutor name]
    if(email_type=='session_cancel'):
        print(email_format.format(" Session has been cancelled",recipients[0],"The session at {} has been cancelled.\n The amount {} has been refunded to your wallet.".format(info.datetime,info.amount)))
        print(email_format.format(" Session has been cancelled",recipients[1],"The session at {} has been cancelled.".format(info.datetime)))
    elif(email_type=='session_book'):
        print(email_format.format(" Session has been booked",recipients[0],"The session at {} has been booked.\n The amount {} including commission fee {} has been deducted from your wallet.".format(info.datetime,info.amount,info.commission)))
        print(email_format.format(" Session has been booked",recipients[1],"The session at {} has been booked.".format(info.datetime)))
    elif(email_type=='session_end'):
        print(email_format.format(" Session has ended",recipients[0],"The session at {} has end.\n Please use the following link to finish a review form:\n {}".format(info.datetime,info.link)))
        print(email_format.format(" Session has end",recipients[1],"The session at {} has end.\n The amount {} has been transferred to your wallet.".format(info.datetime,info.amount)))
    elif(email_type=='transaction_received'):
        print(email_format.format(" Transaction has made.",recipients[0],"The transaction of id {} has made.\n The amount {} has been deducted to your wallet.".format(info.datetime,info.amount)))
        print(email_format.format(" Transaction has made.",recipients[1],"The transaction of id {} has made.\n The amount {} has been added to your wallet".format(info.datetime,info.amount)))
    elif(email_type=='wallet_handle'):
        print(email_format.format(" Wallet transaction is done",recipients,"The amount {} has been {} your wallet".format(abs(info.amount),"added to" if info.amount>0 else "deducted from")))
    elif(email_type=='resetPw'):
        print(email_format.format("Reset your password",recipients,"You can use the following link to reset your password:\n{}".format(info)))
def paymentGateway(user,amount):
    user.amount+=amount
    user.save()
    emailGateway("wallet_handle",user.name,{"amount":amount})