from .base import *
import os
import dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)

DEBUG = True

ALLOWED_HOSTS=['www.ask2live.me', 'ask2live.me']

STATIC_ROOT = BASE_DIR / 'static/'
STATICFILES_DIRS = []
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
# SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'qna_prod',
        'USER': os.environ.get("DB_USER"),
        'PASSWORD': os.environ.get("DB_PW"),
        'HOST': os.environ.get("DB_HOST"),
        'PORT': '3306',
    }
}