# import sys
# import django
#
# from django.conf import settings
# from django.core.management import call_command
#
# settings.configure(DEBUG=True,
#     INSTALLED_APPS=(
#         "django.contrib.auth",
#         "django.contrib.admin",
#         'django.contrib.contenttypes',
#         'tracking',
#     ),
# )
#
# django.setup()
# call_command('makemigrations', 'tracking')

# import sys
# import django
# import os
# from django.conf import settings
#
# INSTALLED_APPS = [
#     "django.contrib.auth",
#     "django.contrib.admin",
#     "django.contrib.contenttypes",
#     'django.contrib.messages',
#     # "django.contrib.sites",
#     "tracking",
# ]
#
# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
# ]
#
# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         # 'DIRS': [(os.path.join(BASE_DIR, 'templates'))],  # include the global templates directory
#         # 'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.debug',
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]
#
# settings.configure(
#     DEBUG=True,
#     USE_TZ=True,
#     USE_I18N=True,
#     DATABASES={
#         "default": {
#             "ENGINE": "django.db.backends.sqlite3",
#         }
#     },
#     MIDDLEWARE=MIDDLEWARE,
#     TEMPLATES=TEMPLATES,
#     SITE_ID=1,
#     INSTALLED_APPS=INSTALLED_APPS,
#     # ROOT_URLCONF="tests.urls",
# )
#
# django.setup()
#
# if __name__ == '__main__':
#     from django.core.management import execute_from_command_line
#     execute_from_command_line(sys.argv)

import sys
import django
from django.conf import settings

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "tracking",
]

settings.configure(
    DEBUG=True,
    USE_TZ=True,
    USE_I18N=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
        }
    },
    MIDDLEWARE_CLASSES=(),
    SITE_ID=1,
    INSTALLED_APPS=INSTALLED_APPS,
    ROOT_URLCONF="tests.urls",
)

django.setup()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
