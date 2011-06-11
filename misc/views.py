# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.dispatch import Signal
from django.template import Context, loader
from django.shortcuts import redirect

from .signals import language_changed


def server_error(request, template_name='500.html'):
    """
        500 error handler.

        Templates: `500.html`
        Context:
            MEDIA_URL
                Path of static media (e.g. "media.example.org")
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL
    })))

def redirect_by_name(request, name, **kwargs):
    keys = kwargs.keys()
    for k in keys:
        if k in kwargs and callable(kwargs[k]):
            kwargs[k] = kwargs[k](kwargs)
    return redirect(name, **kwargs)

def language_change(request, lang):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None) or '/'
    response = redirect(next)
    if lang and lang in map(lambda x: x[0], settings.LANGUAGES):
        if request.user.is_authenticated():
            profile = request.user.get_profile()
            profile.language = lang
            profile.save()
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang,
                max_age=settings.SESSION_COOKIE_AGE)
        language_changed.send(None, request=request, lang=lang)
    return response
