# -*- coding: utf-8 -*-
from django.template import Library, Token, TOKEN_BLOCK, Node, Variable
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter
@stringfilter
def cutafter(value, index):
    if len(value) > int(index)+3:
        return value[:int(index)] + "..."
    else:
        return value
    
@register.filter
def get_range(value):
    return range(value)

@register.simple_tag
def get_element(list, index, index2=None):
    if not index2:
        return list[index]
    return list[index][index2]
    
@register.simple_tag
def find_element(list, index, index2=1):
    """
        When you have list like: a = [(0, 10), (1, 20), (2, 30)] and you need to get value from tuple with first value == index
        Usage:
        {% find_element 1 %} will return 20
    """
    for x in list:
        if x[0] == index:
            return x[index2]
    return None
    
@register.tag
def get_dict(parser, token):
    """
        Call {% get_dict dict key default_key %} or {% get_dict dict key %}
        Return value from dict of key element. If there are no key in get_dict it returns default_key (or '')
        Return value will be in parameter 'value'
    """
    bits = token.contents.split(' ')
    return GetDict(bits[1], bits[2], ((len(bits) > 3) and bits[3]) or '', ((len(bits) > 4) and bits[4]) or '', ((len(bits) > 5) and bits[5]) or '')

class GetDict(Node):
    def __init__(self, dict, key, *args):
        self.dict = dict
        self.key = key
        self.default = ''
        self.context_key = 'value'
        if args[1] == '':
            self.default = args[0]
        elif (args[0] == 'as'):
            self.context_key = args[1]
        elif (args[1] == 'as') and (args[2] != ''):
            self.default = args[0]
            self.context_key = args[2]
        else:
            # raise BadFormat
            pass

    def render(self, context):
        dict = Variable(self.dict).resolve(context)
        key = context.get(self.key, self.key)
        default = context.get(self.default, self.default)
        if dict:
            context[self.context_key] = dict.get(key, default)
        else:
            context[self.context_key] = default
        return ''

@register.tag
def set(parser, token):
    """
        Usage:
        {% set templ_tag var1 var2 ... key %}
        {% set variable key %}
        This tag save result of {% templ_tag var1 var2 ... %} to variable with name key,
        Or will save value of variable to new variable with name key.
    """
    bits = token.contents.split(' ')[1:]
    new_token = Token(TOKEN_BLOCK, ' '.join(bits[:-1]))
    if bits[0] in parser.tags:
        func = parser.tags[bits[0]](parser, new_token)
    else:
        func = Variable(bits[0])
    return SetNode(func, bits[-1])

class SetNode(Node):

    def __init__(self, func, key):
        self.func = func
        self.key = key

    def render(self, context):
        if isinstance(self.func, Node):
            context[self.key] = self.func.render(context)
        else:
            context[self.key] = self.func.resolve(context)
        return ''

@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)

@register.tag
def filter(parser, token):
    """
        Filter tag for Query sets. Use with set tag =)
        {% set filter posts status 0 drafts %}
    """
    bits = token.contents.split(' ')
    return FilterTag(bits[1], bits[2:])
    
class FilterTag(Node):
    def __init__(self, query_list_name, args):
        self.query_list_name = query_list_name
        self.kwargs = {}
        for i, x in enumerate(args):
            if i % 2 == 0:
                self.kwargs[str(x)] = str(args[i + 1])

    def render(self, context):
        kwargs = {}
        for key in self.kwargs:
            kwargs[key] = Variable(self.kwargs[key]).resolve(context)
        query_list = Variable(self.query_list_name).resolve(context)
        return query_list.filter(**kwargs)

@register.simple_tag
def get_settings(key, default=None):
    return getattr(settings, key, default)
