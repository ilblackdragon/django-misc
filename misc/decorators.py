from functools import update_wrapper, wraps

from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import available_attrs

if 'coffin' in settings.INSTALLED_APPS:
    from coffin.template.response import TemplateResponse
else:
    from django.template.response import TemplateResponse

def to_template(template_name=None):
    """
    Decorator for simple call TemplateResponse
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
                return TemplateResponse(request, result.pop('TEMPLATE', template_name), result)
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

def cached(cache_key=None, invalidate_signals=None, timeout=None):
    def decorator(function):
        def invalidate(sender, *args, **kwargs):
            """
            Simple cache invalidate fallback function.
            """
            cache.delete(cache_key)

        def wrapped(*args, **kwargs):
            if cache_key is None:
                if invalidate_signals is not None:
                    raise AttributeError("You cannot use function-level caching (cache_key=None) "
                        "with invalidate signals.")
                # Store cached data into function itself
                if not hasattr(function, '_cached'):
                    function._cached = function(*args, **kwargs)
                return function._cached
            else:
                # Cache to external cache backend
                if callable(cache_key):
                    _cache_key = cache_key(*args, **kwargs)
                else:
                    _cache_key = cache_key
                result = cache.get(_cache_key)
                if result is None:
                    result = function(*args, **kwargs)
                    if _cache_key is not None:
                        cache.set(_cache_key, result, timeout)
            return result

        if invalidate_signals:
            wrapped.invalidate = invalidate
            for signal, sender, _invalidate in invalidate_signals:
                # weak - Django stores signal handlers as weak references by default. Thus, if your
                # receiver is a local function, it may be garbage collected. To prevent this, pass
                # weak=False when you call the signal`s connect() method.
                if _invalidate is None:
                    if callable(cache_key):
                        continue
                    _invalidate = wrapped.invalidate
                signal.connect(_invalidate, sender=sender, weak=False)
        return wrapped
    return decorator
