from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import signals
from django.utils.translation import ugettext_noop as _


def sync_site(app, created_models, verbosity, **kwargs):
    try:
        site = Site.objects.get_current()
        site.name = settings.SITE_NAME
        site.domain = settings.SITE_DOMAIN
        site.save()
    except Site.DoesNotExist: # In case if Site table doesn't created yet
        pass

signals.post_syncdb.connect(sync_site)
