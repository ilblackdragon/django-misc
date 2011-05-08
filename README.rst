django-misc
##############

**Django misc** is module with set of utilities, decorators, templatetags that everybody uses at least once in project.
So here they all in one application, that will grow to aggregate all usefull utilities for Django.

.. contents::

Quick overview
==============

Here you'll find:

* Couple decorators, like render_to and receive
* Json_encode module for simplify work with json
* Some usefull templatetags, like set, filter, get etc
* Some additional utilities
* Bbcode template tags
* Template tags that provide like and share for social sevices



Requirements
==============

- python >= 2.5
- pip >= 0.8
- django >= 1.2

Optional (for html clearing and bbcodes):

- BeautifulSoup 
- git+git://github.com/frol/postmarkup.git

Installation
=============

**Django misc** should be installed using pip: ::

    pip install git+git://github.com/ilblackdragon/django-misc.git


Setup
============

- Add 'misc' to INSTALLED_APPS ::

    INSTALLED_APPS += ( 'misc', )
  
- If you want to use the html clearer ::
    
    pip install BeautifulSoup
    
- If you want to use bbcodes ::
    
    pip install git+git://github.com/frol/postmarkup.git
    
    
Use django-misc
===============

How to use some specific functional will be added later

Contributing
============

Development of django-misc happens at github: https://github.com/ilblackdragon/django-misc

License
============

Copyright (C) 2009-2011 Ilya Polosukhin & Vladyslav Frolov
This program is licensed under the MIT License (see LICENSE) 
                          
