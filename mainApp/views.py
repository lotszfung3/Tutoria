from django.shortcuts import render
from django.http import HttpResponse

def test(request):
    return render(request, 'mainApp/test.html')


#form for finding tutors
def findTutors(request):
	return HttpResponse("findTutors")

#list of tutors with requirement in side request.GET
def tutorsList(request):
	if ('id' in request.GET):
		return HttpResponse(request.GET['id'])

def detailedProfile(request):
	return HttpResponse("detailedProfile")

#post request for payment confirmation
def confirmPayment(request):
	return HttpResponse("confirmPayment")

#routes for cancel payment
def  viewUpcomingSessions(request):
	return HttpResponse("viewUpcomingSessions")

#post request
def cancelSession(request):
	return HttpResponse("cancelSession")