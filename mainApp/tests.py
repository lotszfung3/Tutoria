from django.contrib.auth.models import User
from django.test import TestCase,Client
from .utils import getSlotIdfromDateTime
from .models import Tutor,SubjectCode
# Create your tests here.
class mainTestCase(TestCase):
	def setUp(self):
		sc=SubjectCode.objects.create(subject_code="COMP3258")
		sc.save()
		sc=SubjectCode.objects.create(subject_code="COMP3279")
		sc.save()
		c=Client()
		c.post('/main/register',{"name":"Frankie",
								 "username":"fra123",
								 "email":"fra123@gmail.com",
								 "password":"mnbv1234",
								 "role":"t",
								 "phone":"12345678",
								 "uni":"HKU",
								 "tag":"#Python",
								 "type":"p",
								 "hourlyRate":100,
								 "description":"i like programming",
								 "subject":"COMP3258",
								 "subject":"COMP3279",
								})
	def test_main(self):
		self.user=User.objects.all()[0]
		print(self.user.tutor.schedule.available_timeslot)
		
		
		
