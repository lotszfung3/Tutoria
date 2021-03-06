from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime,timezone, timedelta
from django.db.models import Avg

# Create your models here.

class SubjectCode(models.Model):
	subject_code=models.CharField(max_length=8)
	@classmethod
	def getCodeList(cls):
		return SubjectCode.objects.all().values("subject_code")
		
	def __str__ (self):
		return self.subject_code
	
class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	phoneNumber=models.CharField(max_length=10)
	photo_url=models.CharField(max_length=30)
	@classmethod
	def create(cls, user):
		student = cls(user=user)
        # do something with the book
		return student
	def __str__ (self):
		return self.user.first_name


class Tutor(models.Model):
	phoneNumber=models.CharField(max_length=10)
	photo_url=models.CharField(max_length=30)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	#below different from student
	tutor_type=models.CharField(max_length=8,default="Private")#Contract/Private
	university=models.CharField(max_length=60)
	teach_course_code=models.ManyToManyField(SubjectCode)
	subject_tag=models.CharField(max_length=60)
	hourly_rate=models.IntegerField(default=100)
	introduction=models.TextField(default="I love programming")
	activated=models.BooleanField(default=True)#profiles show to public or not
	avg_review=models.IntegerField(default=-1)
	#schduel: tutor.schedule
	@classmethod
	def create(cls, user,phone,introduction,hourly_rate,subject_code,tag,atype,imagePath,uni):
		tutor = cls(user=user)
		tutor.phoneNumber=phone
		tutor.introduction=introduction
		tutor.hourly_rate=hourly_rate
		tutor.subject_tag=tag
		tutor.photo_url=imagePath
		tutor.university=uni
		if(atype=='c'):
			tutor.tutor_type="Contract"
		tutor.save()
		if(isinstance(subject_code,list)):
			for i in subject_code:
				tutor.teach_course_code.add(SubjectCode.objects.get(subject_code=i))
		else:
			tutor.teach_course_code.add(SubjectCode.objects.get(subject_code=subject_code))
        # do something with the book
		return tutor
	def updateAvgReview(self):
		if self.review_set.count()<3:
			self.avg_review=-1
		else:
			self.avg_review=round(self.review_set.aggregate(Avg('stars'))["stars__avg"])
		self.save()
			
	def getStudentRate(self):
		return int(((.05 * self.hourly_rate) + self.hourly_rate))
	def __str__ (self):
		return self.user.first_name	

class Session(models.Model):
	coupon_used=models.BooleanField()
	session_datetime=models.DateTimeField()
	state=models.CharField(max_length=10,default='normal')#cancelled/normal/ended/locked
	review_state=models.CharField(max_length=10,default='empty')#complete
	session_student=models.ForeignKey(Student)
	session_tutor=models.ForeignKey(Tutor)
	def __str__ (self):
		return str(self.id)


#record twice for students wallet and tutors wallet
class Transaction(models.Model):
	amount=models.DecimalField(max_digits=7, decimal_places=2,default=0)
	create_date=models.DateTimeField(auto_now_add=True)
	state=models.CharField(max_length=10,default='pending')#pending/completed/cancelled
	involved_session=models.OneToOneField(Session,null=True)
	payment_student=models.ForeignKey(Student)
	payment_tutor=models.ForeignKey(Tutor)
	@classmethod
	def create(cls,session,amount,student,tutor):
		if tutor is None:
			tutor=User.objects.get(first_name="Payment").tutor
		tran=cls(amount=amount,payment_student=student,payment_tutor=tutor,involved_session=session)
		if(tran.involved_session is None):#deposit/withdrawl
			tran.state="completed"
		tran.save()
		student.wallet.transactions.add(tran)
		# TRANSACTION IS CREATED WHEN PAYMENT IS CONFIRMED
		student.wallet.save()
		tutor.wallet.transactions.add(tran)
		tutor.wallet.save()
		return tran
	def __str__ (self):
		return str(self.id)
class Wallet(models.Model):
	amount=models.DecimalField(max_digits=7, decimal_places=2,default=0)
	student=models.OneToOneField(Student, on_delete=models.CASCADE)
	tutor=models.OneToOneField(Tutor, on_delete=models.CASCADE,null=True)
	transactions=models.ManyToManyField(Transaction)#should belong to two wallet
	@classmethod
	def create(cls,tutor,student):
		wallet = cls(tutor=tutor,student=student)
		wallet.save()
		return wallet
	def __str__(self):
		return str(self.student)	
	
class Schedule(models.Model):
	owned_tutor=models.OneToOneField(Tutor)
	start_date=models.DateField(auto_now_add=True)
	available_timeslot=models.CharField(max_length=280,default="a"*140) #a for available, b for booked(cannot be changed by tutor), c for cancelled(by tutor)
	@classmethod
	def create(cls, tutor):
		if(tutor.tutor_type=="Contract"):
			sch = cls(owned_tutor=tutor,available_timeslot="a"*280)		
		else:
			sch = cls(owned_tutor=tutor)
		return sch
	def daily_update(self):
		self.start_date=datetime.now(timezone.utc)+timedelta(days=1)
		if(self.owned_tutor.tutor_type=='Private'):
			self.available_timeslot=self.available_timeslot[10:]+'a'*10
		else:
			self.available_timeslot=self.available_timeslot[20:]+'a'*20
		self.save()
	def __str__ (self):
		return str(self.owned_tutor)+"'s schdedule"


class Review(models.Model):
	stars=models.IntegerField(default=3)
	comment=models.CharField(max_length=200)
	involved_session=models.OneToOneField(Session,null=True)
	written_student=models.ForeignKey(Student)
	for_tutor=models.ForeignKey(Tutor)
	written_date=models.DateTimeField(auto_now_add=True)
	course_code=models.CharField(max_length=10)
	state=models.CharField(max_length=10,default='empty')#completed
	is_anonymous=models.BooleanField(default=True)
	def __str__ (self):
		return str(self.involved_session)


class Coupon(models.Model):
	coupon_code=models.CharField(max_length=30)
	activate_date=models.DateTimeField('activate date')
	expiry_date=models.DateTimeField('expiry date')
	def __str__ (self):
		return self.coupon_code
	def isExpired(self):
		return this.expiry_date<datetime.now(timezone.utc) and this.activate_date>datetime.now(timezone.utc)
#trigger when user created
#user ->student (and/or) tutor 
#tutor ->schedule
@receiver(post_save, sender=Tutor)
def create_tutor_schedule(sender, instance, created, **kwargs):
	if created:
		Schedule.create(instance).save()
@receiver(post_save, sender=User)
def create_user_student(sender, instance, created, **kwargs):
	if created:
		Student.create(instance).save()
