..   -*- mode: rst -*-

django-misc
===========

**Django misc** is module with set of utilities, decorators, templatetags that everybody uses at least once in project.
So here they all in one application, that will grow to aggregate all usefull utilities for Django.

.. image:: https://secure.travis-ci.org/ilblackdragon/django-misc.png?branch=master
   :target: http://travis-ci.org/ilblackdragon/django-misc

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
- django >= 1.2 < 1.5 (Latest tested is 1.4.3)

Optional:

- bbcodes: git+git://github.com/frol/postmarkup.git
- Coffin, Jinja2

Installation
=============

**Django misc** should be installed using pip: ::

    pip install git+git://github.com/ilblackdragon/django-misc.git
    
or for stable version: ::

    pip install django-misc


Setup
============

- Add 'misc' to INSTALLED_APPS ::

    INSTALLED_APPS += ( 'misc', )
  
- If you want to use bbcodes ::
    
    pip install git+git://github.com/frol/postmarkup.git
    
    
Use django-misc
===============

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

in view.py: ::

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

``json_encode(data)``

Serialize python object into JSON string.
    
The main issues with django's default json serializer is that properties that
had been added to an object dynamically are being ignored (and it also has 
problems with some models).

json_response
~~~~~~~~~~~~~

``json_response(data)``

Serialize python object into JSON string and return HttpResponse with correct content_type (application/json)

json_template
~~~~~~~~~~~~~

``json_template(data, template_name, template_context)``

Render template, add it for serialization data, serialize data into JSON string and return HttpResponse with correct content_type.

Context processors
------------------

useful_constants
~~~~~~~~~~~~~~~~

If you want use True, False, None in django templates, add line to TEMPLATE_CONTEXT_PROCESSORS in settings.py: ::

    'misc.context_processors.useful_constants',

Example, A = True, B = False, C = None, D - undefined: ::

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

Will produce output: ::

    A is True
    B is False
    C is None
    D is None


Views utils
-----------

server_error
~~~~~~~~~~~~

``misc.views.server_error(request)``

Put server_error as your handler500 in urls.py and add templates/errors/500.html: ::

    handler500 = 'misc.views.server_error'

decorator to_template or render_to
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``to_template(template_name=None)``

Decorator to simply call direct_to_template: ::
    
    @to_template("test.html")
    def test(request):
        return {'test': 100}

    @to_template
    def test2(request):
        return {'test': 100, 'TEMPLATE': 'test.html'}

    @to_template
    def test2(request, template_name='test.html'):
        return {'test': 100, 'TEMPLATE': template_name}

HttpResponseReload
~~~~~~~~~~~~~~~~~~

``utils.HttpResponseReload(request)``

Reloads current page: ::

    def simple_view(request, form_class=CommentForm, template_name='some_template.html'):
        form = CommentForm(request.POST or None)
        if form.valid():
            form.save()
            return HttpResponseReload(request)
        return render(template_name, {'form': form})

str_to_class
~~~~~~~~~~~~

``utils.str_to_class(class_name)``

Returns a class based on class name

get_alphabets
~~~~~~~~~~~~~

``utils.get_alphabets()``

Returns pair of english and russian alphabets.
Useful for creating filters.
        
Management utils
----------------

BaseCommand
~~~~~~~~~~~

``management.commands.BaseCommand``

Use this class instead of ``django.core.management.base.BaseCommand``.
It will decorate ``handle(self, args, options)`` method of your command by next functionality:

- Logging, that redirects stdout to a log file
- Lock to allow only one command at a time
- Exception handling with email notification about crash of the command (very important for cron jobs, from my excperience)

Set of options are available for configuration in settings.py:

- LOCK_ROOT - configure root directory for lock files
- COMMAND_LOCK_ROOT - configure root directory for lock files only for commands (optional, if LOCK_ROOT must be used for something else)
- LOG_ROOT - configure root directory for log files 
- COMMAND_LOG_ROOT - configure root directory for log files only for commands (optional, if LOG_ROOT must be used for something else)
- COMMAND_USE_LOCK - configure if locks should be used (default True)
- COMMAND_HANDLE_EXCEPTIONS - configure if exceptions should be handled (default True)
- COMMAND_EMAIL_EXCEPTIONS - report about exceptions in command via email to administrators (default True, works only when not DEBUG)

Additional configurations can be used for each particular command (defined as class properties):

- USE_LOCK - use locks for this commands (default True)
- HANDLE_EXCEPTIONS - handle exceptions for this command  (default True)
- EMAIL_EXCEPTIONS - email if exception occured in this command (default True)
- OUTPUT_LOG - redirect output to log file (default True)

handle_lock
~~~~~~~~~~~

``management.handle_lock(handle)``

Decorate the handle method with a file lock to ensure there is only ever one process running at any one time.

sync_site
~~~~~~~~~

sync_site is post syncdb event, that will sync current Site object with settings like SITE_NAME and SITE_DOMAIN

create_app
~~~~~~~~~~

Create application in the current project in the ``apps/`` subfolder.

HTML utils
----------

Moved to separate project https://github.com/ProstoKSI/html-cleaner

Contributing
============

Development of django-misc happens at github: https://github.com/ilblackdragon/django-misc

License
============

Copyright (C) 2009-2013 Illia Polosukhin, Vladyslav Frolov.
This program is licensed under the MIT License (see LICENSE)

