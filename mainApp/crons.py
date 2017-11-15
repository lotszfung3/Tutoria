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

		all_sessions = Sessions.objects.all()
		for session in all_sessions:
			if ((session.session_datetime  < (now + timedelta(hours=24))) & (session.state=="normal")):
				tutor = session.session_tutor
				student = session.session_student
				session.state="locked"
				session.save()
				emailGateway('session_lock', [session.session_student,session.session_tutor], session)


class End_Session(CronJobBase):
	RUN_EVERY_MINS = 30
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.End_Session_cron'
	def do(self):
		now = datetime.now(timezone.utc)

		all_sessions = Sessions.objects.all()
		for session in all_sessions:
			if ((session.session_datetime + timedelta(hours=1)) < now) & (session.state=="locked"):
				session.state="ended"
				session.save()
				emailGateway('session_end', [session.session_student,session.session_tutor], session)
				
				tut = session.session_tutor
				transAMT = tut.hourly_rate + (.05 * tut.hourly_rate)
				transaction = Transaction(involved_session=session.id, amount=transAMT, payment_student=session.session_student, payment_tutor=session.session_tutor)

				tut.amount += tut.hourly_rate
				transaction.state="completed"
				transaction.save()
				emailGateway('transaction_received', [session.session_student, session.session_tutor], this_session)

