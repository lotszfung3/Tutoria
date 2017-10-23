from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^findTutors$',views.findTutors,name='findTutors'),
    url(r'^tutorsList',views.tutorsList,name='tutorsList'),
    url(r'^detailedProfile',views.detailedProfile,name='detailedProfile'),
    url(r'^confirmPayment$',views.confirmPayment,name='confirmPayment'),
    url(r'^viewUpcomingSessions$',views.viewUpcomingSessions,name='viewUpcomingSessions'),
    url(r'^cancelSession$',views.cancelSession,name='cancelSession')
]
