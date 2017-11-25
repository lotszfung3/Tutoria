from .models import *
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime,timezone, timedelta
from django_cron import CronJobBase, Schedule
from .utils import uploadImage,emailGateway,paymentGateway

class Lock_Session(CronJobBase):
	RUN_EVERY_MINS = 1
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.Lock_Session_cron'
	def do(self):
		print("qwe")
		now = datetime.now(timezone.utc)

		all_sessions = Session.objects.filter(state='normal')
		for session in all_sessions:
			if session.session_datetime  < (now + timedelta(days=1)):
				
				# lock session
				session.state = 'locked'
				session.save()

				# send email
				tutor = session.session_tutor
				student = session.session_student
				emailGateway('session_lock', [student, tutor], session)


class End_Session(CronJobBase):
	RUN_EVERY_MINS = 1
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.End_Session_cron'
	def do(self):
		print("asd")
		now = datetime.now(timezone.utc)+timedelta(days=4)

		# all potentially ended sessions
		all_sessions=Session.objects.filter(state='locked')
		for session in all_sessions:
			time_passed=now-session.session_datetime
			if (time_passed>timedelta(hours=1) or (time_passed>timedelta(minutes=30) and session.session_tutor.tutor_type=="Contract")):
				session_transaction = Transaction.objects.get(involved_session=session)

				# mark session as ended
				session.state='ended'
				session.save()

				# add tutor rate to tutor wallet
				tut = session.session_tutor
				tut_wallet = tut.wallet
				tut_wallet.amount += tut.hourly_rate
				tut_wallet.save()

				# add 5% to myTutor wallet
				admin = User.objects.get(username='admin')
				myTutor_wallet = admin.tutor.wallet
				myTutor_wallet.amount += (session_transaction.amount - tut.hourly_rate)
				myTutor_wallet.save()

				# mark transaction as completed
				session_transaction.state = 'completed'
				session_transaction.save()

				emailGateway('session_end', [session.session_student,tut], session)
				emailGateway('transaction_received', tut, session)

class New_Day_Schedule(CronJobBase):
	RUN_AT_TIMES=['00:00']
	schedule=Schedule(run_at_times=RUN_AT_TIMES)
	code='Tutoria.New_Day_Schedule_cron'
	def do(self):
		for sch in Schedule.objects.all():
			sch.daily_update()
