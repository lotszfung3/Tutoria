from django.contrib.auth.models import User
from django.test import TestCase,Client
from .utils import getSlotIdfromDateTime,uploadImage
from .models import Tutor,SubjectCode
from django.contrib.auth.password_validation import validate_password
# Create your tests here.
class mainTestCase(TestCase):
	def setUp1(self):
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
		tutor=Tutor.objects.all()[0]
		tutor.subject_tag.add(SubjectCode.objects.get(subject_code="COMP3258"))
		tutor.subject_tag.add(SubjectCode.objects.get(subject_code="COMP3278"))
		tutor.save()
		
