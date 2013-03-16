import re

from django.contrib.auth.models import SiteProfileNotAvailable
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.utils.cache import patch_vary_headers

from .utils import custom_spaceless, AUTH_USER_LANGUAGE_FIELD


class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = custom_spaceless(response.content)
        return response


class StripCookieMiddleware(object):
    strip_re = re.compile(r'(__utm.=.+?(?:; |$))')
    def process_request(self, request):
        try:
            cookie = self.strip_re.sub('', request.META['HTTP_COOKIE'])
            request.META['HTTP_COOKIE'] = cookie
        except:
            pass


class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context depending on the user's account. This allows pages
    to be dynamically translated to the language the user desires
    (if the language is available, of course).
    """

    def get_language_for_user(self, request):
        if request.user.is_authenticated():
            user = request.user
            language = getattr(user, AUTH_USER_LANGUAGE_FIELD, None)
            if language is None:
                try:
                    profile = user.get_profile()
                except SiteProfileNotAvailable:
                    pass
                else:
                    language = getattr(profile, AUTH_USER_LANGUAGE_FIELD, None)
            if language is not None:
                return language
        return translation.get_language_from_request(request)

    def process_request(self, request):
        translation.activate(self.get_language_for_user(request))
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
