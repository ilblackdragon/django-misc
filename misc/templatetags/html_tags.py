# -*- coding: utf-8 -*-
from django import template
import re

register = template.Library()
tag_re = re.compile(r'</?[^>]*>')

@register.simple_tag
def remove_tags(text):
    text = text.replace('<br/>', '\n')
    return tag_re.sub('', text)
