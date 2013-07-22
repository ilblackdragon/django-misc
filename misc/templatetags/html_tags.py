# -*- coding: utf-8 -*-
import re

if 'coffin' in settings.INSTALLED_APPS:
    from coffin.template import Library
else:
    from django.template import Library

register = Library()

if 'coffin' in settings.INSTALLED_APPS:
    register.simple_tag = register.object

tag_re = re.compile(r'</?[^>]*>')

@register.simple_tag
def remove_tags(text):
    text = text.replace('<br/>', '\n')
    return tag_re.sub('', text)
