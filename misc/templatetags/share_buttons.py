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
        <span class="twitter">
            <a href="http://twitter.com/home/?%s" title="%s" target="_blank"></a>
        </span>    
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
def buzz_it(url, title):
    return """
        <span class="buzz">
            <a onclick="window.open(this.href, '%s', 'width=800,height=300'); return false" href="http://www.google.com/buzz/post?%s" title="%s" target="_blank"></a>
        </span>    
    """ % (ugettext("Post link on Buzz"), urllib.urlencode({'url': url, 'message': title}), ugettext("Buzz it"))
    
@register.simple_tag
def facebook_it(url, title):
    return """
        <span class="facebook">
            <a onclick="window.open(this.href, '%s', 'width=800,height=300'); return false" href="http://www.facebook.com/sharer.php?%s" title="%s" target="_blank"></a>
        </span>
    """ % (ugettext("Share link on FaceBook"), urllib.urlencode({'u': url, 't': title}), ugettext("To FaceBook"))

@register.simple_tag
def facebook_like(url, title):
    return """
        <iframe src="http://www.facebook.com/plugins/like.php?href%s&amp;layout=button_count&amp;show_faces=true&amp;width=85&amp;action=like&amp;colorscheme=light&amp;height=21" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:85px; height:21px;" allowtransparency="true"></iframe>
    """ % (urllib.urlencode({'': url}))
    
@register.simple_tag
def vk_it(url, title):
    return """
        <span class="vk">
            <a onclick="window.open(this.href, '%s', 'width=800,height=300'); return false" href="http://vkontakte.ru/share.php?%s" title="%s"></a>
        </span>
    """ % (ugettext("Share link on VKontakte"), urllib.urlencode({'url': url, 'title': title}), ugettext("To VKontakte"))

@register.simple_tag
def vk_like(url, title):
    block_id = (hashlib.md5(url + title)).hexdigest()
    return """
        <span id="vk_like_%s"></span>
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
       
share_functions = [tweet_it, buzz_it, vk_it, facebook_it] # Ordering
like_functions = [tweet_like, vk_like, facebook_like]

def group_buttons(url, title, funcs, block_class):
    url = current_site_url() + url
    title = title.encode('utf-8')
    res = "<span class=\"%s\">" % block_class
    for f in funcs:
        res += f(url, title)
    res += "</span>"
    return res
    
@register.simple_tag
def share_it(url, title):
    return group_buttons(url, title, share_functions, "share_buttons")

@register.simple_tag
def like_it(url, title):
    return group_buttons(url, title, like_functions, "like_buttons")
    
