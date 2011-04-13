from functools import update_wrapper, wraps

from django.utils.decorators import available_attrs
from django.views.generic.simple import direct_to_template

def to_template(template_name=None):
    """
    Decorator for simple call direct_to_template
    Examples:
    @to_template("test.html")
    def test(request):
        return {'test': 100}

    @to_template
    def test2(request):
        return {'test': 100, 'TEMPLATE': 'test.html'}

    @to_template
    def test2(request, template_name='test.html'):
        return {'test': 100, 'TEMPLATE': template_name}
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            result = view_func(request, *args, **kwargs)
            if isinstance(result, dict):
                return direct_to_template(request, result.pop('TEMPLATE', template_name), result)
            return result 
        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

render_to = to_template
    
def receiver(signal, **kwargs):
    """
    Introduced in Django 1.3 (django.dispatch.receiver)
    
    A decorator for connecting receivers to signals. Used by passing in the
    signal and keyword arguments to connect::

    @receiver(post_save, sender=MyModel)
    def signal_receiver(sender, **kwargs):
        do_stuff()
    """
    def _decorator(func):
        signal.connect(func, **kwargs)
        return func
    return _decorator
