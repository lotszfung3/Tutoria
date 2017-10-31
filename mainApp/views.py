from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from datetime import date
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required
def findTutors(request):
	return render(request,'mainApp/findTutors.html',{'std':request.user.student})

#list of tutors with requirement in side request.GET
@login_required
def tutorsList(request):
	tutor_query = []
	uni = request.GET['university']
	if(uni!=''):
		tutor_query.append(Tutor.objects.filter(university=uni))

	tag = request.GET['tag']
	if(tag!=''):
		tutor_query.append(Tutor.objects.filter(subject_tag__contains=tag))

	lprice = request.GET['lprice']
	if(lprice!=''):
		lprice_i = int(lprice)
		tutor_query.append(Tutor.objects.filter(hourly_rate__gte=lprice_i))

	hprice = request.GET['hprice']
	if(hprice!=''):
		hprice_i = int(hprice)
		tutor_query.append(Tutor.objects.filter(hourly_rate__gte=hprice_i))

	if(request.GET['type']=='c'):
		tutor_query.append(Tutor.objects.filter(tutor_type='Contract'))
	elif(request.GET['type']=='p'):
		tutor_query.append(Tutor.objects.filter(tutor_type='Private'))

	tutor_query.append(Tutor.objects.filter(activated=True))

	tutor_all = Tutor.objects.all()

	for i in range(len(tutor_query)):
		tutor_all = tutor_all.intersection(tutor_query[i])	

	tutor_list = []
	course = request.GET['course']
	if(course!=''):
		for tutor in tutor_all:
			course_code_query = tutor.teach_course_code.all()
			for course_code in course_code_query:
				if(course_code.subject_code==course):
					tutor_list.append(tutor)
					break;
	else:
		for tutor in tutor_all:
			tutor_list.append(tutor)

	if(len(tutor_list)==0):
		for tutor in Tutor.objects.filter(activated=True):
			tutor_list.append(tutor)

	return render(request,'mainApp/tutorList.html',{'tutor_list': tutor_list, 'range5': range(5)})
@login_required
def detailedProfile(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	return render(request,'mainApp/detailedProfile.html',{'tutor': tutor, 'date': str(date.today()), 'schedule': str(schedule.available_timeslot)})

#post request for payment confirmation
@login_required
def confirmPayment(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	slot = int(request.GET['slot'])
	if(str(schedule.available_timeslot)[slot]=='a'):
		return render(request,'mainApp/confirmPayment.html',{'tutor': tutor, 'slot': slot, 'today': str(date.today())})
	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor})

#accept request and create session
@login_required
def bookSession(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	time = int(request.GET['time'])
	date = request.GET['date']
	slot = int(request.GET['slot'])
	if(tutor.tutor_type=="Private"):
		time_str = str(time+9) + ":00:00"
	else:
		if(time%2==0):
			time_str = str(int(time/2+9)) + ":00:00"
		else:
			time_str = str(int((time-1)/2+9)) + ":30:00"
	student = Student.objects.get(id=request.user.student.id)
	if(str(schedule.available_timeslot)[slot]=='a'):
		schedule.available_timeslot = schedule.available_timeslot[:slot] + "b" + schedule.available_timeslot[(slot+1):]
		schedule.save()
		session = Session(session_tutor=tutor, session_datetime=date+" "+time_str, session_student=student, coupon_used=False)
		session.save()

	return redirect(viewUpcomingSessions)

#routes for cancel payment
@login_required
def viewUpcomingSessions(request):
	# Get Student Info
	this_student = request.user.student
	# retrieve list of sessions associated with the student
	# currently only retrieves sessions with (state='normal')
	student_sessions = this_student.session_set.filter(state='normal')
	# return list of sessions
	context = {'student_sessions': student_sessions, 'this_student': this_student,}
	return render(request,'mainApp/viewUpcomingSessions.html',context)


#post request
@login_required
def cancelSession(request, session_ID):
# Get Session ID
	this_student = request.user.student
	this_session = Session.objects.get(id=session_ID)
	session_time = this_session.session_datetime
	session_student_ID = this_student.id
	session_tutor_ID = this_session.session_tutor
	context = {'this_session': this_session, 'session_time': session_time, 'session_student_ID': session_student_ID, 'session_tutor_ID': session_tutor_ID,}
	return render(request,'mainApp/cancelSession.html',context)


@login_required
def sessionCancelled(request, session_ID):
	toCancel = request.GET['YesNoCancel']
	if (toCancel=='N'):
		return HttpResponseRedirect('/main/upcomingSessions')
	else:
		this_session = Session.objects.get(id=session_ID)
		this_session.state='cancelled'
		this_session.save()
		return render(request,'mainApp/sessionCancelled.html')



