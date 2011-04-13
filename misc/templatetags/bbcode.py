from django import template

from misc.utils import render_bbcode, strip_bbcode

register = template.Library()

register.filter('bbcode', render_bbcode)
register.filter('strip_bbcode', strip_bbcode)
