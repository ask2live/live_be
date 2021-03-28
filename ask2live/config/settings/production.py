from .base import *
import os
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
        'OPTIONS': {
            'read_default_file': '/etc/mysql/my.cnf',
            # 'read_default_file': '/ProgramData/MySQL/MySQL Server 8.0/my.ini',
            # 'read_default_file': '/usr/local/etc/my.cnf',
        },
    }
}