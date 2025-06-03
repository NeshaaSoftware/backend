from .base import *

DEBUG = True
ALLOWED_HOSTS = ['neshaa.ir', 'localhost']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'dev_db'),
        'USER': os.getenv('DB_USER', 'dev_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'dev_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}