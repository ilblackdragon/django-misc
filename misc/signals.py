from django.dispatch import Signal

language_changed = Signal(providing_args=['request', 'lang'])
