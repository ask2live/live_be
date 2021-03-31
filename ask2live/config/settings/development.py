from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

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

ALLOWED_HOSTS=['3.36.88.31','143.248.198.125','127.0.0.1', 'localhost', '143.248.226.51','143.248.232.143','143.248.220.177','211.36.145.245','175.223.10.151','223.39.161.127','223.62.213.118', '143.248.232.111','175.223.22.116','223.39.131.25','143.248.232.156', 'www.ask2live.me','ask2live.me']
