"""
WSGI config for thenxparser project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

from dj_static import Cling

# add project folder to path
path = '/home/mharoons/thenx/repositories/vetter/thenxparser/'
if path not in sys.path:
    sys.path.insert(0, path)

path = '/home/mharoons/thenx'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thenxparser.settings')

application = Cling(get_wsgi_application())
