"""
A decorator for management commands (or any class method) to ensure that there is
only ever one process running the method at any one time.

Requires lockfile - (pip install lockfile)

Author: Ross Lawley
"""

import logging
import os
import time

from lockfile import FileLock, AlreadyLocked, LockTimeout
from django.conf import settings

# Lock timeout value - how long to wait for the lock to become available.
# Default behavior is to never wait for the lock to be available (fail fast)
LOCK_WAIT_TIMEOUT = getattr(settings, 'DEFAULT_LOCK_WAIT_TIMEOUT', -1)
LOCK_ROOT = getattr(settings, 'LOCK_ROOT', '')

def handle_lock(handle):
    """
    Decorate the handle method with a file lock to ensure there is only ever
    one process running at any one time.
    """
    
    def wrapper(self, *args, **options):
        start_time = time.time()
        try:
            verbosity = int(options.get('verbosity', 0))
        except ValueError:
            verbosity = 0
        logger = logging.getLogger(self.__module__)
        if verbosity == 0:
            logger.level = logging.WARNING
        elif verbosity == 1:
            logger.level = logging.INFO
        else:
            logger.level = logging.DEBUG
       
        logger.debug("-" * 72)
        
        lock_name = self.__module__.split('.').pop()
        lock = FileLock(os.path.join(LOCK_ROOT, lock_name))
        
        logger.debug("%s - acquiring lock..." % lock_name)
        try:
            lock.acquire(LOCK_WAIT_TIMEOUT)
        except AlreadyLocked:
            logger.debug("lock already in place. quitting.")
            return
        except LockTimeout:
            logger.debug("waiting for the lock timed out. quitting.")
            return
        logger.debug("acquired.")
        
        try:
            handle(self, logger, *args, **options)
        except:
            import traceback
            logging.warn("Command Failed")
            logging.warn('=' * 72)
            logging.warn(traceback.format_exc())
            logging.warn('=' * 72)
        
        logger.debug("releasing lock...")
        lock.release()
        logger.debug("released.")
        
        logger.info("done in %.2f seconds" % (time.time() - start_time))
        return
        
    return wrapper
