import os
from datetime import datetime

import traceback

from lockfile import FileLock

from django.core.management import base
from django.conf import settings

try:
    import mailer
except ImportError:
    from django.core import mail as mailer

class BaseCommandMeta(type):

    def __init__(cls, name, bases, dct):
        """
        Swap handle and _handle methods in the inherited classes from BaseCommand and 
        add COMMAND_NAME field (if it's not present) with name of file that inherited class is
        """
        super(BaseCommandMeta, cls).__init__(name, bases, dct)
        base_command_class = None
        for base in bases:
            if base.__module__ == __name__ and base.__name__ == "BaseCommand":
                base_command_class = base
        if base_command_class is not None and 'handle' in dct:
            cls.handle, cls._handle = base_command_class._handle, cls.handle
            if 'COMMAND_NAME' not in dct and '__module__' in dct:
                cls.COMMAND_NAME = cls.__module__.split('.')[-1]

LOCK_ROOT = getattr(settings, 'LOCK_ROOT', None)
LOG_ROOT = getattr(settings, 'LOG_ROOT', None)
COMMAND_LOCK_ROOT = getattr(settings, 'COMMAND_LOCK_ROOT', None) or LOCK_ROOT
COMMAND_USE_LOCK = getattr(settings, 'COMMAND_USE_LOCK', True)
COMMAND_HANDLE_EXCEPTIONS = getattr(settings, 'COMMAND_HANDLE_EXCEPTIONS', True)
COMMAND_LOG_ROOT = getattr(settings, 'COMMAND_LOG_ROOT', None) or LOG_ROOT
COMMAND_EMAIL_EXCEPTIONS = getattr(settings, 'COMMAND_EMAIL_EXCEPTIONS', True)

class BaseCommand(base.BaseCommand):
    """
    This is base class, use it as class to inherit from your commands.

    Note, that meta class magic is used for usability - to use this class you don't need to change 
    anything in your code except import BaseCommand class from different place.
    """
    
    __meta__ = BaseCommandMeta

    USE_LOCK = True
    HANDLE_EXCEPTIONS = True
    EMAIL_EXCEPTIONS = True
    OUTPUT_LOG = True

    def handle(self, *args, **kwargs):
        pass

    def _handle(self, *args, **kwargs):
        stdout_backup = None
        if COMMAND_LOG_ROOT and self.OUTPUT_LOG:
            pass # redirect output to file, not implemented yet
        lock = None
        if COMMAND_LOCK_ROOT and (COMMAND_USE_LOCK or self.USE_LOCK):
            lock = FileLock(os.path.join(COMMAND_LOCK_ROOT, self.COMMAND_NAME))
            try:
                lock.acquire(0)
            except:
                print("Command `%s` already running" % self.COMMAND_NAME)
                return

        print("\n======\nRunning `%s` command at %s\n======\n" % (self.COMMAND_NAME, str(datetime.now())))
        try:
            # This call should call handle(...) method in the inherited class, that was renamed to _handle by BaseCommandMeta
            self._handle(*args, **kwargs)
        except Exception as e:
            if COMMAND_HANDLE_EXCEPTIONS or self.HANDLE_EXCEPTIONS:
                print("Unexpected crash:")
                print(traceback.format_exc())
                if (COMMAND_EMAIL_EXCEPTIONS or self.EMAIL_EXCEPTIONS) and not settings.DEBUG:
                    mailer.send_mail("Command %s crash" % self.COMMAND_NAME, traceback.format_exc(), settings.DEFAULT_FROM_EMAIL, [email for name, email in settings.ADMINS ])
                    print("Emails were sent to admins of the website about this crash")
            else:
                raise e
        finally:
            if lock is not None:
                lock.release()

