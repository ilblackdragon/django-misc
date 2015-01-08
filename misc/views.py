# -*- coding: utf-8 -*-
from django import http
from django.conf import settings
from django.dispatch import Signal
from django.template import Context, loader
from django.shortcuts import redirect

# Django 1.7 Removed custom profiles
try:
    from django.contrib.auth.models import SiteProfileNotAvailable
except ImportError:
    SiteProfileNotAvailable = None

if 'coffin' in settings.INSTALLED_APPS:
    is_coffin = True
    from coffin.template.response import TemplateResponse

from .signals import language_changed
from utils import AUTH_USER_LANGUAGE_FIELD


def handler500(request, template_name='500.html'):
    """
        500 error handler.

        Templates: `500.html`
        Context:
            MEDIA_URL
                Path of static media (e.g. "media.example.org")
            STATIC_URL
    """
    t = loader.get_template(template_name) # You need to create a 500.html template.
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL
    })))

def handler404(request, template_name='404.html'):
    """
        404 error handler.

        Templates: `404.html`
        Context:
            MEDIA_URL
                Path of static media (e.g. "media.example.org")
            STATIC_URL
    """
    t = loader.get_template(template_name) # You need to create a 404.html template.
    return http.HttpResponseNotFound(t.render(Context({
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
        language_saved = False
        if request.user.is_authenticated():
            user = request.user
            if hasattr(user, AUTH_USER_LANGUAGE_FIELD):
                setattr(user, AUTH_USER_LANGUAGE_FIELD, lang)
                user.save()
                language_saved = True
            else:
                if SiteProfileNotAvailable is None:
                    profile = user
                else:
                    try:
                        profile = user.get_profile()
                    except SiteProfileNotAvailable:
                        profile = None
                if profile is not None and hasattr(profile, AUTH_USER_LANGUAGE_FIELD):
                    setattr(profile, AUTH_USER_LANGUAGE_FIELD, lang)
                    profile.save()
                    language_saved = True
        if not language_saved:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang,
                max_age=settings.SESSION_COOKIE_AGE)
        language_changed.send(None, request=request, lang=lang)
    return response

def coffin_template_response(request, view, **kwargs):
    response = view(request, **kwargs)
    if is_coffin and hasattr(response, 'template_name'):
        return TemplateResponse(request, response.template_name, response.context_data)
    return response
