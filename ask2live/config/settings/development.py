from .base import *
import os
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# SECRET_KEY = os.environ.get("SECRET_KEY")
DATABASES = {
  
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'qna_prod',
        'USER': 'qna_proj',
        'PASSWORD': 'ask2live',
        'HOST': '3.36.64.63',
        'PORT': '3306',
    }
}

ALLOWED_HOSTS=['3.36.88.31','143.248.198.125','127.0.0.1', 'localhost', '143.248.226.51','143.248.232.143','143.248.220.177','211.36.145.245','175.223.10.151','223.39.161.127','223.62.213.118', '143.248.232.111','175.223.22.116','223.39.131.25','143.248.232.156', 'www.ask2live.me','ask2live.me']
