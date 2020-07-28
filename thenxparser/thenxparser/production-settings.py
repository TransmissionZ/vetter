from .settings import *
import os


DEBUG=False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TransmissionZ$thenx', #os.path.join(BASE_DIR, 'thenxappMariaDB'),
        'USER': 'TransmissionZ',
        'PASSWORD': 'thenx011',
        'HOST': 'TransmissionZ.mysql.pythonanywhere-services.com',
        'PORT': '',
    }
}

STATIC_ROOT = '/home/TransmissionZ/vetter/thenxparser/static/'