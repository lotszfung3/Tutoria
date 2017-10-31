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