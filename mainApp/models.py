from django.db import models

# Create your models here.
#partiat models only (23/10)
class Student(models.Model):
	name=models.CharField(max_length=60)
	email=models.CharField(max_length=60)
	phoneNumber=models.CharField(max_length=10)
	photo_url=models.CharField(max_length=30)
	owned_wallet=models.OneToOneField(Wallet)


class Wallet(models.Model):
	#its own can be accessed by wallet.student / wallet.tutor if exist
	amount=models.IntegerField(default=0)
	#its transactions list can be accessed wallet.transaction_set

class Tutor(models.Model):
	name=models.CharField(max_length=60)
	email=models.CharField(max_length=60)
	phoneNumber=models.CharField(max_length=10)
	photo_url=models.CharField(max_length=30)
	owned_wallet=models.OneToOneField(Wallet)
	#below different from student
	tutor_type=models.CharField(max_length=7)#contract/private
	university=models.CharField(max_length=60)
	teach_course_code=models.CharField(max_length=10)
	subject_tag=models.CharField(max_length=60)
	hourly_rate=models.IntegerField(default=100)
	introduction=models.CharField(max_length=200)
	activated=models.CharField(max_length=1)#Y/N
	avg_review=models.IntegerField(default=-1)

class Session(models.Model):
	

class Schedule(models.Model):

#record twice for students wallet and tutors wallet
class Transaction(models.Model):
	in_wallet=models.ForeignKey(Wallet,on_delete=models.CASCADE)
class Review(models.Model):

class Coupon(models.Model):
	coupon_code=models.CharField(max_length=30)
	expiry_date=models.DateTimeField('expiry date')