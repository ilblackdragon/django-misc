django-misc
===========

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

Template tags
-------------

{% load html_tags %}
~~~~~~~~~~~~~~~~~~~~

::

    {% remove_tags <text> %}
Removes html tags and replace <br/> by \n

{% load misc_tags %}
~~~~~~~~~~~~~~~~~~~~

::

    {{ text|cutafter:"<length>" }}
Cut text after <length> characters and, if necessary, add tree dots (...) to the end

::

    {% get_range <length> %}
Return simple python range(<length>) list

::

    {% get_element <dict> <key1> [<key2>] %}
Return a dict value by key1 and, if specified, key2 (i.e. dict[key1][key2])

json_encode
-----------

JSONTemplateResponse
~~~~~~~~~~~~~~~~~~~~

It works like TemplateResponse, but return JSON response

in view.py::

    ...
    return JSONTemplateResponse(request, template_name, template_context, data={'status': 'ok', 'user': request.user})


This line will create response

::

    {
        "status": "ok",
        "user": {
            "username": "frol",
            "first_name": "",
            "last_name": "",
            "is_active": true,
            "email": "qq@qq.qq",
            "is_superuser": true,
            "is_staff": true,
            "last_login": "2012-01-24 18:59:55",
            "password": "sha1$fffff$1b4d68b3731ec29a797d61658c716e2400000000",
            "id": 1,
            "date_joined": "2011-07-09 05:57:21"
        },
        "html": "<rendered HTML>"
    }

WARNING: Be carefull with serialization of model objects. As you can see in example, password hash has been serialized.

json_encode
~~~~~~~~~~~

json_encode(data)

Serialize python object into JSON string.
    
The main issues with django's default json serializer is that properties that
had been added to an object dynamically are being ignored (and it also has 
problems with some models).

json_response
~~~~~~~~~~~~~

json_response(data)

Serialize python object into JSON string and return HttpResponse with correct content_type (application/json)

json_template
~~~~~~~~~~~~~

json_template(data, template_name, template_context)

Render template, add it for serialization data, serialize data into JSON string and return HttpResponse with correct content_type.

Context processors
------------------

useful_constants
~~~~~~~~~~~~~~~~

If you want use True, False, None in django templates, add line to TEMPLATE_CONTEXT_PROCESSORS in settings.py::
    'misc.context_processors.useful_constants',

Example, A = True, B = False, C = None, D - undefined::
    {% if A == True %}A is True{% endif %}
    {% if A == False %}A is False{% endif %}
    {% if A == None %}A is None{% endif %}
    {% if B == True %}B is True{% endif %}
    {% if B == False %}B is False{% endif %}
    {% if B == None %}B is None{% endif %}
    {% if C == True %}C is True{% endif %}
    {% if C == False %}C is False{% endif %}
    {% if C == None %}C is None{% endif %}
    {% if D == True %}D is True{% endif %}
    {% if D == False %}D is False{% endif %}
    {% if D == None %}D is None{% endif %}

Will produce output::
    A is True
    B is False
    C is None
    D is None


Views utils
-----------

Management utils
----------------

HTML utils
----------



Contributing
============

Development of django-misc happens at github: https://github.com/ilblackdragon/django-misc

License
============

Copyright (C) 2009-2011 Ilya Polosukhin & Vladyslav Frolov
This program is licensed under the MIT License (see LICENSE)
 
