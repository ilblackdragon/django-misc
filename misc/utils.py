# -*- coding: utf-8 -*-

import string
import re
from postmarkup import render_bbcode as _render_bbcode, strip_bbcode as _strip_bbcode

from django.conf import settings
from django.utils.encoding import smart_str, force_unicode, iri_to_uri
from django.utils.safestring import mark_safe
from django.http import HttpResponse

class HttpResponseReload(HttpResponse):
    """
    Reload page and stay on the same page from where request was made.

    example:

    def simple_view(request):
        if request.POST:
            form = CommentForm(request.POST):
            if form.is_valid():
                form.save()
                return HttpResponseReload(request)
        else:
            form = CommentForm()
        return render_to_response('some_template.html', {'form': form})
    """
    status_code = 302

    def __init__(self, request):
        HttpResponse.__init__(self)
        referer = request.META.get('HTTP_REFERER')
        self['Location'] = iri_to_uri(referer or "/")

def custom_spaceless(value):
    return re.sub('(\n|\r|(>))[ \t]+((?(2)<))', '\\1\\3', force_unicode(value))
#        .replace('\n', '').replace('\r', '')

def render_bbcode(value):
    """
    Generates (X)HTML from string with BBCode "markup".
    By using the postmark lib from:
    @see: http://code.google.com/p/postmarkup/

    """
    value = mark_safe(_render_bbcode(value)\
        .replace('&amp;#91;', '[').replace('&amp;#93;', ']'))
    return value

def strip_bbcode(value):
    """
    Strips BBCode tags from a string
    By using the postmark lib from:
    @see: http://code.google.com/p/postmarkup/

    """
    return mark_safe(_strip_bbcode(value))

def str_to_class(string):
    mod_str, cls_str = string.rsplit('.', 1)
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
