from django.db import models
from .models import *
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime,timezone, timedelta
from django_cron import CronJobBase, Schedule
from .utils import uploadImage,emailGateway,paymentGateway

class Update_Session_States(CronJobBase):
	RUN_EVERY_MINS = 30
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.Update_Session_States_cron'
	def do(self):
		all_sessions = Session.objects.all()
		normal_sessions = []
		for x in all_sessions:
			if x.state=='normal':
				normal_sessions.append(x)
		for session in normal_sessions:
			now = datetime.now(timezone.utc)
			if (session.session_datetime + timedelta(hours=1)) < now:
				session.state='ended'
				session.session_tutor.amount = session.session_tutor.amount + session.session_tutor.hourly_rate
				session.session_tutor.save()
				session.save()
			elif (session.session_datetime - timedelta(hours=24)) < now:
				session.state='soon'
				session.save()
# update the state of any transaction that has an associated session with state 'ended' to completed
class Update_Transaction_States(CronJobBase):
	RUN_EVERY_MINS = 30
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.Update_Transaction_States_cron'
	def do(self):
		all_transactions = Transaction.objects.all()
		pending_transactions = []
		for x in all_transactions:
			if x.state=='pending':
				pending_transactions.append(x)
		for transaction in pending_transactions:
			if(transaction.involved_session.state=='ended'):
				this_session = transaction.involved_session
				transaction.state='completed'
				#TODO: send email notification to Tutor and Student that they have received payment
				emailGateway('transaction_received', [this_session.session_student, this_session.session_tutor], this_session)
				transaction.save()
