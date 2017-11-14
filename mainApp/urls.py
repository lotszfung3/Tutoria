from django.conf.urls import url

from . import views
from . import views_account

urlpatterns = [
    url(r'^test$', views_account.test, name='test'),
    url(r'^findTutors$',views.findTutors,name='findTutors'),
    url(r'^tutorsList',views.tutorsList,name='tutorsList'),
    url(r'^detailedProfile',views.detailedProfile,name='detailedProfile'),
    url(r'^confirmPayment$',views.confirmPayment,name='confirmPayment'),
    url(r'^upcomingSessions',views.viewUpcomingSessions,name='viewUpcomingSessions'),
    url(r'^cancelSession/(?P<session_ID>\d+)',views.cancelSession,name='cancelSession'),
    url(r'^(?P<session_ID>\d+)/sessionCancelled',views.sessionCancelled,name='sessionCancelled'),
    url(r'^bookSession$', views.bookSession, name='bookSession'),
	url(r'^register$',views_account.register,name='register'),
	url(r'^login$',views_account.login_h,name='login'),
  	url(r'^logout$',views_account.logout_h,name='logout'),
	url(r'^forgetPw$',views_account.forgetPw,name='forgetPw'),
	url(r'^retrievePw$',views_account.retrievePw,name='retrievePw'),
    url(r'^manageWallet$',views_account.manageWallet,name='manageWallet')
    url(r'^/submitReview/(?P<session_ID>\d+)$',views.submitReview,name='submitReview'),
    url(r'^(?P<session_ID>\d+)/reviewSubmitted',views.reviewSubmitted,name='reviewSubmitted'),
]
