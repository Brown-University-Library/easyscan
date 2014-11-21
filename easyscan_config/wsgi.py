"""
WSGI config for easyscan_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "easyscan_config.settings")

# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()



""" Prepares application environment.
    Variables assume project setup like:
    easyscan_stuff
        easyscan_project
            easyscan_config
            easyscan_app
        env_ezscan
     """

import os, pprint, sys


## become self-aware, padawan
current_directory = os.path.dirname(os.path.abspath(__file__))

## vars
ACTIVATE_FILE = os.path.abspath( u'%s/../../env_ezscan/bin/activate_this.py' % current_directory )
PROJECT_DIR = os.path.abspath( u'%s/../../easyscan_project' % current_directory )
PROJECT_ENCLOSING_DIR = os.path.abspath( u'%s/../..' % current_directory )
SETTINGS_MODULE = u'easyscan_config.settings'
SITE_PACKAGES_DIR = os.path.abspath( u'%s/../../env_ezscan/lib/python2.6/site-packages' % current_directory )

## virtualenv
execfile( ACTIVATE_FILE, dict(__file__=ACTIVATE_FILE) )

## sys.path additions
for entry in [PROJECT_DIR, PROJECT_ENCLOSING_DIR, SITE_PACKAGES_DIR]:
 if entry not in sys.path:
   sys.path.append( entry )

## environment additions
os.environ[u'DJANGO_SETTINGS_MODULE'] = SETTINGS_MODULE  # so django can access its settings

## gogogo
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()