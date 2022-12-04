from .base import *

DATABASES = {
    'default': {
        'ENGINE': os.environ.get("PRODUCTION_DATABASE_ENGINE"),
        'NAME': os.environ.get("PRODUCTION_DATABASE_NAME"),
    }
}

DEBUG = False

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL=True 