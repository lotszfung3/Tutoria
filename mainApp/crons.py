from django.db import models
from .models import *
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime,timezone, timedelta
from django_cron import CronJobBase, Schedule
from .utils import uploadImage,emailGateway,paymentGateway

class Lock_Session(CronJobBase):
	RUN_EVERY_MINS = 30
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.Lock_Session_cron'
	def do(self):
		now = datetime.now(timezone.utc)

		all_sessions = Session.objects.all()
		for session in all_sessions:
			if ((session.session_datetime  < (now + timedelta(hours=24))) & (session.state=='normal')):
				tutor = session.session_tutor
				student = session.session_student
				session.state='locked'
				session.save()
				emailGateway('session_lock', [student, tutor], session)


class End_Session(CronJobBase):
	RUN_EVERY_MINS = 30
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.End_Session_cron'
	def do(self):
		now = datetime.now(timezone.utc)

		all_sessions = Session.objects.all()
		for session in all_sessions:
			time_passed=now-session.session_datetime
			tut = session.session_tutor
			if (((time_passed>timedelta(minutes=30)) & (tut.tutor_type=='Contract'))) | (time_passed > timedelta(hours=1)):
				session.state='ended'
				session_transaction = session.transaction
				session_transaction.state = 'completed'

				# add tutor rate to tutor wallet
				tut_wallet = tut.wallet
				tut_wallet.amount += tut.hourly_rate
				tut_wallet.save()

				# add 5% to myTutor wallet
				admin = User.objects.get(username='admin')
				myTutor_wallet = admin.tutor.wallet
				myTutor_wallet.amount += (session_transaction.amount - tut.hourly_rate)
				myTutor_wallet.save()

				session.save()		
				session_transaction.save()		
				emailGateway('session_end', [session.session_student,tut], {"session_datetime":session.session_datetime,"link":request.get_host()+"/main/submitReviews/"+session.id})
				emailGateway('transaction_received', [session.session_student, tut], session)

