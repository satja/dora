"""Template za lokalne postavke, koje moraju biti skrivene."""

import os

ADMINS = (
    #  ('Pajo Patak', 'pajopatak@gmail.com'),
)
MANAGERS = ADMINS

ALLOWED_HOSTS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'NEDOSTAJE',
        'USER': 'NEDOSTAJE',
        'PASSWORD': 'NEDOSTAJE',
        'HOST': '',
        'PORT': '',
    }
}

# Use this for development:
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PROJECT_ROOT, "local", "email")

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'testing@example.com'

MEDIA_ROOT = ''
