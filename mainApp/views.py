from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from datetime import date
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .utils import getSlotIdfromDateTime
from django.db.models import Q
from django.contrib import messages
from decimal import *
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

	t_type = request.GET['type']
	if(t_type=='c'):
		tutor_query.append(Tutor.objects.filter(tutor_type='Contract'))
	elif(t_type=='p'):
		tutor_query.append(Tutor.objects.filter(tutor_type='Private'))

	tutor_query.append(Tutor.objects.filter(activated=True))

	tutor_all = Tutor.objects.all()

	for i in range(len(tutor_query)):
		tutor_all = tutor_all.intersection(tutor_query[i])	

	sort = request.GET['sort']
	if(sort=='AscP'):
		tutor_all = tutor_all.order_by('hourly_rate')
	elif(sort=='DscP'):
		tutor_all = tutor_all.order_by('-hourly_rate')
	elif(sort=='AscS'):
		tutor_all = tutor_all.order_by('avg_review')
	elif(sort=='DscS'):
		tutor_all = tutor_all.order_by('-avg_review')

	tutor_list = []
	course = request.GET['course']
	if(course!=''):
		for tutor in tutor_all:
			course_code_query = tutor.teach_course_code.all()
			for course_code in course_code_query:
				if(course_code.subject_code==course and crit):
					tutor_list.append(tutor)
					break;
	else:
		tutor_list = list(tutor_all)

	if 'crit' in request.GET:
		tutor_list = list(tutor for tutor in tutor_list if availableInSevenDays(tutor))

	if(len(tutor_list)==0):
		for tutor in Tutor.objects.filter(activated=True):
			tutor_list.append(tutor)

	url = './tutorsList?university=' + uni + '&course=' + course + '&tag=' + tag + '&lprice=' + lprice + '&hprice=' + hprice + '&type=' + t_type + '&sort='

	return render(request,'mainApp/tutorList.html',{'tutor_list': tutorListToHtml(tutor_list), 'range5': range(5), 'url': url})


@login_required
def detailedProfile(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	reviews = Review.objects.filter(for_tutor=tutor)
	reviews_html = '';
	if(reviews.count()!=0):
		for review in reviews:
			reviews_html = reviews_html + '<tr>'
			reviews_html = reviews_html + '<td class="twelve wide">'
			reviews_html = reviews_html + '<p>' + review.comment + '</p>'
			reviews_html = reviews_html + '</td>'
			reviews_html = reviews_html + '<td class="four wide">'
			reviews_html = reviews_html + '<div align="right">'
			for i in range(5):
				if(i<review.stars):
					reviews_html = reviews_html + '★'
				else:
					reviews_html = reviews_html + '☆'
			reviews_html = reviews_html + '</div>'
			reviews_html = reviews_html + '</td>'
			reviews_html = reviews_html + '</tr>'
	else:
		reviews_html = '<tr><td>No reviews available yet.</td></tr>'

	return render(request,'mainApp/detailedProfile.html',{'tutor': tutor, 'tutor_info': tutorInformationToHtml(tutor), 'date': str(date.today()), 'schedule': str(schedule.available_timeslot), 'reviews_html': reviews_html, 'range5': range(5)})

#post request for payment confirmation
@login_required
def confirmPayment(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	student_rate = tutor.getStudentRate()
	schedule = Schedule.objects.get(owned_tutor=tutor)
	slot = int(request.GET['slot'])
	student = Student.objects.get(id=request.user.student.id)

	if(student.amount < tutor.hourly_rate*Decimal('1.05')):
		message = '<div class="field">'
		message = message + 'Coupon Code (optional): <input type="text" name="coupon" placeholder="Coupon Code">'
		message = message + '</div>'
		message = message +'Your wallet does not have sufficient amount!<button class="ui button" type="submit">Manage Wallet</button>'
		return render(request,'mainApp/confirmPayment.html',{'tutor': tutor, 'slot': slot, 'today': str(date.today()), 'student': student, 
			'student_rate': student_rate, 'action': 'manageWallet', 'button': message, 'method': 'get'})

	if(str(schedule.available_timeslot)[slot]=='a'):
		submit = '<div class="field">'
		submit = submit + 'Coupon Code (optional): <input type="text" name="coupon" placeholder="Coupon Code">'
		submit = submit + '</div>'
		submit = submit + '<button class="ui button" type="submit">Submit</button>'
		return render(request,'mainApp/confirmPayment.html',{'tutor': tutor, 'slot': slot, 'today': str(date.today()), 'student': student, 
			'student_rate': student_rate, 'action': 'bookSession', 'button': submit, 'message': '', 'method': 'post'})
	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor})

#accept request and create session
@login_required
def bookSession(request):
	#getting the information
	tutor = Tutor.objects.get(id=request.POST['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	time = int(request.POST['time'])
	date = request.POST['date']
	slot = int(request.POST['slot'])
	if(tutor.tutor_type=="Private"):
		time_str = str(time+9) + ":00:00"
	else:
		if(time%2==0):
			time_str = str(int(time/2+9)) + ":00:00"
		else:
			time_str = str(int((time-1)/2+9)) + ":30:00"

	if(str(schedule.available_timeslot)[slot]=='a'):
		#saving the wallet amount
		student = Student.objects.get(id=request.user.student.id)
		student.amount = student.amount - tutor.getStudentRate()
		student.save()

		#saving the changed schedule and create session
		schedule.available_timeslot = schedule.available_timeslot[:slot] + "b" + schedule.available_timeslot[(slot+1):]
		schedule.save()
		session = Session(session_tutor=tutor, session_datetime=date+" "+time_str, session_student=student, coupon_used=False)
		session.save()

		#saving the transaction record
		transaction = Transaction(amount=tutor.amount*Decimal('1.05'), state="completed", involved_session=session, payment_student=student, payment_tutor=tutor)
		transaction.save()

	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor})

	return redirect(viewUpcomingSessions)

#routes for cancel payment
@login_required
def viewUpcomingSessions(request):
	# Get Student Info
	this_student = request.user.student
	# retrieve list of sessions associated with the student
	# currently only retrieves sessions with (state='normal')
	student_sessions = this_student.session_set.filter(state='soon') | this_student.session_set.filter(state='normal')
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
	context = {'this_session': this_session, 'session_time': session_time, 'session_student_ID': session_student_ID, 'session_tutor_ID': session_tutor_ID}
	return render(request,'mainApp/cancelSession.html',context)


@login_required
def sessionCancelled(request, session_ID):
	toCancel = request.GET['YesNoCancel']
	this_session = Session.objects.get(id=session_ID)
	if (toCancel=='N'):
		return HttpResponseRedirect('/main/upcomingSessions')
	elif (this_session.state=='soon'):
		messages.info(request, 'You cannot cancel sessions that are starting so soon!')
		return HttpResponseRedirect('/main/upcomingSessions')
	else:
		this_session.state='cancelled'
		this_session.save()
        #change tutor schedule
		temp_tutor=this_session.session_tutor
		temp_slot=getSlotIdfromDateTime(this_session.session_datetime,temp_tutor.tutor_type)
		temp_sch=temp_tutor.schedule
		print("slot"+ str(temp_slot))
		temp_sch.available_timeslot=temp_sch.available_timeslot[:temp_slot]+"a"+temp_sch.available_timeslot[temp_slot+1:]
		temp_sch.save()
		#add value back to student
		this_session.session_student.amount+=temp_tutor.getStudentRate()
		this_session.session_student.save()
		return render(request,'mainApp/sessionCancelled.html')





#check to see if a tutor is available in the future seven days
def availableInSevenDays(tutor):
    schedule = Schedule.objects.get(owned_tutor=tutor)
    sch = ''
    if tutor.tutor_type == 'Contract':
        sch = schedule.available_timeslot[:140]
    elif tutor.tutor_type == 'Private':
        sch = schedule.available_timeslot[:70]
    else:
        return False

    for i in range(len(sch)):
        if sch[i] == 'a':
            return True

    return False

#turn tutor list into html
def tutorListToHtml(tutor_list):
	string = ''
	for tutor in tutor_list:
		string = string + '<tr><td><a href="./detailedProfile?tutorsID=' + str(tutor.id) + '"><table class="ui selectable table"><tr><td><p>'
		string = string + 'Tutor Name: ' + tutor.user.first_name + '<br>'
		string = string + 'University: ' + tutor.university + '<br>'
		string = string + 'Rating: '
		if tutor.avg_review == -1:
			string = string + 'Not Available<br>'
		else:
			for i in range(5):
				if i<tutor.avg_review :
					string = string + '★'
				else:
					string = string + '☆'
			string = string + '<br>'
		if tutor.tutor_type == 'Contract':
			string = string + 'Tutor Type: Contract<br>'
		else:
			string = string + 'Tutor Type: Private<br>'
			string = string + 'Hourly Rate: ' + str(tutor.hourly_rate) + '<br>'
		string = string + 'Subject Tags: ' + tutor.subject_tag
		string = string + '</td><td class="right aligned">'
		string = string + '<img src="/static/' + tutor.photo_url + '"/ alt="' + tutor.photo_url + '" height="100" width="100">'
		string = string + '</td></tr></table></a></td></tr>'

	return string

#turn tutor information into html
def tutorInformationToHtml(tutor):

	string = ''

	string = string + 'Tutor Name: ' + tutor.user.first_name + '<br>'
	string = string + 'University: ' + tutor.university + '<br>'
	string = string + 'Rating: '
	if tutor.avg_review == -1:
		string = string + 'Not Available<br>'
	else:
		for i in range(5):
			if i<tutor.avg_review :
				string = string + '★'
			else:
				string = string + '☆'
		string = string + '<br>'
	if tutor.tutor_type == 'Contract':
		string = string + 'Tutor Type: Contract<br>'
	else:
		string = string + 'Tutor Type: Private<br>'
		string = string + 'Hourly Rate: ' + str(tutor.hourly_rate) + '<br>'
	string = string + 'Subject Tags: ' + tutor.subject_tag

	return string