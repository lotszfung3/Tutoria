from django.apps import AppConfig
from .utils import test

class MainappConfig(AppConfig):
	name = 'mainApp'
	#def ready(self):