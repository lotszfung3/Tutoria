from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from datetime import date

def test(request):
    return render(request, 'mainApp/test.html')

def login(request):
	if request.method == 'GET':
		return render(request, 'mainApp/login.html')
	elif request.method == 'POST':
		return HttpResponse("login_post")
def register(request):
	if request.method == 'GET':
		return HttpResponse("register_get")
	elif request.method == 'POST':
		return HttpResponse("register_post")
#form for finding tutors
def findTutors(request):
	return render(request,'mainApp/findTutors.html')

#list of tutors with requirement in side request.GET
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

def detailedProfile(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	return render(request,'mainApp/detailedProfile.html',{'tutor': tutor, 'date': str(date.today()), 'schedule': str(schedule.available_timeslot)})

#post request for payment confirmation
def confirmPayment(request):
	return HttpResponse("confirmPayment")

#routes for cancel payment
def viewUpcomingSessions(request, student_ID):
# Get Student ID
	this_student = Student.objects.get(id=student_ID)

# retrieve list of sessions associated with the student
# currently only retrieves sessions with (state='normal')
	student_sessions = this_student.session_set.filter(state='normal')

# return list of sessions
	return render(request, 'mainApp/viewUpcomingSessions.html',{'student_sessions': student_sessions, 'range5': range(5)})

##  if we were to further implement search options for user sessions
#	user_sessions = []
##   not sure how to make this unique to a student profile using  'payment_student' ForeignKey
#	datetime = request.GET['session_datetime']
#	if(datetime!=''):
#		user_sessions.append(Session.objects.filter(session_datetime=datetime))
#
#	curr_state = request.GET['state']
#	if(state!=''):
#		user_sessions.append(Session.objects.filter(state=curr_state))
#
#	coupon = request.GET['coupon_used']
#	if(coupon_used!=''):
#		user_sessions.append(Session.objects.filter(coupon=coupon_used))
#
#	tutor_key = request.GET['session_tutor']
#	if(tutor_key!=''):
#		user_sessions.append(Session.objects.filter(tutor_key=session_tutor))
#
#	session_cost = request.GET['amount']
#	if(session_cost!=0):
#		user_sessions.append(Transaction.objects.filter(session_cost=amount))


#post request
def cancelSession(request):
	return HttpResponse("cancelSession")