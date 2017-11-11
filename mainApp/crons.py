from django.db import models
from .models import *
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime,timezone, timedelta
from django_cron import CronJobBase, Schedule

class Update_Session_States(CronJobBase):
    RUN_EVERY_MINS = 30
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Tutoria.Update_Session_States_cron'
    #get all type normal sessions
    all_sessions = Session.objects.all()
    def get_normal_sessions(lst):
    	new_lst = []
    	for x in lst:
    		if x.state=='normal':
    			new_lst.append(x)
    	return new_lst
    def do(self):
    	normal_sessions = get_normal_sessions(all_sessions)
    	for session in normal_sessions:
    		if (session.session_datetime + timedelta(hours=1)) < datetime.now(timezone('UTC')):
    			session.state='ended'
    			session.session_tutor.amount = session.session_tutor.amount + session.session_tutor.hourly_rate
    			session.session_tutor.save()
    			session.save()
    		elif (session.session_datetime - timedelta(hours=24)) > datetime.now(timezone('UTC')):
    			session.state='soon'
    			session.save()

# update the state of any transaction that has an associated session with state 'ended' to completed
class Update_Transaction_States(CronJobBase):
	RUN_EVERY_MINS = 30
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'Tutoria.Update_Transaction_States_cron'
	all_transactions = Transaction.objects.all()
	def get_pending_transactions(lst):
		new_list = []
		for x in list:
			if x.state=='pending':
				new_lst.append(x)
		return new_list
	def do(self):
		pending_transactions = get_pending_transactions(all_transactions)
		for transaction in pending_transactions:
			if(transaction.involved_session.state=='ended'):
				transaction.state='completed'
				transaction.save()
