from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from datetime import date, datetime
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .utils import uploadImage,getSlotIdfromDateTime, emailGateway,paymentGateway
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import never_cache
from django.contrib import messages
from decimal import *

import pytz


@login_required
def findTutors(request):
	return render(request,'mainApp/findTutors.html',{'std':request.user.student,"subject_list":SubjectCode.getCodeList()})

@login_required
def editAccountDetail(request):
    if request.method == 'POST':
        request.user.username = request.POST['Name']
        request.user.email = request.POST['email']
        request.user.student.phoneNumber= request.POST['phoneNumber']
        request.user.student.save()
        if('newImage' in request.FILES):
            fs = FileSystemStorage()
            fs.delete('profilepic/'+str(request.user.id)+'.jpg')
            filename=fs.save('profilepic/'+str(request.user.id)+'.jpg',request.FILES['newImage'])
            #uploadImage(request.FILES['newImage'],request.user.id)
        request.user.save()
        if(hasattr(request.user,'tutor')):
            tutor = request.user.tutor
            tutor.phoneNumber= request.POST['phoneNumber']
            tutor.university = request.POST['university']
            tutor.subject_tag = request.POST['subject_tag']
            tutor.hourly_rate = request.POST['hourly_rate']
            tutor.introduction = request.POST['introduction']
            tutor.activated= (request.POST['activated']=='y')
            subject_list=request.POST.getlist('subject')
            tutor.teach_course_code.clear()
            if(isinstance(subject_list,list)):
                for i in subject_list:
                    tutor.teach_course_code.add(SubjectCode.objects.get(subject_code=i))
            else:
                tutor.teach_course_code.add(SubjectCode.objects.get(subject_code=subject_list))

            tutor.save()
            
        return HttpResponseRedirect('/main/viewAccountDetail')
    else:
        #this_user = request.user.student
        #return render(request,'mainApp/editAccountDetail_student.html',{'this_user':this_user})
        if(hasattr(request.user,'tutor')):
            this_user = request.user.tutor
            if this_user.activated:
            	activate_yes = 'checked = "yes"'
            	activate_no = ''
            else:
            	activate_yes = ''
            	activate_no = 'checked = "yes"'
            return render(request,'mainApp/editAccountDetail_tutor.html',{'this_user':this_user,"subject_list":SubjectCode.getCodeList(),"teach_course_code":this_user.teach_course_code.values('subject_code'), "activate_yes": activate_yes, "activate_no": activate_no})
        else:
            this_user = request.user.student
            return render(request,'mainApp/editAccountDetail_student.html',{'this_user':this_user})

#list of tutors with requirement in side request.GET
@login_required
@never_cache
def tutorsList(request):
	uni=request.GET["university"]
	tag=request.GET["tag"]
	lprice=request.GET["lprice"]
	hprice=request.GET["hprice"]
	t_type=request.GET["type"]
	tutor_query={}
	if uni!='':
		tutor_query["university"]=uni
	if tag!='':
		tutor_query["subject_tag__contains"]=tag
	if lprice!='':
		tutor_query["hourly_rate__gte"]=int(lprice)
	if hprice!='':
		tutor_query["hourly_rate__lte"]=int(hprice)
	if t_type=='c':
		tutor_query["tutor_type"]='Contract' 
	elif t_type=='p':
		tutor_query["tutor_type"]='Private'

	tutor_query["activated"]=True 
	tutor_all = Tutor.objects.filter(**tutor_query)

	sort = request.GET['sort']
	if(sort=='AscP'):
		tutor_all = tutor_all.order_by('hourly_rate')
	elif(sort=='DscP'):
		tutor_all = tutor_all.order_by('-hourly_rate')
	elif(sort=='AscS'):
		tutor_all = tutor_all.order_by('avg_review')
	elif(sort=='DscS'):
		tutor_all = tutor_all.order_by('-avg_review')

	course = request.GET['course']
	if(course!=''):
		subject_code=SubjectCode.objects.get(subject_code=course)#assume it must be there
		tutor_all=tutor_all.filter(teach_course_code=subject_code)#e.g.: "COMP3297"

	if 'crit' in request.GET:
		tutor_all = [tutor for tutor in tutor_all if availableInSevenDays(tutor)]
		#if the result is empty
	if(not tutor_all.exists()):
		tutor_all=Tutor.objects.filter(activated=True)

#exclude yourself
	tutor_all=tutor_all.exclude(user_id=request.user.id)
	url = './tutorsList?university=' + uni + '&course=' + course + '&tag=' + tag + '&lprice=' + lprice + '&hprice=' + hprice + '&type=' + t_type + '&sort='

	return render(request,'mainApp/tutorList.html',{'tutor_list': tutorListToHtml(tutor_all), 'range5': range(5), 'url': url})

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
	student_wallet = Wallet.objects.get(student=student.id)


	session_date = ''
	if(tutor.tutor_type=="Private"):
		time = slot%10
		time_str = str(time+9) + ":00:00"
		session_date = str(datetime.now(timezone.utc).date()+timedelta(days=(slot-slot%10)/10+1))
	else:
		time = slot%20
		session_date = str(datetime.now(timezone.utc).date()+timedelta(days=(slot-slot%20)/20+1))
		if(time%2==0):
			time_str = str(int(time/2+9)) + ":00:00"
		else:
			time_str = str(int((time-1)/2+9)) + ":30:00"

	if sameTutorBooked(student,tutor,session_date):
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'You have already booked another session of this tutor on this day, please try again.'})

	if sameTimeBooked(student,session_date,time_str,tutor.tutor_type):
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'You have already booked session at the same time, please try again.'})

	if lessThan24Hours(session_date,time_str):
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'You cannot book a session within 24 hours, please choose another slot.'})

	if(student.user==tutor.user):
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'You cannot register your own slot! Please choose another tutor.'})

	if(student_wallet.amount < tutor.hourly_rate*Decimal('1.05')):
		message = '<div class="field">'
		message = message + 'Coupon Code (optional): <input type="text" name="coupon" placeholder="Coupon Code">'
		message = message + '</div>'
		message = message +'Your wallet does not have sufficient amount!<button class="ui button" type="submit">Manage Wallet</button>'
		return render(request,'mainApp/confirmPayment.html',{'tutor': tutor, 'slot': slot, 'today': str(datetime.now(timezone.utc).date()+timedelta(days=1)), 'student': student, 'student_wallet': student_wallet,
			'student_rate': student_rate, 'action': 'manageWallet', 'button': message, 'method': 'get'})

	if(str(schedule.available_timeslot)[slot]=='a'):
		submit = '<div class="field">'
		submit = submit + 'Coupon Code (optional): <input type="text" name="coupon" placeholder="Coupon Code">'
		submit = submit + '</div>'
		submit = submit + '<button class="ui button" type="submit">Submit</button>'
		return render(request,'mainApp/confirmPayment.html',{'tutor': tutor, 'slot': slot, 'today': str(datetime.now(timezone.utc).date()+timedelta(days=1)), 'student': student, 
			'student_rate': student_rate, 'action': 'bookSession', 'button': submit, 'message': '', 'method': 'post', 'student_wallet': student_wallet})
	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'The slot you chose is not available, please choose another slot.'})

#accept request and create session
@login_required
def bookSession(request):
	#getting the information
	tutor = Tutor.objects.get(id=request.POST['tutorsID'])
	schedule = Schedule.objects.get(owned_tutor=tutor)
	time = int(request.POST['time'])
	date = request.POST['date']
	slot = int(request.POST['slot'])
	student = Student.objects.get(id=request.user.student.id)

	if sameTutorBooked(student,tutor,date):
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'You have already booked another session of this tutor on this day, please try again.'})

	coupon = request.POST['coupon']
	if coupon == '':
		couponValid = False
	elif Coupon.objects.filter(coupon_code=coupon).exists():
		temp_coupon = Coupon.objects.get(coupon_code=coupon)
		if not temp_coupon.isExpired():
			couponValid = True
		else:
			return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'The coupon code you entered has expired, please try again.'})
	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'The coupon code you entered is not valid, please try again.'})

	if(tutor.tutor_type=="Private"):
		time_str = str(time+9) + ":00:00"
	else:
		if(time%2==0):
			time_str = str(int(time/2+9)) + ":00:00"
		else:
			time_str = str(int((time-1)/2+9)) + ":30:00"

	if sameTimeBooked(student,date,time_str,tutor.tutor_type):
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'You have already booked session at the same time, please try again.'})

	if(str(schedule.available_timeslot)[slot]=='a') & (student.wallet.amount > tutor.getStudentRate()):
		#saving the wallet amount and create session
		utc=pytz.UTC
		s_datetime = datetime.strptime(date + " " + time_str, '%Y-%m-%d %H:%M:%S')
		s_datetime=utc.localize(s_datetime)-timedelta(hours=8)
		student_wallet = Wallet.objects.get(student=student.id)
		if not couponValid :
			student_wallet.amount = student_wallet.amount - tutor.getStudentRate()
			session = Session(session_tutor=tutor, session_datetime=s_datetime, session_student=student, coupon_used=False)
		else:
			student_wallet.amount = student_wallet.amount - tutor.hourly_rate
			session = Session(session_tutor=tutor, session_datetime=s_datetime, session_student=student, coupon_used=True)
		student_wallet.save()
		session.save()

		#saving the changed schedule
		schedule.available_timeslot = schedule.available_timeslot[:slot] + "b" + schedule.available_timeslot[(slot+1):]
		schedule.save()
		

		#saving the transaction record
		if not couponValid :
			transAMT = tutor.hourly_rate + (.05 * tutor.hourly_rate)
		else:
			transAMT = tutor.hourly_rate
		new_transaction = Transaction.create(session, transAMT, student, tutor)
		new_transaction.save()



		if not couponValid:
			emailGateway('session_book',[student.user.first_name,tutor.user.first_name],{"datetime":session.session_datetime,"amount":tutor.hourly_rate, "commission": tutor.getStudentRate()})
		else:
			emailGateway('session_book_coupon',[student.user.first_name,tutor.user.first_name],{"datetime":session.session_datetime,"amount":tutor.hourly_rate})

	else:
		return render(request,'mainApp/confirmPayment_false.html',{'tutor': tutor, 'message': 'The slot you chose is not available, please choose another slot.'})



#routes for cancel payment
@login_required
def viewUpcomingSessions(request):
	# Get Student Info
	this_student = request.user.student
	# retrieve list of sessions associated with the student
	student_sessions = this_student.session_set.filter(state__in=['locked','normal']) 
	# return list of sessions associated with tutor
	tutor_sessions=request.user.tutor.session_set.filter(state__in=['locked','normal']).order_by('session_datetime') if hasattr(request.user,'tutor') and request.user.tutor.session_set.exists() else None
		
	context = {'student_sessions': student_sessions, 'this_student': this_student,'tutor_sessions':tutor_sessions}
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
		messages.info(request,'This session has been cancelled')
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
		temp_amount=temp_tutor.hourly_rate if this_session.coupon_used else temp_tutor.getStudentRate()
		student_wallet.amount +=  temp_amount
		student_wallet.save()

		#change transaction state
		this_transaction.state='cancelled'
		this_transaction.save()
		
		#email
		emailGateway('session_cancel',[str(this_student),str(temp_tutor)],{"datetime":this_session.session_datetime,"amount":temp_amount})
		
		return render(request,'mainApp/cancel/sessionCancelled.html')

@login_required
def submitReviews(request, session_ID):
	this_session = Session.objects.get(id=session_ID)
	this_student = request.user.student

	if (this_session.session_student.id != this_student.id):
		messages.info(request, 'You do not have the permission to review this session')
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
	rating = request.POST['rating']
	comment = request.POST['comment']
	
	if "is_anonymous" in request.POST and request.POST['is_anonymous']=="Y":
		is_anonymous=True
	else:
		is_anonymous=False
	#create new review
	new_review = Review(stars=int(rating), is_anonymous=is_anonymous,comment = comment, for_tutor=tut, written_student= student,involved_session=this_session, course_code="COMP3297", state="completed")
	new_review.save()

	this_session.review_state='complete'
	this_session.save()
	
	#change tutor avg review
	tut.updateAvgReview()
	return render(request,'mainApp/review/reviewSubmitted.html')


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
		string = string + '<img src="/main/media/'+ tutor.photo_url+'"'+'height="100" width="100">'
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


def sameTutorBooked(student,tutor,date):
	sessionQuery = {}

	sessionQuery['session_student'] = student
	sessionQuery['session_tutor'] = tutor
	sessionQuery['state'] = 'normal'
	date=datetime.strptime(date,'%Y-%m-%d')+timedelta(days=1)
	session = Session.objects.filter(**sessionQuery)

	if session.exists():
		sessionList = list(session)
		sessionList = [session for session in sessionList if session.session_datetime.date() == date.date()]
		if len(sessionList)!=0:
			return True
		else:
			return False
	else:
		return False

def sameTimeBooked(student,date,time,tutor_type):
	utc=pytz.UTC
	s_datetime = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
	s_datetime=utc.localize(s_datetime)-timedelta(hours=8)
	if tutor_type =='Contract':
		sessionQuery = {}

		sessionQuery['session_datetime'] = s_datetime
		sessionQuery['state'] = 'normal'
		sessionQuery['session_student'] = student

		session = Session.objects.filter(**sessionQuery)

		sessionQuery['session_datetime'] = s_datetime - timedelta(minutes=30)
		session2 = Session.objects.filter(**sessionQuery)
		session2List = list(session2)
		session2List = [session for session in session2List if session.session_tutor.tutor_type == 'Private']

		if session.exists() or len(session2List)!=0:
			return True
		else:
			return False
	else:
		sessionQuery = {}

		sessionQuery['session_datetime'] = s_datetime
		sessionQuery['state'] = 'normal'
		sessionQuery['session_student'] = student

		session = Session.objects.filter(**sessionQuery)

		sessionQuery['session_datetime'] = s_datetime + timedelta(minutes=30)
		session2 = Session.objects.filter(**sessionQuery)

		if session.exists() or session2.exists():
			return True
		else:
			return False

def lessThan24Hours(date,time):
	utc=pytz.UTC
	s_datetime = datetime.strptime(date + " " + time, '%Y-%m-%d %H:%M:%S')
	s_datetime=utc.localize(s_datetime)-timedelta(hours=8)
	if datetime.now(timezone.utc)+timedelta(days=1) > s_datetime:
		return True
	else:
		return False