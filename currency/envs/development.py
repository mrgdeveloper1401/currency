from currency.settings import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DEV_SECRET_KEY', cast=str)

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
