"""
Django settings for easyscan_project project.

Environmental variables set in project's env/bin/activate, when using runserver,
  or env/bin/activate_this.py, when using apache via mod_wsgi or passenger.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import json, os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['EZSCAN__SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
# temp_DEBUG = os.environ['EZSCAN__DEBUG']
# assert temp_DEBUG in [ 'True', '' ], Exception( 'DEBUG env setting is, "%s"; must be either "True" or ""' % temp_DEBUG )
# DEBUG = bool( temp_DEBUG )

DEBUG = json.loads( os.environ['EZSCAN__DEBUG'] )

ALLOWED_HOSTS = json.loads( os.environ['EZSCAN__ALLOWED_HOSTS'] )  # list


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'easyscan_app',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'easyscan_config.urls'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': os.environ['EZSCAN__DATABASES_ENGINE'],
#         'NAME': os.environ['EZSCAN__DATABASES_NAME'],
#         'USER': os.environ['EZSCAN__DATABASES_USER'],
#         'PASSWORD': os.environ['EZSCAN__DATABASES_PASSWORD'],
#         'HOST': os.environ['EZSCAN__DATABASES_HOST'],
#         'PORT': os.environ['EZSCAN__DATABASES_PORT'],
#     }
# }

## the environ.get() sytax allows env_var settings to point to either mysql or sqlite
DATABASES = {
    'default': {
        'ENGINE': os.environ['EZSCAN__DATABASES_ENGINE'],
        'NAME': os.environ['EZSCAN__DATABASES_NAME'],
        'USER': os.environ.get('EZSCAN__DATABASES_USER'),
        'PASSWORD': os.environ.get('EZSCAN__DATABASES_PASSWORD'),
        'HOST': os.environ.get('EZSCAN__DATABASES_HOST'),
        'PORT': os.environ.get('EZSCAN__DATABASES_PORT'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = os.environ['EZSCAN__STATIC_URL']
STATIC_ROOT = os.environ['EZSCAN__STATIC_ROOT']  # needed for collectstatic command


# Templates

# TEMPLATE_DIRS = json.loads( os.environ['EZSCAN__TEMPLATE_DIRS'] )  # list

template_dirs = json.loads( os.environ['EZSCAN__TEMPLATE_DIRS'] )
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': template_dirs,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Email
EMAIL_HOST = os.environ['EZSCAN__EMAIL_HOST']
EMAIL_PORT = int( os.environ['EZSCAN__EMAIL_PORT'] )


# sessions

# <https://docs.djangoproject.com/en/1.6/ref/settings/#std:setting-SESSION_SAVE_EVERY_REQUEST>
# Thinking: not that many concurrent users, and no pages where session info isn't required, so overhead is reasonable.
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
        'format': "[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level':'DEBUG',
            'class':'logging.FileHandler',  # note: configure server to use system's log-rotate to avoid permissions issues
            'filename': os.environ.get(u'EZSCAN__LOG_PATH'),
            'formatter': 'standard',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'easyscan_app': {
            'handlers': ['logfile'],
            'level': os.environ.get(u'EZSCAN__LOG_LEVEL'),
        },
    }
}
