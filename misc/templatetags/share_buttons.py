# -*- coding: utf-8 -*-

import urllib
import hashlib

from django.template import Library
from django.utils.translation import get_language_from_request, ugettext
from django.contrib.sites.models import Site
from django.conf import settings

register = Library()

def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port     = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, settings.SITE_DOMAIN)
    if port:
        url += ':%s' % port
    return url

@register.simple_tag
def tweet_it(url, title):
    return """
        <div class="twitter">
            <a href="http://twitter.com/home/?%s" title="%s" target="_blank"></a>
        </div>    
    """ % (urllib.urlencode({'status': title + (u" " + url + u" #escalibro").encode('utf-8')}), ugettext("Tweet it"))    

@register.simple_tag
def tweet_like(url, title):
    return """
        <iframe allowtransparency="true" frameborder="0" scrolling="no" tabindex="0" class="twitter-share-button twitter-count-horizontal" 
                src="http://platform0.twitter.com/widgets/tweet_button.html?_=1302382076454&amp;count=horizontal&amp;lang=en&amp;via=escalibro&amp;%s" 
                style="width: 110px; height: 20px; " title="Twitter For Websites: Tweet Button"></iframe>
        <script type="text/javascript" src="http://platform.twitter.com/widgets.js"></script>
    """ % ('text=' + title + ' %23escalibro&amp;' + urllib.urlencode({'url': url}))
    
@register.simple_tag
def facebook_it(url, title):
    return """
        <div class="facebook">
            <a onclick="window.open(this.href, '%s', 'width=800,height=300'); return false" href="http://www.facebook.com/sharer.php?%s" title="%s" target="_blank"></a>
        </div>
    """ % (ugettext("Share link on FaceBook"), urllib.urlencode({'u': url, 't': title}), ugettext("To FaceBook"))

@register.simple_tag
def facebook_like(url, title):
    return """
        <iframe src="http://www.facebook.com/plugins/like.php?href%s&amp;layout=button_count&amp;show_faces=true&amp;width=85&amp;action=like&amp;colorscheme=light&amp;height=21" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:85px; height:21px;" allowtransparency="true"></iframe>
    """ % (urllib.urlencode({'': url}))
    
@register.simple_tag
def vk_it(url, title):
    return """
        <div class="vk">
            <a onclick="window.open(this.href, '%s', 'width=800,height=300'); return false" href="http://vkontakte.ru/share.php?%s" title="%s"></a>
        </div>
    """ % (ugettext("Share link on VKontakte"), urllib.urlencode({'url': url, 'title': title}), ugettext("To VKontakte"))

@register.simple_tag
def vk_like(url, title):
    block_id = (hashlib.md5(url + title)).hexdigest()
    return """
        <div id="vk_like_%s"></div>
        <script type="text/javascript">
            VK.Widgets.Like("vk_like_%s", {type: "button", pageUrl: "%s", pageTitle: "%s", height: "20px"});
        </script>
    """ % (block_id, block_id, url, settings.SITE_NAME + " - " + title)

@register.simple_tag
def vk_js():
    return """
        <script type="text/javascript">
            VK.init({apiId: "%s", onlyWidgets: true});
        </script>
    """ % settings.VKONTAKTE_APPLICATION_ID

@register.simple_tag
def gplus_it(url, title):
    return """
        <div class="gplus">
            <g:plusone size="small" annotation="none"></g:plusone>
        </div>
    """

@register.simple_tag
def gplus_js():
    return """
        <script type="text/javascript">
          window.___gcfg = {lang: 'ru'};
          (function() {
            var po = document.createElement('script'); po.type = 'text/javascript'; po.async = true;
            po.src = 'https://apis.google.com/js/plusone.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(po, s);
          })();
        </script>
    """

@register.simple_tag
def gplus_like(url, title):
    return """
        <div class="gplus_like">
            <g:plusone size="small"></g:plusone>
        </div>
    """

share_functions = [tweet_it, vk_it, facebook_it, gplus_it] # Ordering
like_functions = [tweet_like, vk_like, facebook_like, gplus_like]
js_functions = [gplus_js]

def group_buttons(url, title, funcs, block_class):
    url = current_site_url() + url
    url = url.encode('utf-8')
    title = title.encode('utf-8')
    res = "<div class=\"%s\">" % block_class
    for f in funcs:
        res += f(url, title)
    res += "</div>"
    return res
    
@register.simple_tag
def share_it(url, title):
    return group_buttons(url, title, share_functions, "share_buttons")

@register.simple_tag
def like_it(url, title):
    return group_buttons(url, title, like_functions, "like_buttons")
   
@register.simple_tag
def share_js():
    return ' '.join([f() for f in js_functions])

