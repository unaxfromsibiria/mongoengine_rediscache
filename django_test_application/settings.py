# -*- coding: utf-8 -*-

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (,)

MANAGERS = ADMINS

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME'  : 'testdb',
    'USER'  : 'admin',
    'PASSWORD': 'password',
    'HOST'  : 'localhost',
    'PORT'  : '5432',
    },
    'mongoengine' : {
    'NAME'  : 'testdb',
    'USER'  : 'admin',
    'PASSWORD': 'password',
    'HOST'  : 'localhost',
    'PORT'  : 27017,
    }
}

from mongoengine import connect

connect(DATABASES['mongoengine'].get('NAME'),
        username=DATABASES['mongoengine'].get('USER'),
        password=DATABASES['mongoengine'].get('PASSWORD'),
        host=DATABASES['mongoengine'].get('HOST'),
        port=DATABASES['mongoengine'].get('PORT') )

TIME_ZONE = 'Asia/Novosibirsk'
TIME_INPUT_FORMATS =('%H:%M',)
DATE_INPUT_FORMATS  =('%H:%M',)
LANGUAGE_CODE = 'ru'
SITE_ID = 1

USE_I18N = True
USE_L10N = True
USE_TZ = False
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (

)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'j_uptm-k^$wydy!&amp;7inbc4b8e*bmjmnfyl76m^uwn9z)l!vcsa'

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.filesystem.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS =(
                              "django.contrib.auth.context_processors.auth",
                              "django.core.context_processors.debug",
                              "django.core.context_processors.i18n",
                              "django.core.context_processors.media",
                              "django.core.context_processors.static",
                              "django.contrib.messages.context_processors.messages"
                              )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.gzip.GZipMiddleware',
)


ROOT_URLCONF = 'urls'



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'tests',
    'mongoengine_rediscache',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


CACHE_USE=True


MONGOENGINE_REDISCACHE = {
    'scheme' : {
                'tests.models.TestModelObj'  : { 'all' : 600 },
                'tests.models.TestModelList' : { 'all' : 600 },
                'tests.models.TestModelRef'  : { 'list' : 120, 'reference' : 600, 'get' : 120, 'list_reference' : 600 },
                },
    'redis' : {
        'host': 'localhost',
        'port': 6379,
        'db': 1, 
        'socket_timeout': 3,
    },
    'used' : True,
    'keyhashed' : False,
}
