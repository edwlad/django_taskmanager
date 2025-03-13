# -*- coding: utf-8 -*-
import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")

application = get_wsgi_application()
