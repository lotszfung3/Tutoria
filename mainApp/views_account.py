from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from datetime import date,timedelta
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import TimestampSigner
from .utils import uploadImage,emailGateway

@csrf_exempt
def test(request):
	if(request.method=='GET'):
		return render(request, 'mainApp/test.html')
	else:
		return HttpResponse("post")
	
@login_required
def logout_h(request):
	logout(request)
	return HttpResponseRedirect('/main/login')

def login_h(request):
	if request.method == 'GET':
		if(request.user.is_authenticated()):
			return HttpResponseRedirect('/main/findTutors')
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
		if(request.user.is_authenticated()):
			return HttpResponseRedirect('/main/findTutors')
		return render(request,'mainApp/register.html')
	elif request.method == 'POST':

		user = User.objects.create_user(request.POST['name'], request.POST['email'], request.POST['password'])
		user.save()
		if('myImage' in request.FILES):
			uploadImage(request.FILES['myImage'],user.id)
		user.student.phoneNumber=request.POST['phone']
		user.student.save()
		#if he want to be a tutor
		if('role' in request.POST):
			if('myImage' in request.FILES):
				uploadImage(request.FILES['myImage'],user.id)
			type=request.POST['type'] if 'type' in request.POST else 'p'
			tut=Tutor.create(user=user,phone=request.POST['phone'],introduction=request.POST['description'],hourly_rate=request.POST['hourlyRate'],subject_code=request.POST['subject'],tag=request.POST['tag'],type=type)
			tut.save()
		return HttpResponseRedirect('/main/login?fail=t')
def forgetPw(request):
	if request.method=='GET':
		return render(request, 'mainApp/forgetPw.html')
	elif request.method == "POST":
		username=request.POST['username']
		user=User.objects.filter(username=username)
		if(user.exists()):
			emailGateway("resetPw",user[0].email,request.get_host()+"/main/retrievePw?token="+TimestampSigner().sign(username).split(":")[1])
			return HttpResponseRedirect('/main/login')
		else:
			return HttpResponseRedirect('/main/forgetPw')
            
            
#form for finding tutors
def retrievePw(request):
	if request.method=='GET':
		return render(request,'mainApp/retrievePw.html')
	elif request.method=='POST':
		token=request.GET["token"]
		if(request.POST["password"]==request.POST["password1"]):
			try:
				TimestampSigner().unsign(request.POST["username"]+":"+token,max_age=timedelta(minutes=5))
				u=User.objects.get(username=request.POST["username"])
				u.set_password(request.POST["password1"])
				u.save()
			except:
				return HttpResponseRedirect('/main/login')			
		else:
			return HttpResponseRedirect('/main/login')
	