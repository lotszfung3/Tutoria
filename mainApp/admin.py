from django.contrib import admin

from .models import Student,Tutor,Schedule,Session,Coupon,Transaction,Review,SubjectCode

# Register your models here.

admin.site.register(Student)
admin.site.register(Tutor)
admin.site.register(Schedule)
admin.site.register(Session)
admin.site.register(Coupon)
admin.site.register(Transaction)
admin.site.register(Review)
admin.site.register(SubjectCode)
