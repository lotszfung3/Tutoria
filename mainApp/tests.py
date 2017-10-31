from django.test import TestCase
from .utils import getSlotIdfromDateTime
from .models import Session
# Create your tests here.
class mainTestCase(TestCase):
    def setUp(self):
        self.session0=Session.objects.all()
    def test_time(self):
        print(self.session0)
