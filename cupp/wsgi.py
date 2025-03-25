#!/usr/bin/env python3
"""
WSGI config for xbook project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cupp.settings")
sys.path.insert(0, '/home/cuadmin/.local/lib/python3.6/site-packages')

application = get_wsgi_application()
