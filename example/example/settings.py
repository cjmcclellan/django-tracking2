"""
Django settings for example project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import django

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6!9cxt&$5a3bz-*xf(l$r4(z24pxyytf0aksfb_kt^b$1kq^4g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

TRACK_PAGEVIEWS = True
GEOIP_PATH = os.path.join(BASE_DIR, 'geoip')

# TRACK_IGNORE_URLS = [r'^tracking/', r'^django_plotly_dash/']
TRACK_SELECTED_URLS = [r'^', r'^/']

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.contrib.auth.context_processors.auth',
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.i18n',
#                 'django.template.context_processors.media',
#                 'django.template.context_processors.static',
#                 'django.template.context_processors.tz',
#                 'django.contrib.messages.context_processors.messages',
#                 'congo'
#             ],
#         },
#     }
# ]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(os.path.join(BASE_DIR, 'templates'))],  # include the global templates directory
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

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'tracking',
    'congo',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_plotly_dash.middleware.BaseMiddleware',
    'django_plotly_dash.middleware.ExternalRedirectionMiddleware',

]

# if django.VERSION < (1, 10):
#     MIDDLEWARE_CLASSES = (
#         # make sure tracking middleware is before SessionMiddleware
#         'tracking.middleware.VisitorTrackingMiddleware',
#
#         'django.contrib.sessions.middleware.SessionMiddleware',
#         'django.middleware.common.CommonMiddleware',
#         'django.middleware.csrf.CsrfViewMiddleware',
#         'django.contrib.auth.middleware.AuthenticationMiddleware',
#         'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#         'django.contrib.messages.middleware.MessageMiddleware',
#         'django.middleware.clickjacking.XFrameOptionsMiddleware',
#         'django_plotly_dash.middleware.BaseMiddleware',
#
#     )
# else:
#     MIDDLEWARE = [
#         # make sure tracking middleware is before SessionMiddleware
#         'tracking.middleware.VisitorTrackingMiddleware',
#
#         'django.middleware.security.SecurityMiddleware',
#         'django.contrib.sessions.middleware.SessionMiddleware',
#         'django.middleware.common.CommonMiddleware',
#         'django.middleware.csrf.CsrfViewMiddleware',
#         'django.contrib.auth.middleware.AuthenticationMiddleware',
#         'django.contrib.messages.middleware.MessageMiddleware',
#         'django.middleware.clickjacking.XFrameOptionsMiddleware',
#         'django_plotly_dash.middleware.BaseMiddleware',
#     ]

ROOT_URLCONF = 'example.urls'

WSGI_APPLICATION = 'example.wsgi.application'

PLOTLY_DASH = {
    'cache_arguments': False
}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
