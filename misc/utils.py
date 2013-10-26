# -*- coding: utf-8 -*-

import string
import re

from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.utils.encoding import smart_str, force_unicode, iri_to_uri

AUTH_USER_LANGUAGE_FIELD = getattr(settings, 'AUTH_USER_LANGUAGE_FIELD', 'language')


class HttpResponseReload(HttpResponse):
    """
    Reload page and stay on the same page from where request was made.

    example:

    def simple_view(request, form_class=CommentForm, template_name='some_template.html'):
        form = CommentForm(request.POST or None)
        if form.valid():
            form.save()
            return HttpResponseReload(request)
        return render(template_name, {'form': form})
    """
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__(self)
        referer = request.META.get('HTTP_REFERER')
        self['Location'] = iri_to_uri(referer or "/")

def custom_spaceless(value):
    """
    Remove spaces between tags and leading spaces in lines.
    WARNING: It works buggly for <pre> tag.
    """
    return re.sub('(\n|\r|(>))[ \t]+((?(2)<))', '\\1\\3', force_unicode(value))
#        .replace('\n', '').replace('\r', '')

def str_to_class(class_name):
    """
    Returns a class based on class name    
    """
    mod_str, cls_str = class_name.rsplit('.', 1)
    mod = __import__(mod_str, globals(), locals(), [''])
    cls = getattr(mod, cls_str)
    return cls

def get_alphabets():
    alphabet_en = unicode(string.ascii_uppercase)
    alphabet_ru = []
    first = ord(u'а')
    last = ord(u'я')+1
    for ch in range(first, last):
        alphabet_ru.append(unichr(ch).upper()) 
    return (alphabet_en, alphabet_ru)
    
alphabet_en, alphabet_ru = get_alphabets()

def user_from_session_key(session_key):
    session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_wrapper = session_engine.SessionStore(session_key)
    user_id = session_wrapper.get(SESSION_KEY)
    auth_backend = load_backend(session_wrapper.get(BACKEND_SESSION_KEY))

    if user_id and auth_backend:
        return auth_backend.get_user(user_id)
    else:
        return AnonymousUser()

def get_hierarchy_path(str_id, file_ext, root, auto_mkdir=True):
    """
    Attached filenames consists of extra_path, that build from id, and id plus filetype.
    """
    str_id_len = len(str_id)
    if str_id_len >= settings.PREFIX_PATH_LENGTH:
        # generate path name for big amount of files:
        # 1234567890.txt -> 123/456/789/
        extra_path = os.path.join(*[
            str_id[i * settings.PREFIX_PATH_LENGTH : (i + 1) * settings.PREFIX_PATH_LENGTH]
                for i in xrange(str_id_len / settings.PREFIX_PATH_LENGTH)
        ])
        if auto_mkdir:
            try:
                os.makedirs(os.path.join(root, extra_path))
            except OSError:
                pass
    else:
        extra_path = ''
    return os.path.join(root, extra_path, str_id + file_ext)

def get_hierarchy_uploader(root):
    """
    Returns uploader, that uses get_hierarch_path to store files
    """
    def upload_to(instance, filename):
        file_name, file_ext = os.path.splitext(filename)
        return get_hierarchy_path(str(instance.id), file_ext, root)
    return upload_to

