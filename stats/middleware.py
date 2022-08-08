from django.shortcuts import HttpResponseRedirect
from urllib.parse import quote


class AuthRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before the view (and later middleware) are called.
        if not request.user.is_authenticated and request.path != "/login/":
            path = quote(request.get_full_path())
            return HttpResponseRedirect(f"/login/?next={path}")

        # Code to be executed for each request/response after the view is called.
        response = self.get_response(request)
        return response
