from django.db import models

# Create your models here.
class SubjectCode(models.Model):
	subject_code=models.CharField(max_length=8)

class Wallet(models.Model):
	#its own can be accessed by wallet.student / wallet.tutor if exist
	amount=models.IntegerField(default=0)
	#its transactions list can be accessed wallet.transaction_set

class Student(models.Model):
	name=models.CharField(max_length=60)
	email=models.CharField(max_length=60)
	phoneNumber=models.CharField(max_length=10)
	photo_url=models.CharField(max_length=30)
	owned_wallet=models.OneToOneField(Wallet)


class Tutor(models.Model):
	name=models.CharField(max_length=60)
	email=models.CharField(max_length=60)
	phoneNumber=models.CharField(max_length=10)
	photo_url=models.CharField(max_length=30)
	owned_wallet=models.OneToOneField(Wallet)
	#below different from student
	tutor_type=models.CharField(max_length=7)#contract/private
	university=models.CharField(max_length=60)
	teach_course_code=models.ManyToManyField(SubjectCode)
	subject_tag=models.CharField(max_length=60)
	hourly_rate=models.IntegerField(default=100)
	introduction=models.CharField(max_length=200)
	activated=models.BooleanField()#profiles show to public or not
	avg_review=models.IntegerField(default=-1)
	#schduel: tutor.schedule

class Session(models.Model):
	coupon_used=models.BooleanField()
	session_datetime=models.DateTimeField()
	state=models.CharField(max_length=10,default='normal')#cancelled/normal/ended/in-progress
	session_student=models.ForeignKey(Student)
	session_tutor=models.ForeignKey(Tutor)
	
#record twice for students wallet and tutors wallet
class Transaction(models.Model):
	in_wallet=models.ForeignKey(Wallet,on_delete=models.CASCADE)
	amount=models.IntegerField(default=0)
	state=models.CharField(max_length=10,default='pending')#pending/completed/cancelled
	involved_session=models.OneToOneField(Session)
	payment_student=models.ForeignKey(Student)
	payment_tutor=models.ForeignKey(Tutor)



class Schedule(models.Model):
	owned_tutor=models.OneToOneField(Tutor)
	start_date=models.DateField()
	available_timeslot=models.BinaryField()


class Review(models.Model):
	stars=models.IntegerField(default=3)
	comment=models.CharField(max_length=200)
	written_student=models.ForeignKey(Student)
	for_tutor=models.ForeignKey(Tutor)
	written_date=models.DateTimeField(auto_now_add=True)
	course_code=models.CharField(max_length=10)

class Coupon(models.Model):
	coupon_code=models.CharField(max_length=30)
	expiry_date=models.DateTimeField('expiry date')

