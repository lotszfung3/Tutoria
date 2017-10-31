from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^findTutors$',views.findTutors,name='findTutors'),
    url(r'^tutorsList',views.tutorsList,name='tutorsList'),
    url(r'^detailedProfile',views.detailedProfile,name='detailedProfile'),
    url(r'^confirmPayment$',views.confirmPayment,name='confirmPayment'),
    url(r'^upcomingSessions',views.viewUpcomingSessions,name='viewUpcomingSessions'),
    url(r'^cancelSession/(?P<session_ID>\d+)',views.cancelSession,name='cancelSession'),
    url(r'^(?P<session_ID>\d+)/sessionCancelled',views.sessionCancelled,name='sessionCancelled'),
    url(r'^register$',views.register,name='register'),
	url(r'^login$',views.login_h,name='login'),
	url(r'^logout$',views.logout_h,name='logout')
]
