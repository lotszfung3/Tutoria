from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import User,Student,Tutor,SubjectCode,Wallet,Transaction,Schedule
from datetime import datetime,date,timedelta,timezone
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner
from .utils import uploadImage,emailGateway,paymentGateway
from django.contrib.auth.password_validation import validate_password
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import never_cache

message_dict={"l_logout":"You have logged out.","l_fail":"Your username or your password doesn't match",
			 "l_register":"You have registered your account sucessfully","l_reset":"You have reset your password",
			 "r_pw":"The passwrod is too weak","l_fp":"Please check your registered email to reset password",
			 "l_fpfail":"The username or email doesn't belongs to any user","lrp_fail":"The two password doesn't match",
             "rp_fail":"Your username is not coorrect",
			 "r_un":"Please use another username"}

@csrf_exempt
def test(request):
	if(request.method=='GET'):
		'''tutor=Tutor.objects.all()[0]
		tutor.teach_course_code.add(SubjectCode.objects.get(subject_code="COMP3258"))
		tutor.teach_course_code.add(SubjectCode.objects.get(subject_code="COMP3278"))
		tutor.save()'''
	else:
		print(request.POST.getlist('subject'))
		return HttpResponse("post")
	
@login_required
def logout_h(request):
	logout(request)
	return HttpResponseRedirect('/main/login?message=l_logout')

def login_h(request):
	if request.method == 'GET':
		if(request.user.is_authenticated()):
			return HttpResponseRedirect('/main/findTutors')
		return render(request, 'mainApp/account/login.html',{'message':message_dict[request.GET['message']]} if 'message' in request.GET and request.GET['message'] in message_dict else None)
	elif request.method == 'POST':
		if('username' not in request.POST or 'password' not in request.POST):
			return HttpResponseRedirect('./login?message=l_fail')
		username=request.POST['username']
		password=request.POST['password']
		user=authenticate(request,username=username,password=password)
		if user is not None:
			login(request,user)
			return HttpResponseRedirect('./findTutors')
		else:
			return HttpResponseRedirect('./login?message=l_fail')

def register(request):
	if request.method == 'GET':
		if(request.user.is_authenticated()):
			return HttpResponseRedirect('/main/findTutors')
		return render(request,'mainApp/account/register.html',{"subject_list":SubjectCode.getCodeList(),'message':message_dict[request.GET['message']] if 'message' in request.GET and request.GET['message'] in message_dict else None})
	elif request.method == 'POST':
		try:#test password strength
			validate_password(request.POST['password'])
		except:
			return HttpResponseRedirect('/main/register?message=r_pw')
		if(User.objects.filter(username=request.POST['username']).exists()):
			return HttpResponseRedirect('/main/register?message=r_un')
		user = User.objects.create_user(request.POST['username'], request.POST['email'], request.POST['password'])
		user.first_name=request.POST['name']
		user.save()
		fs = FileSystemStorage()
		filename=fs.save('profilepic/'+str(user.id)+'.jpg',request.FILES['myImage'])
		user.student.photo_url='profilepic/{}.jpg'.format(str(user.id))
		user.student.phoneNumber=request.POST['phone']
		user.student.save()
		#if he want to be a tutor
		tut=None
		if('role' in request.POST and request.POST['role']=='on'):
			atype=request.POST['type'] if 'type' in request.POST else 'p'
			temprate=request.POST['hourlyRate'] if atype=='p' else 0
			tut=Tutor.create(user=user,phone=request.POST['phone'],introduction=request.POST['description'],hourly_rate=temprate,uni=request.POST['uni'],
							 subject_code=request.POST.getlist('subject'),tag=request.POST['tag'],atype=atype,imagePath='profilepic/{}.jpg'.format(str(user.id)))
			
			tut.save()
		Wallet.create(student=user.student,tutor=tut)
		return HttpResponseRedirect('/main/login?message=l_register')
def forgetPw(request):
	if request.method=='GET':
		return render(request, 'mainApp/account/forgetPw.html')
	elif request.method == "POST":
		if(request.POST['username']!=""):
			username=request.POST['username']
			user=User.objects.filter(username=username)
			if(user.exists()):
				emailGateway("resetPw",user[0].email,request.get_host()+"/main/retrievePw?token="+TimestampSigner().sign(username).split(":",maxsplit=1)[1])
				return HttpResponseRedirect('/main/login?message=l_fp')
		elif(request.POST['email']!=""):
			email=request.POST['email']
			user=User.objects.filter(email=email)
			if(user.exists()):
				emailGateway("resetPw",user[0].email,request.get_host()+"/main/retrievePw?token="+TimestampSigner().sign(user[0].username).split(":",maxsplit=1)[1])
				return HttpResponseRedirect('/main/login?message=l_fp')
		return HttpResponseRedirect('/main/login?message=l_fpfail')
            
            
#form for finding tutors
def retrievePw(request):
	if request.method=='GET':
		return render(request,'mainApp/account/retrievePw.html',{'message':message_dict[request.GET['message']]} if 'message' in request.GET and request.GET['message'] in message_dict else None)
	elif request.method=='POST':
		token=request.GET["token"]
		if(request.POST["password"]==request.POST["password1"]):
			try:
				TimestampSigner().unsign(request.POST["username"]+":"+token,max_age=timedelta(minutes=5))
				u=User.objects.get(username=request.POST["username"])
				u.set_password(request.POST["password1"])
				u.save()
				return HttpResponseRedirect('/main/login?message=l_reset')
			except:
				return HttpResponseRedirect('/main/retrievePw?message=rp_fail&token={}'.format(token))			
		else:
			return HttpResponseRedirect('/main/login?message=lrp_fail')
@csrf_exempt
@login_required
def manageWallet(request):
	if(request.method=='GET'):
		return render(request,'mainApp/wallet.html')
	else:
		amount=100 if request.GET['action']=='add' else -100
		transaction=Transaction.create(None,amount,request.user.student,None)
		mes=paymentGateway(request.user,amount)
		
		return HttpResponse(mes)
@never_cache
@login_required
def viewAccountDetail(request):
	#this_user = request.user.student
	#return render(request, 'mainApp/viewAccountDetail_student.html', {'this_user': this_user})
    if(hasattr(request.user,'tutor')):
        this_user = request.user.tutor
        return render(request, 'mainApp/viewAccountDetail_tutor.html', {'this_user': this_user,"tut_reviews":this_user.review_set.all()})
    else:
        this_user = request.user.student
        return render(request, 'mainApp/viewAccountDetail_student.html', {'this_user': this_user})

@login_required
def viewTransaction(request):
	name=request.user.first_name
	wallet=request.user.student.wallet
	return render(request, 'mainApp/viewTransaction.html', {'name': name,'transactions':wallet.transactions.filter(create_date__lte=datetime.now(timezone.utc)+timedelta(days=30)).order_by("-create_date") if wallet.transactions.count()>0 else None})
	
@login_required
def editUnavailableSession(request):
	tutor = Tutor.objects.get(id=request.user.tutor.id)
	schedule = Schedule.objects.get(owned_tutor=tutor)

	return render(request,'mainApp/editUnavailableSession.html',{'tutor': tutor, 'date': str(date.today()), 'schedule': str(schedule.available_timeslot)})

@login_required
def changeSession(request):
	if(request.method=='GET'):
		tutor = Tutor.objects.get(id=request.user.tutor.id)
		schedule = Schedule.objects.get(owned_tutor=tutor)
		slot = int(request.GET['sessionID'])

		if(str(schedule.available_timeslot)[slot] == 'a'):
			schedule.available_timeslot = schedule.available_timeslot[:slot] + "c" + schedule.available_timeslot[(slot+1):]
			schedule.save()
		elif(str(schedule.available_timeslot)[slot] == 'c'):
			schedule.available_timeslot = schedule.available_timeslot[:slot] + "a" + schedule.available_timeslot[(slot+1):]
			schedule.save()

	return redirect(editUnavailableSession)
