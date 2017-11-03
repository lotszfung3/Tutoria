from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from datetime import date
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def test(request):
	return render(request, 'mainApp/test.html')
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
		user.student.phoneNumber=request.POST['phone']
		user.student.save()
		#if he want to be a tutor
		if('role' in request.POST):
			type=request.POST['type'] if 'type' in request.POST else 'p'
			tut=Tutor.create(user=user,phone=request.POST['phone'],introduction=request.POST['description'],hourly_rate=request.POST['hourlyRate'],subject_code=request.POST['subject'],tag=request.POST['tag'],type=type)
			tut.save()
		return HttpResponseRedirect('/main/login?fail=t')
def forgetPw(request):
	if request.method=='GET':
		if(request.user.is_authenticated()):
			return HttpResponseRedirect('/main/findTutors')
		return HttpResponse("forgetPw_get")
	elif request.method == "POST":
		return HttpResponse("forgetPw_post")
#form for finding tutors