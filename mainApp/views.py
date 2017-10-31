from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from datetime import date
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

def test(request):
    return render(request, 'mainApp/test.html')
@login_required
def logout_h(request):
	if(request.user and request.user.is_authenticated()):
		logout(request)
	return HttpResponseRedirect('/main/login')

def login_h(request):
	if request.method == 'GET':
		return render(request, 'mainApp/login.html')
	elif request.method == 'POST':
		username=request.POST['username']
		password=request.POST['password']
		user=authenticate(request,username=username,password=password)
		if user is not None:
			login(request,user)
			return HttpResponseRedirect('./findTutors')
		else:
			return HttpResponseRedirect('./login')

def register(request):
	if request.method == 'GET':
		return HttpResponse("register_get")
	elif request.method == 'POST':
		return HttpResponse("register_post")
#form for finding tutors
@login_required
def findTutors(request):
	return render(request,'mainApp/findTutors.html')

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
	return HttpResponse("confirmPayment")

#routes for cancel payment
@login_required
def viewUpcomingSessions(request, student_ID):
	# Get Student ID
	this_student = Student.objects.get(id=student_ID)

	# retrieve list of sessions associated with the student
	# currently only retrieves sessions with (state='normal')
	student_sessions = this_student.session_set.filter(state='normal')
	# return list of sessions
	context = {'student_sessions': student_sessions, 'range5' : range(5)}
	return render(request,'mainApp/viewUpcomingSessions.html',context)


#post request
@login_required
def cancelSession(request, session_ID, student_ID):
# Get Session ID
	this_session = Session.objects.get(id=session_ID)
	session_time = this_session.session_datetime
	session_student_ID = Student.objects.get(id=student_ID)
	session_tutor_ID = this_session.session_tutor
	context = {'this_session': this_session, 'session_time': session_time, 'session_student_ID': session_student_ID, 'session_tutor_ID': session_tutor_ID,}
	return render(request,'mainApp/cancelSession.html',context)
