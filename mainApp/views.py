from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from datetime import date
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .utils import uploadImage,getSlotIdfromDateTime, emailGateway,paymentGateway
from django.db.models import Q

from django.contrib import messages
@login_required
def findTutors(request):
	return render(request,'mainApp/findTutors.html',{'std':request.user.student})

@login_required
def editAccountDetail(request):
    if request.method == 'POST':
        request.user.username = request.POST['Name']
        request.user.email = request.POST['email']
        request.user.student.phoneNumber= request.POST['phoneNumber']
        request.user.student.save()
        imagePath=uploadImage(request.FILES['newImage'],request.user.id)
        request.user.save()
        if(hasattr(request.user,'tutor')):
            this_user = request.user.tutor
            this_user.user.username = request.POST['Name']
            this_user.user.email = request.POST['email']
            this_user.phoneNumber= request.POST['phoneNumber']
            this_user.university = request.POST['university']
            this_user.subject_code = request.POST['subject_code']
            this_user.subject_tag = request.POST['subject_tag']
            this_user.hourly_rate = request.POST['hourly_rate']
            this_user.introduction = request.POST['introduction']
            this_user.save()
        return HttpResponseRedirect('/main/viewAccountDetail')
    else:
        #this_user = request.user.student
        #return render(request,'mainApp/editAccountDetail_student.html',{'this_user':this_user})
        if(hasattr(request.user,'tutor')):
            this_user = request.user.tutor
            return render(request,'mainApp/editAccountDetail_tutor.html',{'this_user':this_user})
        else:
            this_user = request.user.student
            return render(request,'mainApp/editAccountDetail_student.html',{'this_user':this_user})

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
			if(tutor.user.id!=request.user.id):
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
	student_rate = tutor.getStudentRate()
	schedule = Schedule.objects.get(owned_tutor=tutor)
	slot = int(request.GET['slot'])
	student = Student.objects.get(id=request.user.student.id) 
	student_wallet = Wallet.objects.get(student=student.id)


	if(str(schedule.available_timeslot)[slot]=='a'):
		student.wallet.amount = student.wallet.amount - tutor.getStudentRate()
		student.wallet.save()
		return render(request,'mainApp/confirmPayment.html',{'tutor': tutor, 'slot': slot, 'today': str(date.today()), 'student': student, 
			'student_rate': student_rate,'student_wallet': student.wallet})
	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor})

#accept request and create session
@login_required
def bookSession(request):
	tutor = Tutor.objects.get(id=request.GET['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	student = Student.objects.get(id=request.user.student.id)
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


	if(str(schedule.available_timeslot)[slot]=='a'):
		schedule.available_timeslot = schedule.available_timeslot[:slot] + "b" + schedule.available_timeslot[(slot+1):]
		schedule.save()
		session = Session(session_tutor=tutor, session_datetime=date+" "+time_str, session_student=student, coupon_used=False)
		session.save()

		transAMT = tutor.hourly_rate + (.05 * tutor.hourly_rate)
		new_transaction = Transaction.create(session, transAMT, student, tutor)
		new_transaction.save()

		
	return redirect(viewUpcomingSessions)

#routes for cancel payment
@login_required
def viewUpcomingSessions(request):
	# Get Student Info
	this_student = request.user.student
	# retrieve list of sessions associated with the student
	# currently only retrieves sessions with (state='normal')
	student_sessions = this_student.session_set.filter(state='locked') | this_student.session_set.filter(state='normal')
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

	now = datetime.now(timezone.utc)
	if (this_session.state=='ended'):#ended
		messages.info(request, 'This session has ended')
		return HttpResponseRedirect('/main/upcomingSessions')
		
	elif ((session_time  < (now + timedelta(hours=24))) & (this_session.state=='normal')):
		messages.info(request, 'You cannot cancel sessions that are starting so soon!')
		this_session.state='locked'
		this_session.save()
		emailGateway('session_lock', [this_student, session_tutor_ID], this_session)
		return HttpResponseRedirect('/main/upcomingSessions')
	
	elif(this_session.state=='cancelled'):#cancelled
		messages.info(request,'This session have been cancelled')
		return HttpResponseRedirect('/main/upcomingSessions')
	
	elif(this_session.state=='locked'):
		messages.info(request,'You cannot cancel sessions that are starting so soon!')
		return HttpResponseRedirect('/main/upcomingSessions')
	
	else:
		context = {'this_session': this_session, 'session_time': session_time, 'session_student_ID': session_student_ID, 'session_tutor_ID': session_tutor_ID}
		return render(request,'mainApp/cancel/cancelSession.html',context)


@login_required
def sessionCancelled(request, session_ID):
	toCancel = request.GET['YesNoCancel']
	this_session = Session.objects.get(id=session_ID)
	this_transaction = Transaction.objects.get(involved_session=session_ID)
	this_student = request.user.student

	if (toCancel=='N'):
		return HttpResponseRedirect('/main/upcomingSessions')
	elif (this_session.state=='locked'):
		messages.info(request, 'You cannot cancel sessions that are starting so soon!')
		return HttpResponseRedirect('/main/upcomingSessions')
	else:
		this_session.state='cancelled'
		this_session.save()
        #change tutor schedule
		temp_tutor=this_session.session_tutor
		temp_slot=getSlotIdfromDateTime(this_session.session_datetime,temp_tutor.tutor_type)
		temp_sch=temp_tutor.schedule
		temp_sch.available_timeslot=temp_sch.available_timeslot[:temp_slot]+"a"+temp_sch.available_timeslot[temp_slot+1:]
		temp_sch.save()
		#add value back to student
		student_wallet = this_student.wallet
		student_wallet.amount += temp_tutor.getStudentRate()
		student_wallet.save()

		#change transaction state
		this_transaction.state='cancelled'
		this_transaction.save()

		this_session.session_student.save()

		return render(request,'mainApp/cancel/sessionCancelled.html')

@login_required
def submitReviews(request, session_ID):
	this_session = Session.objects.get(id=session_ID)
	this_student = request.user.student

	if (this_session.session_student.id != this_student.id):
		messages.info(request, 'You do not have permission to review this session')
		return HttpResponseRedirect('/main/upcomingSessions')

	elif this_session.state != 'ended':
		messages.info(request, 'This session has not ended yet')
		return HttpResponseRedirect('/main/upcomingSessions')
	
	elif this_session.review_state=='empty':
		context = {'this_session': this_session,}
		return render(request,'mainApp/review/submitReviews.html',context)

	else :
		messages.info(request, 'You have already submitted a review for this Session!')
		return HttpResponseRedirect('/main/upcomingSessions')


	# return list of ended sessions

@login_required
def reviewSubmitted(request):
	session_ID = request.POST["sessionID"]
	this_session = Session.objects.get(id=session_ID)

	student_ID = request.POST['studentID']
	student = Student.objects.get(id=student_ID)

	tut = this_session.session_tutor

	#get review info
	anonymous_answer = request.POST['is_anonymous']
	rating = request.POST['rating']
	comment = request.POST['comment']
	
	if anonymous_answer=="Y":
		is_anonymous=True
	else:
		is_anonymous=False
	#create new review
	new_review = Review(stars=int(rating), is_anonymous=is_anonymous,comment = comment, for_tutor=tut, written_student= student,involved_session=this_session, course_code="COMP3297", state="completed")
	new_review.save()

	this_session.review_state='complete'
	this_session.save()

	return render(request,'mainApp/review/reviewSubmitted.html')













