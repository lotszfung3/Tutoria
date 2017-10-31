from django.shortcuts import HttpResponseRedirect


class AuthRequiredMiddleware(object):
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

		response = self.get_response(request)
		print(request.user.is_authenticated())
		if(request.path.find('admin')>-1):
			return response
		if(request.path.find('login')>-1 and request.user and request.user.is_authenticated()):
			return HttpResponseRedirect('/main/findTutors')
		if(request.path.find('login')>-1):
			return response
		if(request.user and request.user.is_authenticated()):
			return response

		return HttpResponseRedirect('/main/login')


        # Code to be executed for each request/response after
        # the view is called.
